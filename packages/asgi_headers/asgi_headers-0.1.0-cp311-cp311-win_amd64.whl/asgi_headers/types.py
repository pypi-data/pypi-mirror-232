from collections.abc import Awaitable, Callable
from typing import TypeAlias, Literal, cast

Scope: TypeAlias = dict
Receive: TypeAlias = Callable[[None], Awaitable[dict]]
Send: TypeAlias = Callable[[dict], Awaitable[None]]
ASGIApp: TypeAlias = Callable[[Scope, Receive, Send], Awaitable[None]]

Method: TypeAlias = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
Path: TypeAlias = str

Header: TypeAlias = str
HeaderValue: TypeAlias = str
Headers: TypeAlias = dict[Header, HeaderValue]

MatchAll: TypeAlias = Literal["*"]

MethodIdentifier: TypeAlias = tuple[Method | MatchAll, Path | MatchAll]
InjectionMap: TypeAlias = dict[MethodIdentifier, Headers]


class InjectionMapWrapper:
    __slots__ = (
        "_wildcard_methods",
        "_wildcard_paths",
        "_full_matches",
        "_full_wildcard",
    )

    def __init__(self, data: InjectionMap) -> None:
        self._wildcard_methods: dict[tuple[MatchAll, Path], Headers] = {}
        self._wildcard_paths: dict[tuple[Method, MatchAll], Headers] = {}
        self._full_matches: dict[tuple[Method, Path], Headers] = {}
        self._full_wildcard: Headers = {}

        for (method, path), value in data.items():
            if method == "*" and path == "*":
                self._full_wildcard = value
            elif method == "*":
                self._wildcard_methods[("*", path)] = value
            elif path == "*":
                self._wildcard_paths[(method, path)] = value
            else:
                self._full_matches[(method, path)] = value

    def __getitem__(self, key: MethodIdentifier) -> Headers:
        sought_method, sought_path = key
        sought_method = cast(Method, sought_method)

        headers: Headers = self._full_wildcard.copy()

        for (_, path_prefix), headers_to_set in self._wildcard_methods.items():
            if sought_path.startswith(path_prefix):
                headers.update(headers_to_set)

        if (sought_method, "*") in self._wildcard_paths:
            headers.update(self._wildcard_paths[(sought_method, "*")])

        for (method, path), headers_to_set in self._full_matches.items():
            if method == sought_method and sought_path.startswith(path):
                headers.update(headers_to_set)

        return headers
