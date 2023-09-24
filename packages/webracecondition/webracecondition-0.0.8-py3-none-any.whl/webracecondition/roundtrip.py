import io
import re
import typing as T
from urllib.parse import urlencode


class Request:
    def __init__(
        self,
        method: str,
        path: str,
        headers: T.Optional[T.Dict[str, str]] = None,
        params: T.Optional[T.Dict[str, T.Any]] = None,
        body: T.Optional[bytes] = None,
    ):
        self._method = method
        self._path = self._create_path(path, params)
        self._headers = headers
        self._params = params
        self._body = body

    @property
    def method(self) -> str:
        return self._method.upper()

    @property
    def path(self) -> str:
        return self._create_path(self._path, self._params)

    @property
    def headers(self) -> T.Dict[str, str]:
        headers = self._headers if self._headers is not None else {}
        if "content-length" in headers:
            del headers["content-length"]

        if self._body is None:
            # Set Content-Length to 0 for methods that can have a body
            # but don't provide one. (i.e. not GET or HEAD)
            if self.method not in ["GET", "HEAD"]:
                headers["content-length"] = "0"
            return headers

        headers["content-length"] = self._get_content_length()

        return headers

    @property
    def body(self) -> T.Optional[bytes]:
        return self._body

    def _create_path(self, path: str, params: T.Optional[T.Dict[str, T.Any]]) -> str:
        query_string = ""
        if params is not None:
            query_string = urlencode(params)

        return path if query_string == "" else f"{path}?{query_string}"

    def _get_content_length(self) -> str:
        if self._body is None:
            return "0"
        return str(len(self._body))


class Response:
    def __init__(self, headers: str, raw_body: bytes):
        self._headers = headers
        self._raw_body = raw_body

    @property
    def raw(self) -> bytes:
        return self._raw_body

    @property
    def status_code(self) -> int:
        match = re.search(r"\b\d{3}\b", self._headers.split("\n")[0])
        if match:
            return int(match.group(0))
        return -1

    @property
    def headers(self) -> T.Dict[str, str]:
        headers: T.Dict[str, str] = {}
        for line in self._headers.split("\n")[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()  # Remove leading/trailing spaces
                value = value.strip()  # Remove leading/trailing spaces
                headers[key] = value

        return headers


class RoundTrip:
    def __init__(self, hostname: str, port: int):
        self.hostname = hostname
        self.port = port
        self.request: T.Optional[Request] = None
        self.response: T.Optional[Response] = None

    def set_request(self, request: Request) -> None:
        self.request = request

    def set_response(self, response: Response) -> None:
        self.response = response

    def __str__(self) -> str:
        buffer = io.StringIO()
        if self.response is not None:
            buffer.write(f"HTTP/2 {self.response.status_code}\n")
            for k, v in self.response.headers.items():
                buffer.write(f"{k}: {v}\n")
        buffer.write("\n\n")
        if self.response is not None:
            buffer.write(self.response.raw.decode("UTF-8", "ignore"))

        return buffer.getvalue()
