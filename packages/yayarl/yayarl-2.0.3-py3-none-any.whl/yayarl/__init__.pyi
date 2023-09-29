import sys
from functools import _CacheInfo
from typing import Any, Mapping, Optional, Sequence, Tuple, Type, Union, overload

import multidict
import requests
from requests.cookies import RequestsCookieJar

if sys.version_info >= (3, 8):
    from typing import Final, TypedDict, final
else:
    from typing_extensions import Final, TypedDict, final

_SimpleQuery = Union[str, int, float]
_QueryVariable = Union[_SimpleQuery, Sequence[_SimpleQuery]]
_Query = Union[
    None, str, Mapping[str, _QueryVariable], Sequence[Tuple[str, _QueryVariable]]
]


@final
class URL:
    scheme: Final[str]
    raw_user: Final[str]
    user: Final[Optional[str]]
    raw_password: Final[Optional[str]]
    password: Final[Optional[str]]
    raw_host: Final[Optional[str]]
    host: Final[Optional[str]]
    port: Final[Optional[int]]
    explicit_port: Final[Optional[int]]
    raw_authority: Final[str]
    authority: Final[str]
    raw_path: Final[str]
    path: Final[str]
    raw_query_string: Final[str]
    query_string: Final[str]
    path_qs: Final[str]
    raw_path_qs: Final[str]
    raw_fragment: Final[str]
    fragment: Final[str]
    query: Final[multidict.MultiDict[str]]
    raw_name: Final[str]
    name: Final[str]
    raw_suffix: Final[str]
    suffix: Final[str]
    raw_suffixes: Final[Tuple[str, ...]]
    suffixes: Final[Tuple[str, ...]]
    raw_parts: Final[Tuple[str, ...]]
    parts: Final[Tuple[str, ...]]
    parent: Final[URL]

    def __init__(
        self, val: Union[str, "URL"] = ..., *, encoded: bool = ...
    ) -> None: ...

    @classmethod
    def build(
        cls,
        *,
        scheme: str = ...,
        authority: str = ...,
        user: Optional[str] = ...,
        password: Optional[str] = ...,
        host: str = ...,
        port: Optional[int] = ...,
        path: str = ...,
        query: Optional[_Query] = ...,
        query_string: str = ...,
        fragment: str = ...,
        encoded: bool = ...
    ) -> URL: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __bytes__(self) -> bytes: ...

    def __eq__(self, other: Any) -> bool: ...

    def __le__(self, other: Any) -> bool: ...

    def __lt__(self, other: Any) -> bool: ...

    def __ge__(self, other: Any) -> bool: ...

    def __gt__(self, other: Any) -> bool: ...

    def __hash__(self) -> int: ...

    def __truediv__(self, name: Any) -> URL: ...

    def __mod__(self, query: _Query) -> URL: ...

    def is_absolute(self) -> bool: ...

    def is_default_port(self) -> bool: ...

    def origin(self) -> URL: ...

    def relative(self) -> URL: ...

    def with_scheme(self, scheme: str) -> URL: ...

    def with_user(self, user: Optional[str]) -> URL: ...

    def with_password(self, password: Optional[str]) -> URL: ...

    def with_host(self, host: str) -> URL: ...

    def with_port(self, port: Optional[int]) -> URL: ...

    def with_path(self, path: str, *, encoded: bool = ...) -> URL: ...

    @overload
    def with_query(self, query: _Query) -> URL: ...

    @overload
    def with_query(self, **kwargs: _QueryVariable) -> URL: ...

    @overload
    def update_query(self, query: _Query) -> URL: ...

    @overload
    def update_query(self, **kwargs: _QueryVariable) -> URL: ...

    def with_fragment(self, fragment: Optional[str]) -> URL: ...

    def with_name(self, name: str) -> URL: ...

    def with_suffix(self, suffix: str) -> URL: ...

    def join(self, url: URL) -> URL: ...

    def joinpath(self, *url: str, encoded: bool = ...) -> URL: ...

    def human_repr(self) -> str: ...

    # private API
    @classmethod
    def _normalize_path(cls, path: str) -> str: ...

    # fork:

    def get(
        self,
        params: Optional[Union[dict, list, bytes]] = None,
        # data: Optional[Union[dict, list, bytes]] = None,
        # json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        # files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        # new:
        session: requests.Session | None = None,
    ) -> requests.Response:
        ...

    def options(
        self,
        params: Optional[Union[dict, list, bytes]] = None,
        # data: Optional[Union[dict, list, bytes]] = None,
        # json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        # files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        # new:
        session: requests.Session | None = None,
    ) -> requests.Response: ...

    def head(
        self,
        params: Optional[Union[dict, list, bytes]] = None,
        # data: Optional[Union[dict, list, bytes]] = None,
        # json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        # files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        # new:
        session: requests.Session | None = None,
    ) -> requests.Response: ...

    def post(
        self,
        data: Optional[Union[dict, list, bytes]] = None,
        json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        params: Optional[Union[dict, list, bytes]] = None,
        # new:
        session: requests.Session | None = None,
    ) -> requests.Response: ...

    def put(
        self,
        data: Optional[Union[dict, list, bytes]] = None,
        json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        params: Optional[Union[dict, list, bytes]] = None,
        # new:
        session: requests.Session | None = None,
    ) -> requests.Response: ...

    def patch(
        self,
        data: Optional[Union[dict, list, bytes]] = None,
        json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        params: Optional[Union[dict, list, bytes]] = None,
        # new:
        session: requests.Session | None = None,
    ) -> requests.Response: ...

    def delete(
        self,
        params: Optional[Union[dict, list, bytes]] = None,
        # data: Optional[Union[dict, list, bytes]] = None,
        # json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        # files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        # new:
        session: requests.Session | None = None,
    ) -> requests.Response: ...

    _default_session: Optional[requests.Session]

    def __and__(self, other: requests.Session | None) -> URL: ...


@final
class cached_property:
    def __init__(self, wrapped: Any) -> None: ...

    def __get__(self, inst: URL, owner: Type[URL]) -> Any: ...

    def __set__(self, inst: URL, value: Any) -> None: ...


class CacheInfo(TypedDict):
    idna_encode: _CacheInfo
    idna_decode: _CacheInfo


def cache_clear() -> None: ...


def cache_info() -> CacheInfo: ...


def cache_configure(
    *, idna_encode_size: Optional[int] = ..., idna_decode_size: Optional[int] = ...
) -> None: ...
