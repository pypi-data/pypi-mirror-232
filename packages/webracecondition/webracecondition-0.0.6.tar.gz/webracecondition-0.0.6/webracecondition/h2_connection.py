import time
import logging
import typing as T
from abc import ABC, abstractmethod

import scapy.contrib.http2 as h2
import scapy.supersocket as supersocket
import scapy.packet as packet
from scapy.data import MTU

from .frames import (
    is_frame_type,
    has_ack_set,
    has_end_stream_set,
    create_settings_frame,
)

MAX_HEADER_TABLE_SIZE = (1 << 16) - 1
MAX_FRAME_SIZE = (1 << 24) - 1
WIN_SIZE = (1 << 31) - 1


class H2Connection(ABC):
    """
    Base class for HTTP/2 connections.
    """

    def __init__(self, host: str, port: int, print_frames: bool = True) -> None:
        self._host = host
        self._port = port
        self._print_frames = print_frames

        self.sock = self._connect()
        self._send_preface()
        self._send_initial_settings()
        self._setup_wait_loop()

        logging.info("Completed HTTP/2 connection setup")

    @abstractmethod
    def _connect(self) -> supersocket.StreamSocket:
        pass

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    def close(self) -> None:
        self.sock.close()

    def set_timeout(self, value: float) -> None:
        self.sock.ins.settimeout(value)

    def read_answers(
        self, stream_ids: T.List[int]
    ) -> T.Tuple[T.Dict[int, str], T.Dict[int, h2.H2Frame]]:
        # The stream variable will contain all read frames
        stream = h2.H2Seq()
        # Number of streams closed by the server
        closed_stream = 0

        logging.info("Read loop starting...")
        while True:
            frames = self._recv_frames()
            if frames.stream_id in stream_ids:
                stream.frames.append(frames)
                if self._print_frames:
                    stream.show()
                if has_end_stream_set(frames):
                    closed_stream += 1

            if closed_stream >= len(stream_ids):
                break

        # Structure used to store textual representation of the stream headers
        headers: T.Dict[int, str] = {}
        # Structure used to store data from each stream
        data: T.Dict[int, h2.H2Frame] = {}

        srv_tblhdr = h2.HPackHdrTable(
            dynamic_table_max_size=MAX_HEADER_TABLE_SIZE,
            dynamic_table_cap_size=MAX_HEADER_TABLE_SIZE,
        )
        for frame in stream.frames:
            # If this frame is a header
            if is_frame_type(frame, h2.H2HeadersFrame):
                # Convert this header block into its textual representation.
                headers[frame.stream_id] = srv_tblhdr.gen_txt_repr(frame)
            # If this frame is data
            if is_frame_type(frame, h2.H2DataFrame):
                if frame.stream_id not in data:
                    data[frame.stream_id] = []
                data[frame.stream_id].append(frame)

        return (headers, data)

    def infinite_read_loop(self) -> None:
        """
        Start an infinite loop that reads and possibly prints received frames.
        :param print_frames: whether to print received frames
        """
        logging.info("Infinite read loop starting...")
        while True:
            frames = self._recv_frames()
            if self._print_frames:
                for f in frames:
                    logging.info("Read frame:")
                    f.show()

    def send_frames(self, *frames: h2.H2Frame) -> None:
        """
        Send frames on this connection.
        :param frames: 1 or more frames to send
        """
        self._send_frames(*frames)

    def recv_frames(self) -> h2.H2Frame:
        """
        Synchronously receive frames. Block if there aren't any frames to read.
        :return: list of received frames
        """
        return self._recv_frames()

    def _setup_wait_loop(self) -> None:
        server_has_acked_settings = False
        client_has_acked_settings = False

        while not server_has_acked_settings or not client_has_acked_settings:
            frames = self._recv_frames()
            if self._print_frames:
                frames.show()
            for f in frames:
                if is_frame_type(f, h2.H2SettingsFrame):
                    if has_ack_set(f):
                        logging.info("Server acked our settings")
                        server_has_acked_settings = True
                    else:
                        logging.info("Got server settings, acking")
                        self._ack_settings()
                        client_has_acked_settings = True

    def _ack_settings(self) -> None:
        self._send_frames(create_settings_frame(is_ack=True))
        logging.info("Acked server settings")

    def _send_initial_settings(self) -> None:
        settings = [
            h2.H2Setting(id=h2.H2Setting.SETTINGS_ENABLE_PUSH, value=0),
            h2.H2Setting(id=h2.H2Setting.SETTINGS_INITIAL_WINDOW_SIZE, value=WIN_SIZE),
            h2.H2Setting(
                id=h2.H2Setting.SETTINGS_HEADER_TABLE_SIZE, value=MAX_HEADER_TABLE_SIZE
            ),
            h2.H2Setting(id=h2.H2Setting.SETTINGS_MAX_FRAME_SIZE, value=MAX_FRAME_SIZE),
            h2.H2Setting(id=h2.H2Setting.SETTINGS_MAX_CONCURRENT_STREAMS, value=1000),
        ]

        self._send_frames(create_settings_frame(settings))

        logging.info("Sent settings")

    def _send_frames(self, *frames: h2.H2Frame) -> None:
        b = bytes()
        for f in frames:
            b += bytes(f)
        self._send(b)

    def _send_preface(self) -> None:
        self._send(packet.Raw(h2.H2_CLIENT_CONNECTION_PREFACE))

    def _send(self, data: bytes) -> None:
        self.sock.send(data)

    def _recv_frames(self) -> h2.H2Frame:
        chunk = self._recv()
        return chunk

    def _recv(self) -> bytes:
        while True:
            try:
                return self.sock.recv(MTU)
            except AssertionError:
                # Frame parsing failed on current data, try again in 100 ms
                time.sleep(0.1)
