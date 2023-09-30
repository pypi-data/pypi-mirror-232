from concurrent import futures
from functools import wraps

from grpc import Server, server
from typing_extensions import Self

from .arp_pb2_grpc import AIMServicer, add_AIMServicer_to_server


class ServerBuilder:
    _server: Server

    def __init__(self) -> None:
        self._server = server(futures.ThreadPoolExecutor(max_workers=8))

    def set_port(self, port: int) -> Self:
        self._server.add_insecure_port(f"[::]:{port}")
        return self

    def add_servicer(self, servicer: AIMServicer) -> Self:
        add_AIMServicer_to_server(servicer, self._server)
        return self

    def build(self) -> Server:
        return self._server

    def new(self) -> Self:
        return ServerBuilder()
