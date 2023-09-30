# asgi_headers

Simple middleware for injecting headers in ASGI apps.

## Installation

The library is available on PyPI:

```shell
pip install asgi_headers
```

Or in the `Releases` tab, both in `sdist` format as well as `wheels`.

## Supported Python versions

Currently the library supports Python 3.11 only.

## Example usage:

### With FastAPI
```python
from fastapi import FastAPI
from asgi_headers import InjectHeadersMiddleware

app = FastAPI()
app.add_middleware(
    InjectHeadersMiddleware,
    injections={
        ("GET", "/hello"): {"This-Header-Will-Be-Injected-To-All-GET-Requests-Starting-With-/foo-path": 1},
        ("*", "/hello", "This-Header-Will-Be-Injected-To-All-Requests-Starting-With-/foo-path", "1")
        ("GET", "*", "This-Header-Will-Be-Injected-To-All-GET-Requests", "1")
        ("*", "*", "This-Header-Will-Be-Injected-To-All-Requests", "1")
    }
)

@app.get("/hello")
def hello_world():
    return {"hello": "world"}
```

### With Litestar

```python
from litestar import Litestar
from asgi_headers import InjectHeadersMiddlewareFactory

@get(path="/", media_type="application/json", sync_to_thread=False)
def hello_world() -> dict[str, str]:
    return {"hello": "world"}

app = Litestar(
    route_handlers=[hello_world],
    middleware=[
        InjectHeadersMiddlewareFactory(
            injections={
                ("GET", "/hello"): {"This-Header-Will-Be-Injected-To-All-GET-Requests-Starting-With-/foo-path": 1},
                ("*", "/hello", "This-Header-Will-Be-Injected-To-All-Requests-Starting-With-/foo-path", "1")
                ("GET", "*", "This-Header-Will-Be-Injected-To-All-GET-Requests", "1")
                ("*", "*", "This-Header-Will-Be-Injected-To-All-Requests", "1")
            }
        ),
    ]
)
```
