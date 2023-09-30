import pytest
from litestar import Litestar, get, post
from asgi_headers.core import InjectHeadersMiddlewareFactory
from litestar.testing import TestClient


@pytest.fixture
def app():
    @get("/foo", sync_to_thread=False)
    def foo_get() -> dict[str, str]:
        return {"foo": "get"}

    @post("/foo", sync_to_thread=False)
    def foo_post() -> dict[str, str]:
        return {"foo": "post"}

    @get("/foo/bar", sync_to_thread=False)
    def foo_bar_get() -> dict[str, str]:
        return {"foo": "bar"}

    @get("/bar", response_headers={"X-Already-Set": "2"}, sync_to_thread=False)
    def bar_get() -> dict[str, str]:
        return {"bar": "get"}

    _app = Litestar(
        middleware=[
            InjectHeadersMiddlewareFactory(
                injections={
                    ("*", "*"): {"X-Exists-In-All": "1"},
                    ("*", "/foo"): {"X-Exists-In-Foo": "1"},
                    ("GET", "*"): {"X-Exists-In-Get": "1"},
                    ("GET", "/foo"): {"X-Exists-In-Foo-Get": "1"},
                    ("POST", "/foo"): {"X-Exists-In-Foo-Post": "1"},
                    ("GET", "/foo/bar"): {"X-Exists-In-Foo-Bar": "1"},
                    ("GET", "/bar"): {"X-Already-Set": "1"},
                },
            ),
        ],
        route_handlers=[
            foo_get,
            foo_post,
            foo_bar_get,
            bar_get,
        ],
    )

    return _app


def test_foo_get(app):
    with TestClient(app) as client:
        response = client.get("/foo")

    assert response.status_code == 200
    assert response.json() == {"foo": "get"}
    assert response.headers["X-Exists-In-All"] == "1"
    assert response.headers["X-Exists-In-Foo"] == "1"
    assert response.headers["X-Exists-In-Get"] == "1"
    assert response.headers["X-Exists-In-Foo-Get"] == "1"
    assert "X-Exists-In-Foo-Post" not in response.headers
    assert "X-Exists-In-Foo-Bar" not in response.headers


def test_foo_post(app):
    with TestClient(app) as client:
        response = client.post("/foo")

    assert response.status_code == 201
    assert response.json() == {"foo": "post"}
    assert response.headers["X-Exists-In-All"] == "1"
    assert response.headers["X-Exists-In-Foo"] == "1"
    assert "X-Exists-In-Get" not in response.headers
    assert "X-Exists-In-Foo-Get" not in response.headers
    assert response.headers["X-Exists-In-Foo-Post"] == "1"
    assert "X-Exists-In-Foo-Bar" not in response.headers


def test_foo_bar_get(app):
    with TestClient(app) as client:
        response = client.get("/foo/bar")

    assert response.status_code == 200
    assert response.json() == {"foo": "bar"}
    assert response.headers["X-Exists-In-All"] == "1"
    assert response.headers["X-Exists-In-Foo"] == "1"
    assert response.headers["X-Exists-In-Get"] == "1"
    assert response.headers["X-Exists-In-Foo-Get"] == "1"
    assert "X-Exists-In-Foo-Post" not in response.headers
    assert response.headers["X-Exists-In-Foo-Bar"] == "1"


def test_bar_get(app):
    with TestClient(app) as client:
        response = client.get("/bar")

    assert response.status_code == 200
    assert response.json() == {"bar": "get"}
    assert response.headers["X-Exists-In-All"] == "1"
    assert "X-Exists-In-Foo" not in response.headers
    assert response.headers["X-Exists-In-Get"] == "1"
    assert "X-Exists-In-Foo-Get" not in response.headers
    assert "X-Exists-In-Foo-Post" not in response.headers
    assert "X-Exists-In-Foo-Bar" not in response.headers
    assert response.headers["X-Already-Set"] == "2, 1"
