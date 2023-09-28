import asyncio
import base64
import datetime
import os
import socket
import struct
import time
import hashlib
import typing
from asyncio import transports
from typing import Any

from pytoniq_core import Slice
from pytoniq_core.tl.generator import TlGenerator, TlSchema

from pytoniq_core.crypto.ciphers import Server, Client, AdnlChannel, get_random, create_aes_ctr_cipher, aes_ctr_encrypt, aes_ctr_decrypt, get_shared_key, create_aes_ctr_sipher_from_key_n_data
from pytoniq_core.crypto.signature import verify_sign

from build.lib.pytoniq.tlb import MessageAny
from .udp_client import AdnlNode, SocketProtocol, AdnlUdpClientError


class OverlayError(AdnlUdpClientError):
    pass


class OverlayClient(AdnlNode):

    def __init__(self,
                 host: str,
                 port: int,
                 server_pub_key: str,  # server ed25519 public key in base64,
                 timeout: int = 3,
                 tl_schemas_path: typing.Optional[str] = None,
                 overlay_id: typing.Union[bytes, str] = '12b8a83f098e15ea47fe76d0b0df0986ff6dda1980796b084b0d2a68b2558649'  # by default basechain overlay id
                 ) -> None:

        super().__init__(host, port, server_pub_key, timeout, tl_schemas_path)

        if isinstance(overlay_id, bytes):
            overlay_id = overlay_id.hex()

        self.overlay_id = overlay_id

    def create_overload_query_message(self, tl_schema_name: str, data: dict):
        pass

    async def send_custom_message(self, message: bytes) -> dict:
        pass

    def get_signed_myself(self):
        ts = int(time.time())

        overlay_node_data = {'id': {'@type': 'pub.ed25519', 'key': self.client.ed25519_public.encode().hex()},
                             'overlay': self.overlay_id, 'version': ts, 'signature': b''}

        overlay_node_to_sign = self.schemas.serialize(self.schemas.get_by_name('overlay.node.toSign'),
                                                      {'id': {'id': self.client.get_key_id().hex()},
                                                       'overlay': self.overlay_id,
                                                       'version': overlay_node_data['version']})
        signature = self.client.sign(overlay_node_to_sign)

        overlay_node = overlay_node_data | {'signature': signature}
        return overlay_node

    async def send_query_message(self, tl_schema_name: str, data: dict) -> dict:

        message = {
            '@type': 'adnl.message.query',
            'query_id': get_random(32),
            'query': self.schemas.serialize(self.schemas.get_by_name('overlay.query'), data={'overlay': self.overlay_id})
                     + self.schemas.serialize(self.schemas.get_by_name(tl_schema_name), data)
        }
        data = {
            'message': message,
        }

        result = await self.send_message_in_channel(data)
        return result

    async def connect(self) -> dict:
        """
        Connects to the peer, creates channel and asks for a signed list in channel.
        :return: response dict for overlay.getRandomPeers
        """
        self.loop = asyncio.get_running_loop()
        self.transport, self.protocol = await self.loop.create_datagram_endpoint(
            lambda: SocketProtocol(timeout=self.timeout), remote_addr=(self.host, self.port))

        ts = int(time.time())
        channel_client = Client(Client.generate_ed25519_private_key())
        create_channel_message = self.schemas.serialize(schema=self.create_channel_sch,
                                                        data={'key': channel_client.ed25519_public.encode().hex(),
                                                              'date': ts})

        # master fc061ba11e1d7ba92dc6eb25ba79174a5ea4b11ea6299f9cd80df4214f1ddb3b
        # base 12b8a83f098e15ea47fe76d0b0df0986ff6dda1980796b084b0d2a68b2558649

        get_random_peers_messsage = self.schemas.serialize(
            self.adnl_query_sch,
            data={
                'query_id': get_random(32),
                'query': self.schemas.serialize(self.schemas.get_by_name('overlay.query'), data={
                    'overlay': '12b8a83f098e15ea47fe76d0b0df0986ff6dda1980796b084b0d2a68b2558649'}) + self.schemas.serialize(
                    self.schemas.get_by_name('overlay.getRandomPeers'), {'peers': {'nodes': []}})
            }
        )

        from_ = self.schemas.serialize(self.schemas.get_by_name('pub.ed25519'),
                                       data={'key': self.client.ed25519_public.encode().hex()})
        data = {
            'from': from_,
            'messages': [create_channel_message, get_random_peers_messsage],
            'address': {
                'addrs': [],
                'version': ts,
                'reinit_date': ts,
                'priority': 0,
                'expire_at': 0,
            },
            'recv_addr_list_version': ts,
            'reinit_date': ts,
            'dst_reinit_date': 0,
        }

        data = await self.send_message_outside_channel(data)
        messages = data['messages']

        confirm_channel = messages[0]
        assert confirm_channel.get(
            '@type') == 'adnl.message.confirmChannel', f'expected adnl.message.confirmChannel, got {confirm_channel.get("@type")}'
        assert confirm_channel['peer_key'] == channel_client.ed25519_public.encode().hex()

        channel_server = Server(self.host, self.port, bytes.fromhex(confirm_channel['key']))

        channel = AdnlChannel(channel_client, channel_server, self.local_id, self.peer_id)

        self.channels.append(channel)

        # test channel:

        data = {
            'message': get_random_peers_messsage,
        }

        result = await self.send_message_in_channel(data)
        return result['message']['answer']

    async def get_random_peers(self):
        overlay_node = self.get_signed_myself()

        peers = [
            overlay_node
        ]
        return await self.send_query_message(tl_schema_name='overlay.getRandomPeers', data={'peers': {'nodes': peers}})

    async def get_capabilities(self):

        return await self.send_query_message(tl_schema_name='tonNode.getCapabilities', data={})


