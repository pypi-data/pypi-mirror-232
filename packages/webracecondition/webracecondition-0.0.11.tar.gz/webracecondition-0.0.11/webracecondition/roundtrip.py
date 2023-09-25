import re
from json import dumps
import typing as T
from urllib.parse import urlencode


class Request:
    def __init__(
        self,
        method: str,
        path: str,
        headers: T.Optional[T.Dict[str, str]] = None,
        cookies: T.Optional[T.Dict[str, str]] = None,
        params: T.Optional[T.Dict[str, T.Any]] = None,
        data: T.Optional[T.Dict[str, T.Any]] = None,
        json: T.Optional[T.Dict[str, T.Any]] = None,
        raw_body: T.Optional[bytes] = None,
    ):
        self._method = method
        self._path = self._create_path(path, params)
        self._headers = headers if headers is not None else {}
        self._cookies = cookies
        self._params = params
        self._body = self._prepare_body(data=data, json=json, raw_body=raw_body)

    @property
    def method(self) -> str:
        return self._method.upper()

    @property
    def path(self) -> str:
        return self._path

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
        else:
            headers["content-length"] = self._get_content_length()

        if self._cookies is not None:
            headers["cookie"] = self._prepare_cookie_header()

        return headers

    @property
    def body(self) -> T.Optional[bytes]:
        return self._body

    def _prepare_body(
        self,
        data: T.Optional[T.Dict[str, T.Any]] = None,
        json: T.Optional[T.Dict[str, T.Any]] = None,
        raw_body: T.Optional[bytes] = None,
    ) -> T.Optional[bytes]:
        if json is None and data is None and raw_body is None:
            return None
        elif json is not None and data is None and raw_body is None:
            self._headers["content-type"] = "application/json"
            return dumps(json, allow_nan=False).encode("utf-8")
        elif data is not None and json is None and raw_body is None:
            self._headers["content-type"] = "application/x-www-form-urlencoded"
            return urlencode(data).encode("utf-8")
        elif raw_body is not None and data is None and json is None:
            return raw_body

        raise ValueError("Only one of data, json, or raw_body should be set")

    def _prepare_cookie_header(self) -> str:
        if self._cookies is None:
            return ""

        cookie_header = "; ".join(
            [f"{key}={value}" for key, value in self._cookies.items()]
        )
        return cookie_header

    def _create_path(
        self, path: str, params: T.Optional[T.Dict[str, T.Any]] = None
    ) -> str:
        if params is not None:
            return f"{path}?{urlencode(params)}"

        return path

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
        if self.request is not None and self.response is not None:
            return f"{self.request.method} {self.request.path} HTTP/2: {self.response.status_code}"
        if self.request is None and self.response is not None:
            return f"??? ??? HTTP/2: {self.response.status_code}"
        if self.response is None and self.request is not None:
            return f"{self.request.method} {self.request.path} HTTP/2: ???"
        return "??? ??? HTTP/2: ???"
