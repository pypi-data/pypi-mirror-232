import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from asgi_headers.core import InjectHeadersMiddleware


@pytest.fixture
def app():
    _app = FastAPI()

    _app.add_middleware(
        InjectHeadersMiddleware,
        injections={
            ("*", "*"): {
                "X-Exists-In-All": "1",
            },
            ("*", "/foo"): {
                "X-Exists-In-Foo": "1",
            },
            ("GET", "*"): {
                "X-Exists-In-Get": "1",
            },
            ("GET", "/foo"): {
                "X-Exists-In-Foo-Get": "1",
            },
            ("POST", "/foo"): {
                "X-Exists-In-Foo-Post": "1",
            },
            ("GET", "/foo/bar"): {
                "X-Exists-In-Foo-Bar": "1",
            },
            ("GET", "/bar"): {
                "X-Already-Set": "1",
            },
        },
    )

    @_app.get("/foo")
    def foo_get():
        return {"foo": "get"}

    @_app.post("/foo")
    def foo_post():
        return {"foo": "post"}

    @_app.get("/foo/bar")
    def foo_bar_get():
        return {"foo": "bar"}

    @_app.get("/bar")
    def bar_get(response: Response):
        response.headers["X-Already-Set"] = "2"
        return {"bar": "get"}

    return _app


def test_foo_get(app):
    client = TestClient(app)

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
    client = TestClient(app)

    response = client.post("/foo")

    assert response.status_code == 200
    assert response.json() == {"foo": "post"}
    assert response.headers["X-Exists-In-All"] == "1"
    assert response.headers["X-Exists-In-Foo"] == "1"
    assert "X-Exists-In-Get" not in response.headers
    assert "X-Exists-In-Foo-Get" not in response.headers
    assert response.headers["X-Exists-In-Foo-Post"] == "1"
    assert "X-Exists-In-Foo-Bar" not in response.headers


def test_foo_bar_get(app):
    client = TestClient(app)

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
    client = TestClient(app)

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
