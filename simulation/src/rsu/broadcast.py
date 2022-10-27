import socket
import asyncio_dgram

import conf

MCAST_GRP = "224.1.1.1"

class Broadcast():
    def __init__(self):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    async def initialize(self):
        self.socket = await asyncio_dgram.from_socket(self.__sock)

    async def send(self, msg):
        await self.socket.send(msg, (MCAST_GRP,conf.env("HEARTBEAT_PORT")))

    def close(self):
        self.socket.close()