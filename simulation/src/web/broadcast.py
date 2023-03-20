import socket
import asyncio_dgram
import struct

import utils
import conf

MCAST_GRP = "224.1.1.1"

class Broadcast():
    def __init__(self, port, random_group=False):
        if random_group:
            group = utils.get_random_int(1, conf.env("NUM_GROUPS"))
            self.__port = port + group
        else:
            self.__port = port

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind((MCAST_GRP, self.__port))
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        self.__sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.__sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    async def initialize(self):
        self.socket = await asyncio_dgram.from_socket(self.__sock)

    async def recv(self):
        data, _ = await self.socket.recv()
        return data

    async def send(self, msg):
        await self.socket.send(msg, (MCAST_GRP,self.__port))

    def close(self):
        self.socket.close()

    def __str__(self) -> str:
        return f"{MCAST_GRP}:{self.__port}"