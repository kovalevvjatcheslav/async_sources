from functools import partial

import pytest

import service


@pytest.fixture
def client():
    with service.app.test_client() as client:
        yield client


def mock_randint(a, b, real):
    return real


def test_all_successful(client, monkeypatch):
    monkeypatch.setattr("service.randint", partial(mock_randint, real=1))
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.json == [{"id": i, "name": f"Test {i}"} for i in range(1, 61)]


def test_all_failed(client, monkeypatch):
    monkeypatch.setattr("service.randint", partial(mock_randint, real=2))
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.json == []
