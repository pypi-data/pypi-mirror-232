from asgi_headers.types import ASGIApp, Headers, InjectionMap, InjectionMapWrapper, Receive, Scope, Send


class InjectHeadersMiddleware:
    __slots__ = ("app", "injections")

    def __init__(self, app: ASGIApp, injections: InjectionMap) -> None:
        self.app = app
        self.injections = InjectionMapWrapper(injections)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        headers_to_set = self.injections[(method, path)]

        if not headers_to_set:
            await self.app(scope, receive, send)
            return

        await self.app(scope, receive, SendWrapper(send, headers_to_set))


class InjectHeadersMiddlewareFactory:
    __slots__ = ("injections",)

    def __init__(self, injections: InjectionMap) -> None:
        self.injections = injections

    def __call__(self, app: ASGIApp) -> InjectHeadersMiddleware:
        return InjectHeadersMiddleware(app, self.injections)


class SendWrapper:
    __slots__ = ("send", "headers_to_set")

    def __init__(self, send: Send, headers_to_set: Headers) -> None:
        self.send = send
        self.headers_to_set = headers_to_set

    async def __call__(self, scope: Scope) -> None:
        if scope["type"] != "http.response.start":
            await self.send(scope)
            return

        headers = scope["headers"]

        for header, value in self.headers_to_set.items():
            headers.append((header.encode(), value.encode()))

        await self.send(scope)
