import typing as T

import scapy.contrib.http2 as h2
from scapy.packet import NoPayload


def create_request_frames(
    scheme: str,
    host: str,
    port: int,
    method: str,
    path: str,
    stream_id: int,
    headers: T.Optional[T.Dict[str, str]] = None,
    body: T.Optional[bytes] = None,
) -> h2.H2Seq:
    """
    Create HTTP/2 frames representing a HTTP request.
    :param method: HTTP request method, e.g. GET
    :param path: request path, e.g. /example/path
    :param stream_id: stream ID to use for this request, e.g. 1
    :param headers: request headers
    :param body: request body
    :return: frame sequence consisting of a single HEADERS frame, potentially followed by CONTINUATION and DATA frames
    """
    header_table = h2.HPackHdrTable()
    req_str = (
        f":method {method}\n:path {path}\n:authority {host}:{port}\n:scheme {scheme}\n"
    )

    if headers is not None:
        req_str += "\n".join(
            map(lambda e: "{}: {}".format(e[0].lower(), e[1]), headers.items())
        )

    return header_table.parse_txt_hdrs(
        bytes(req_str.strip(), "UTF-8"),
        stream_id=stream_id,
        body=body,
        is_sensitive=lambda hdr_name, hdr_val: hdr_name in ["cookie"],
    )


def create_dependant_request_frames(
    scheme: str,
    host: str,
    port: int,
    method: str,
    path: str,
    stream_id: int,
    dependency_stream_id: int = 0,
    dependency_weight: int = 0,
    dependency_is_exclusive: bool = False,
    headers: T.Optional[T.Dict[str, str]] = None,
    body: T.Optional[bytes] = None,
) -> h2.H2Seq:
    """
    Create HTTP/2 frames representing a HTTP request that depends on another request (stream).
    :param method: HTTP request method, e.g. GET
    :param path: request path, e.g. /example/path
    :param stream_id: stream ID to use for this request, e.g. 1
    :param dependency_stream_id: ID of the stream that this request (stream) will depend upon
    :param dependency_weight: weight of the dependency
    :param dependency_is_exclusive: whether the dependency is exclusive
    :param headers: request headers
    :param body: request body
    :return: frame sequence consisting of a single HEADERS frame, potentially followed by CONTINUATION and DATA frames
    """
    req_frameseq = create_request_frames(
        scheme=scheme,
        host=host,
        port=port,
        method=method,
        path=path,
        stream_id=stream_id,
        headers=headers,
        body=body,
    )

    dep_req_frames = []

    for f in req_frameseq.frames:
        if is_frame_type(f, h2.H2HeadersFrame):
            pri_hdr_frame = h2.H2PriorityHeadersFrame()
            pri_hdr_frame.stream_dependency = dependency_stream_id
            pri_hdr_frame.weight = dependency_weight
            pri_hdr_frame.exclusive = 1 if dependency_is_exclusive else 0
            pri_hdr_frame.hdrs = f.hdrs
            dep_req_frames.append(
                h2.H2Frame(stream_id=f.stream_id, flags=f.flags | {"+"}) / pri_hdr_frame
            )
        else:
            dep_req_frames.append(f)

    req_frameseq.frames = dep_req_frames

    return req_frameseq


def create_ping_frame(
    data: T.Union[str, bytes, None] = None, is_ack: bool = False
) -> h2.H2Frame:
    """
    Create a HTTP/2 PING frame.
    :param data: opaque data that will be replicated in the response, either a 8-character string or 8 bytes
    :param is_ack: whether to set the ACK flag
    """
    if is_ack:
        frame = h2.H2Frame(flags={"A"})
    else:
        frame = h2.H2Frame()

    if data is not None:
        ping = h2.H2PingFrame(data)
    else:
        ping = h2.H2PingFrame()

    return frame / ping


