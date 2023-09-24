import socket
import ssl
import logging

import scapy.contrib.http2 as h2
import scapy.supersocket as supersocket

from .h2_connection import H2Connection


class H2TLSConnection(H2Connection):
    """
    TLS-secured HTTP/2 connection.
    """

    def __init__(
        self,
        host: str,
        port: int = 443,
        verify: bool = False,
        ssl_ctx: ssl.SSLContext = ssl.create_default_context(),
        print_frames: bool = True,
    ):
        if not ssl.HAS_ALPN:
            raise AssertionError("TLS ALPN extension is required for HTTP/2 over TLS")

        self._verify = verify
        self._ssl_ctx = ssl_ctx
        super().__init__(host, port, print_frames=print_frames)

    def _connect(self) -> supersocket.StreamSocket:
        """
        Set up the connection by creating the TCP connection, performing the TLS handshake with ALPN
        selected protocol h2 and finally performing the HTTP/2 handshake.
        :param host: host to connect to, e.g. example.com or 127.0.0.1
        :param port: TCP port to connect to
        """
        addrinfos = socket.getaddrinfo(
            self.host, self.port, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )

        if len(addrinfos) == 0:
            raise AssertionError(
                f"No TCP socket info available for host {self.host} and port {self.port}"
            )

        addrinfo = addrinfos[0]

        logging.debug("Endpoint addrinfo: {}".format(addrinfo))

        raw_sock = socket.socket(addrinfo[0], addrinfo[1], addrinfo[2])
        self._setsockopt(raw_sock)

        if not self._verify:
            self._ssl_ctx.check_hostname = False
            self._ssl_ctx.verify_mode = ssl.CERT_NONE

        self._ssl_ctx.set_alpn_protocols(["h2"])
        ssl_sock = self._ssl_ctx.wrap_socket(raw_sock, server_hostname=self.host)
        ssl_sock.connect(addrinfo[4])

        if ssl_sock.selected_alpn_protocol() != "h2":
            raise AssertionError("Server did not agree to use HTTP/2 in ALPN")

        return supersocket.SSLStreamSocket(ssl_sock, basecls=h2.H2Frame)

    def _setsockopt(self, raw_sock: socket.socket) -> None:
        raw_sock.settimeout(30)
        raw_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)
        raw_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            raw_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
