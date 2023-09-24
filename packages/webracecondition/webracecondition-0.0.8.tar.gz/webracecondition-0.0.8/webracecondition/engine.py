import time
import typing as T
from urllib.parse import urlparse
import scapy.contrib.http2 as h2

from .frames import (
    create_request_frames,
    create_dependant_request_frames,
    create_ping_frame,
)
from .h2_tls_connection import H2TLSConnection
from .roundtrip import Request, Response, RoundTrip


class LongRunningChain:
    def __init__(self, root: Request):
        self._root = root
        self._requests: T.List[Request] = []

    @property
    def root(self) -> Request:
        return self._root

    @property
    def dependant_requests(self) -> T.List[Request]:
        return self._requests

    def add_request(self, req: Request) -> None:
        self._requests.append(req)


class Engine:
    def __init__(self, base_url: str, verify: bool = False):
        parsed_url = urlparse(base_url)

        if parsed_url.scheme == "https":
            self._scheme = parsed_url.scheme
        else:
            raise AssertionError("Only https is supported")

        if parsed_url.hostname is not None and parsed_url.hostname != "":
            self._hostname = parsed_url.hostname
        else:
            raise AssertionError("Hostname cannot be empty")

        self._port = 443 if parsed_url.port is None else parsed_url.port
        self._verify = verify
        self._requests: T.List[Request] = []

    @property
    def scheme(self) -> str:
        return self._scheme

    @property
    def host(self) -> str:
        return self._hostname

    @property
    def port(self) -> int:
        return self._port

    def add_request(self, req: Request) -> None:
        self._requests.append(req)

    def last_frame_sync_attack(
        self,
        sleep_time: float = 100 / 1000,
        timeout: float = 30,
        print_frames: bool = False,
    ) -> T.List[RoundTrip]:
        conn = H2TLSConnection(
            host=self._hostname,
            port=self._port,
            verify=self._verify,
            print_frames=print_frames,
        )

        conn.set_timeout(timeout)

        final_seq = h2.H2Seq()
        round_trips: T.Dict[int, RoundTrip] = {}

        for idx, req in enumerate(self._requests):
            stream_id = self._generate_stream_id(idx)

            round_trips[stream_id] = RoundTrip(self._hostname, self._port)
            round_trips[stream_id].set_request(req)

            last_byte = None
            body = None
            if req.body is not None:
                last_byte = req.body[-1:]
                body = req.body[:-1]

            rframe = create_request_frames(
                scheme=self._scheme,
                host=self._hostname,
                port=self._port,
                method=req.method,
                path=req.path,
                stream_id=stream_id,
                headers=req.headers,
                body=body,
            )

            if print_frames:
                rframe.show()

            # Remove END_STREAM flag from latest frames
            rframe.frames[len(rframe.frames) - 1].flags.remove("ES")

            # Send the request frames
            conn.send_frames(rframe)

            # Create the final DATA frame using scapy and store it
            final_seq.frames.append(
                h2.H2Frame(flags={"ES"}, stream_id=stream_id)
                / h2.H2DataFrame(data=last_byte)
            )

        # Sleep a little to make sure previous frames have been delivered
        time.sleep(sleep_time)

        # Send a ping packet to warm the local connection.
        conn.send_frames(create_ping_frame())

        # Send the final frames to complete the requests
        conn.send_frames(*final_seq)

        # Listening for the answers on the connection
        headers, data = conn.read_answers(list(round_trips.keys()))

        # Close the connection
        conn.close()

        for id in round_trips.keys():
            raw_body = b""
            for frgmt in data[id]:
                if frgmt.len != 0:
                    raw_body += frgmt.payload.data

            round_trips[id].set_response(Response(headers[id], raw_body))

        return list(round_trips.values())

    def dependant_streams_attack(
        self,
        long_running_chain: LongRunningChain,
        timeout: float = 30,
        print_frames: bool = False,
    ) -> T.List[RoundTrip]:
        conn = H2TLSConnection(
            host=self._hostname,
            port=self._port,
            verify=self._verify,
            print_frames=print_frames,
        )

        conn.set_timeout(timeout)

        round_trips: T.Dict[int, RoundTrip] = {}

        chain_seq = h2.H2Seq()

        root_stream_id = self._generate_stream_id(0)

        round_trips[root_stream_id] = RoundTrip(self._hostname, self._port)
        round_trips[root_stream_id].set_request(long_running_chain.root)

        root_frame = create_request_frames(
            scheme=self._scheme,
            host=self._hostname,
            port=self._port,
            method=long_running_chain.root.method,
            path=long_running_chain.root.path,
            stream_id=root_stream_id,
            headers=long_running_chain.root.headers,
            body=long_running_chain.root.body,
        )

        if print_frames:
            root_frame.show()

        chain_seq.frames.append(root_frame)

        dependency_stream_id = root_stream_id

        for idx, req in enumerate(long_running_chain.dependant_requests):
            stream_id = self._generate_stream_id(idx + 1)

            round_trips[stream_id] = RoundTrip(self._hostname, self._port)
            round_trips[stream_id].set_request(req)

            rframe = create_dependant_request_frames(
                scheme=self._scheme,
                host=self._hostname,
                port=self._port,
                method=req.method,
                path=req.path,
                stream_id=stream_id,
                dependency_stream_id=dependency_stream_id,
                headers=req.headers,
                body=req.body,
            )

            dependency_stream_id = stream_id

            if print_frames:
                rframe.show()

            chain_seq.frames.append(rframe)

        race_req_seq = h2.H2Seq()

        for idx, req in enumerate(self._requests):
            stream_id = self._generate_stream_id(
                idx + len(long_running_chain.dependant_requests) + 1
            )

            round_trips[stream_id] = RoundTrip(self._hostname, self._port)
            round_trips[stream_id].set_request(req)

            rframe = create_dependant_request_frames(
                scheme=self._scheme,
                host=self._hostname,
                port=self._port,
                method=req.method,
                path=req.path,
                stream_id=stream_id,
                dependency_stream_id=dependency_stream_id,
                headers=req.headers,
                body=req.body,
            )

            if print_frames:
                rframe.show()

            race_req_seq.frames.append(rframe)

        # First send the long-running chain frames
        conn.send_frames(*chain_seq)

        # Next, race request frames are sent to run concurrently after the long-running chain completes
        conn.send_frames(*race_req_seq)

        # Listening for the answers on the connection
        headers, data = conn.read_answers(list(round_trips.keys()))

        # Close the connection
        conn.close()

        for id in round_trips.keys():
            raw_body = b""
            for frgmt in data[id]:
                if frgmt.len != 0:
                    raw_body += frgmt.payload.data

            round_trips[id].set_response(Response(headers[id], raw_body))

        return list(round_trips.values())

    def _generate_stream_id(self, idx: int) -> int:
        """
        Generates a valid client-side stream ID for passed index (positive odd integer).
        :param idx: the index for which an ID should be generated
        :return: a generated ID
        """
        return 2 * idx + 1