def create_priority_frame(
    dependant_stream_id: int,
    dependency_stream_id: int,
    weight: int = 0,
    is_exclusive: bool = False,
) -> h2.H2Frame:
    """
    Create a HTTP/2 PRIORITY frame.
    :param dependant_stream_id: ID of the stream that will depend on the dependency stream
    :param dependency_stream_id: ID of the stream that will be depended upon
    :param weight: weight of the dependency
    :param is_exclusive: whether the dependency is exclusive
    """
    f = h2.H2Frame(stream_id=dependant_stream_id) / h2.H2PriorityFrame()
    f.stream_dependency = dependency_stream_id
    f.weight = weight
    f.exclusive = 1 if is_exclusive else 0

    return f


def create_settings_frame(
    settings: T.Optional[T.List[h2.H2Setting]] = None, is_ack: bool = False
) -> h2.H2Frame:
    """
    Create a HTTP/2 SETTINGS frame.
    :param settings: list of settings, can be empty or None
    :param is_ack: whether to set the ACK flag
    """
    if is_ack:
        return h2.H2Frame(flags={"A"}) / h2.H2SettingsFrame()

    settings_frame = h2.H2Frame() / h2.H2SettingsFrame()
    if settings is not None:
        settings_frame.settings = settings
    return settings_frame


def create_rst_stream_frame(
    stream_id: int, error_code: h2.H2ErrorCodes = h2.H2ErrorCodes.NO_ERROR
) -> h2.H2Frame:
    """
    Create a HTTP/2 RST_STREAM frame.
    :param stream_id: which stream to end
    :param error_code: error code
    """
    rst = h2.H2Frame(stream_id=stream_id) / h2.H2ResetFrame()
    rst.error = error_code
    return rst


def create_goaway_frame(
    error_code: h2.H2ErrorCodes = h2.H2ErrorCodes.NO_ERROR,
    last_stream_id: int = 0,
    additional_data: str = "",
) -> h2.H2Frame:
    """
    Create a HTTP/2 GOAWAY frame.
    :param error_code: error code
    :param last_stream_id: last processed server-initiated stream ID
    :param additional_data: additional debug data
    """
    goaway = h2.H2Frame() / h2.H2GoAwayFrame()
    goaway.error = error_code
    goaway.last_stream_id = last_stream_id
    goaway.additional_data = additional_data

    return goaway


def create_window_update_frame(
    stream_id: int, window_increment: int, reserved_bit: int = 0
) -> h2.H2Frame:
    """
    Create a HTTP/2 WINDOW_UPDATE frame.
    :param stream_id: which stream's window to increment, set to 0 to increment the connection-wide window
    :param window_increment: window increment in bytes
    :param reserved_bit: reserved bit, must be set to 0 according to the spec
    """
    win = h2.H2Frame(stream_id=stream_id) / h2.H2WindowUpdateFrame()
    win.win_size_incr = window_increment
    win.reserved = reserved_bit

    return win


def is_frame_type(
    h2_frame: h2.H2Frame, inner_frame_type: T.Type[h2.H2FramePayload]
) -> bool:
    """
    Check the type of a HTTP/2 frame.
    :param h2_frame: unknown-type frame
    :param inner_frame_type: specific frame type
    """
    type_id_matches = h2_frame.type == inner_frame_type.type_id

    class_matches = isinstance(h2_frame.payload, inner_frame_type) or isinstance(
        h2_frame.payload, NoPayload
    )

    return type_id_matches and class_matches


def has_ack_set(h2_frame: h2.H2Frame) -> bool:
    """
    Check whether the given frame has the ACK flag set.
    :param h2_frame: frame to check
    """
    return "A" in h2_frame.flags


def has_end_stream_set(h2_frame: h2.H2Frame) -> bool:
    """
    Check whether the given frame has the END_STREAM flag set.
    :param h2_frame: frame to check
    """
    return "ES" in h2_frame.flags


def gen_stream_ids(n: int) -> T.List[int]:
    """
    Generate n valid client-side stream IDs (positive odd integers).
    :param n: the number of IDs to generate
    :return: list of generated IDs
    """
    return [i for i in range(1, n * 2, 2)]