class OverlayServer(OverlayClient):

    def __init__(self,
                 # peers: typing.List[OverlayClient],
                 host: str,
                 port: int,
                 server_pub_key: str,  # server ed25519 public key in base64,
                 timeout: int = 3,
                 tl_schemas_path: typing.Optional[str] = None,
                 overlay_id: typing.Union[bytes, str] = '12b8a83f098e15ea47fe76d0b0df0986ff6dda1980796b084b0d2a68b2558649'  # by default basechain overlay id
                 ) -> None:

        super().__init__(host, port, server_pub_key, timeout, tl_schemas_path)

        if isinstance(overlay_id, bytes):
            overlay_id = overlay_id.hex()

        self.overlay_id = overlay_id
        self.listener = None
        self.tasks: typing.Dict[str, asyncio.Future] = {}

    def process_outcoming_message(self, message: dict) -> typing.Optional[asyncio.Future]:
        future = self.loop.create_future()
        type_ = message['@type']
        # print(type_)
        if type_ == 'adnl.message.query':
            self.tasks[message.get('query_id')[::-1].hex()] = future
        elif type_ == 'adnl.message.createChannel':
            self.tasks[message.get('key')] = future
        else:
            print(type_)
            return None
        return future

    def create_futures(self, data: dict) -> typing.List[asyncio.Future]:
        futures = []
        if data.get('message'):
            future = self.process_outcoming_message(data['message'])
            if future is not None:
                futures.append(future)

        if data.get('messages'):
            for message in data['messages']:
                future = self.process_outcoming_message(message)
                if future is not None:
                    futures.append(future)
        return futures

    async def receive(self, futures: typing.List[asyncio.Future]) -> list:
        return list(await asyncio.gather(*futures))

    async def send_message_in_channel(self, data: dict, channel: typing.Optional[AdnlChannel] = None) -> typing.Union[dict, list]:
        if channel is None:
            if not self.channels:
                raise OverlayError('no channels created!')
            channel = self.channels[0]

        data = self.prepare_packet_content_msg(data)
        sending_seqno = data.get('seqno')

        futures = self.create_futures(data)

        if self.seqno == sending_seqno:
            self.seqno += 1
        else:
            raise Exception(f'sending seqno {sending_seqno}, client seqno: {self.seqno}')
        serialized = self.schemas.serialize(self.adnl_packet_content_sch, data)
        res = channel.encrypt(serialized)

        self.transport.sendto(res, None)
        result = await asyncio.wait_for(self.receive(futures), self.timeout)
        if len(result) == 1:
            return result[0]
        else:
            return result

    async def send_message_outside_channel(self, data: dict) -> typing.Union[dict, list]:
        """
        Serializes, signs and encrypts sending message.
        :param data: data for `adnl.packetContents` TL Scheme
        :return: decrypted and deserialized response
        """
        data = self.prepare_packet_content_msg(data)
        sending_seqno = data.get('seqno')

        data = self.compute_flags_for_packet(data)

        futures = self.create_futures(data)

        serialized1 = self.schemas.serialize(self.adnl_packet_content_sch, self.compute_flags_for_packet(data))
        signature = self.client.sign(serialized1)
        serialized2 = self.schemas.serialize(self.adnl_packet_content_sch,
                                             self.compute_flags_for_packet(data | {'signature': signature}))

        checksum = hashlib.sha256(serialized2).digest()
        shared_key = get_shared_key(self.client.x25519_private.encode(), self.server.x25519_public.encode())
        init_cipher = create_aes_ctr_sipher_from_key_n_data(shared_key, checksum)
        data = aes_ctr_encrypt(init_cipher, serialized2)

        res = self.peer_id + self.client.ed25519_public.encode() + checksum + data
        self.transport.sendto(res, None)

        if self.seqno == sending_seqno:
            self.seqno += 1
        else:
            raise Exception(f'sending seqno {sending_seqno}, client seqno: {self.seqno}')

        result = await asyncio.wait_for(self.receive(futures), self.timeout)
        if len(result) == 1:
            return result[0]
        else:
            return result

    async def start_server(self, port=13678) -> dict:
        """
        Connects to the peer, creates channel and asks for a signed list in channel.
        :return: response dict for overlay.getRandomPeers
        """
        self.loop = asyncio.get_running_loop()
        self.transport, self.protocol = await self.loop.create_datagram_endpoint(
            lambda: SocketProtocol(timeout=self.timeout), remote_addr=(self.host, self.port),
            local_addr=('0.0.0.0', port))

        ts = int(time.time())
        channel_client = Client(Client.generate_ed25519_private_key())
        create_channel_message = {
            '@type': 'adnl.message.createChannel',
            'key': channel_client.ed25519_public.encode().hex(),
            'date': ts
        }

        # master fc061ba11e1d7ba92dc6eb25ba79174a5ea4b11ea6299f9cd80df4214f1ddb3b
        # base 12b8a83f098e15ea47fe76d0b0df0986ff6dda1980796b084b0d2a68b2558649

        overlay_node_data = {'id': {'@type': 'pub.ed25519', 'key': self.client.ed25519_public.encode().hex()},
                             'overlay': self.overlay_id, 'version': ts, 'signature': b''}

        overlay_node_to_sign = self.schemas.serialize(self.schemas.get_by_name('overlay.node.toSign'),
                                                      {'id': {'id': self.client.get_key_id().hex()}, 'overlay': self.overlay_id, 'version': overlay_node_data['version']})
        signature = self.client.sign(overlay_node_to_sign)

        overlay_node = overlay_node_data | {'signature': signature}

        peers = [
            overlay_node
        ]

        get_random_peers_messsage = {
            '@type': 'adnl.message.query',
            'query_id': get_random(32),
            'query': self.schemas.serialize(self.schemas.get_by_name('overlay.query'), data={
                'overlay': '12b8a83f098e15ea47fe76d0b0df0986ff6dda1980796b084b0d2a68b2558649'}) + self.schemas.serialize(
                self.schemas.get_by_name('overlay.getRandomPeers'), {'peers': {'nodes': peers}})
        }

        from_ = self.schemas.serialize(self.schemas.get_by_name('pub.ed25519'),
                                       data={'key': self.client.ed25519_public.encode().hex()})

        data = {
            'from': from_,
            'from_short': {'id': self.client.get_key_id().hex()},
            'messages': [create_channel_message, get_random_peers_messsage],
            'address': {
                'addrs': [

                ],
                'version': ts,
                'reinit_date': ts,
                'priority': 0,
                'expire_at': 0,
            },
            'recv_addr_list_version': ts,
            'reinit_date': ts,
            'dst_reinit_date': 0,
        }

        self.listener = self.loop.create_task(self.listen())

        messages = await self.send_message_outside_channel(data)

        confirm_channel = messages[0]
        assert confirm_channel.get('@type') == 'adnl.message.confirmChannel', f'expected adnl.message.confirmChannel, got {confirm_channel.get("@type")}'
        assert confirm_channel['peer_key'] == channel_client.ed25519_public.encode().hex()

        channel_server = Server(self.host, self.port, bytes.fromhex(confirm_channel['key']))
        channel = AdnlChannel(channel_client, channel_server, self.local_id, self.peer_id)
        self.channels.append(channel)

        # test channel:
        data = {
            'message': get_random_peers_messsage,
        }
        result = await self.send_message_in_channel(data)
        return result

    def process_incoming_message(self, message: dict):
        if message['@type'] == 'adnl.message.answer':
            future = self.tasks.pop(message.get('query_id'))
            future.set_result(message['answer'])

        elif message['@type'] == 'adnl.message.confirmChannel':
            future = self.tasks.pop(message.get('peer_key'))
            future.set_result(message)
        elif message['@type'] == 'adnl.message.custom':
            msg = MessageAny.deserialize(Slice.one_from_boc(message['data'][1]['data']['message']['data']))
            print('EXTERNAL', datetime.datetime.now(), msg, )
        else:
            print('received smth else', message)

    async def listen(self):
        while True:
            packet, addr = await self.protocol.receive()
            decrypted = self._decrypt_any(packet)
            if decrypted is None:
                continue
            response = self.schemas.deserialize(decrypted)[0]
            received_confirm_seqno = response.get('confirm_seqno')

            if received_confirm_seqno > self.confirm_seqno:
                self.confirm_seqno = received_confirm_seqno

            message = response.get('message')
            messages = response.get('messages')

            if message:
                self.process_incoming_message(message)
            if messages:
                for message in messages:
                    self.process_incoming_message(message)
