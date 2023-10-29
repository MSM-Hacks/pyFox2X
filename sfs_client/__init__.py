import io
import json
import os
import socket
import multiprocessing.connection, time
import copy

from .task import SFSTask
from ..sfs_types import SFSArray
from ..sfs_types import SFSObject

import time


class SFSClient:
    connection = None

    def __init__(self, proxy_host: str = None, proxy_port: int = None, proxy_login: str = None,
                 proxy_password: str = None):
        if proxy_host is None or proxy_port is None:
            self.connection = socket.socket()
        else:
            # pip install pysocks requests urllib3

            import socks

            def create_connection(address, timeout=None, source_address=None):
                sock = socks.socksocket()
                sock.connect(address)
                return sock

            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, proxy_port, username=proxy_login,
                                  password=proxy_password)
            copy_socket = copy.deepcopy(socket)
            copy_socket.socket = socks.socksocket
            copy_socket.create_connection = create_connection
            self.connection = copy_socket.socket()

        # self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024 * 4)

    def __del__(self):
        self.connection.close()

    def connect(self, host: str, port: int = 9933):
        self.connection.connect((host, port))
        self.send_handshake_request()

    @staticmethod
    def compile_packet(packet) -> bytes:
        compiled_packet = packet.compile()
        if len(compiled_packet) < 65535:
            return b'\x80' + (len(compiled_packet)).to_bytes(2, "big") + compiled_packet
        else:
            return b'\x88' + (len(compiled_packet)).to_bytes(4, "big") + compiled_packet

    @staticmethod
    def decompile_packet(packet: bytes) -> SFSObject:
        return SFSObject.decompile(packet).get("p")

    @staticmethod
    def decompile_packet_conn(conn: io.BytesIO) -> SFSObject:
        return SFSObject.decompile_conn(conn).get("p")

    def send_raw(self, packet: bytes):
        self.connection.sendall(packet)


    def send_packet(self, c: int, a: int, params: SFSObject):
        packet = SFSObject()
        packet.putByte("c", c)
        packet.putShort("a", a)
        packet.putSFSObject("p", params)

        self.send_raw(SFSClient.compile_packet(packet))

    def send_handshake_request(self):
        session_info = SFSObject()
        session_info.putUtfString("api", "1.0.3")
        session_info.putUtfString("cl", "UnityPlayer::")
        session_info.putBool("bin", True)

        self.send_packet(0, 0, session_info)
        self.read_response()

    def send_login_request(self, zone: str, username: str, password: str, auth_params: SFSObject):
        auth_info = SFSObject()
        auth_info.putUtfString("zn", zone)
        auth_info.putUtfString("un", username)
        auth_info.putUtfString("pw", password)
        auth_info.putSFSObject("p", auth_params)

        self.send_packet(0, 1, auth_info)

    def send_extension_request(self, command: str, params: SFSObject):
        request = SFSObject()
        request.putUtfString("c", command)
        request.putInt("r", -1)
        request.putSFSObject("p", params)

        self.send_packet(1, 12, request)

    def read_response(self):
        response = b''
        packet_size = b''

        packet_type = self.connection.recv(1)
        if packet_type == b'\x88':
            packet_size_len = 4
        elif packet_type == b'\x80':
            packet_size_len = 2
        else:
            return SFSObject(), b""

        while packet_size_len > 0:
            new = self.connection.recv(packet_size_len)
            packet_size += new
            packet_size_len -= len(new)

        packet_size = int.from_bytes(packet_size, 'big')

        while len(response) < packet_size:
            chunk_size = min(packet_size - len(response), 4096*4)
            response += self.connection.recv(chunk_size)

        packet_bytes = io.BytesIO(response)

        response = self.decompile_packet_conn(packet_bytes)

        return response, b"TODO: Fix bytes"

        # return self.decompile_packet(response), response

    def wait_extension_response(self, command: str, binary=None, timeout=None):
        if binary is None:
            binary = False

        task = SFSTask(self)
        return task.wait_response(command, binary, timeout)

    def wait_requests(self, commands: list, binary=None):
        if binary is None:
            binary = False

        cmd, params = '', SFSObject()
        bin_packet = bytes()
        fuck_counter = 0

        while not cmd in commands:
            response, bin_packet = self.read_response()
            if bin_packet == b"":
                fuck_counter += 1
            else:
                fuck_counter = 0

            if fuck_counter >= 10:
                self.connection.close()
                return

            if 'c' in response.getValue():
                cmd, params = response.get("c"), response.get("p")
        print("OK")
        if binary:
            return cmd, bin_packet
        print(json.dumps(params.getValue(), indent=2))
        return cmd, params

    def request(self, command: str, params: SFSObject, binary=None, parse_chunks=None):
        if binary is None:
            binary = False
        if parse_chunks is None:
            parse_chunks = False

        self.send_extension_request(command, params)
        response = self.wait_extension_response(command, binary)

        print(response)

        if response is None:
            return self.request(command, params, binary, parse_chunks)

        if response.get("numChunks") is None or not parse_chunks:
            return response
        packets = [response]
        for _ in range(response.get("numChunks") - 1):
            packets.append(self.wait_extension_response(command))
        return packets

    def get_connection(self):
        return self.connection
