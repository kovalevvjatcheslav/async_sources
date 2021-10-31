from functools import partialmethod
import json

import httpx
import pytest

import service


@pytest.fixture
def client():
    with service.app.test_client() as client:
        yield client


class MockResponse:
    def __init__(self, source_name):
        self.source_name = source_name

    def json(self):
        with open(self.source_name, "rt") as source_file:
            data = json.load(source_file)
        return data


async def mock_get_source(self, url, timeout, expected_timeout=0, source_to_check=None):
    source_id = int(url.split("/")[-1])
    if source_id == source_to_check or expected_timeout >= timeout:
        raise httpx.ReadTimeout("test timeout")
    return MockResponse(f"sources/source{source_id}.json")


def test_all_successful(client, monkeypatch):
    monkeypatch.setattr("service.httpx.AsyncClient.get", mock_get_source)
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json == [{"id": i, "name": f"Test {i}"} for i in range(1, 61)]


def test_all_failed(client, monkeypatch):
    monkeypatch.setattr(
        "service.httpx.AsyncClient.get",
        partialmethod(mock_get_source, expected_timeout=3),
    )
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json == []


def test_first_failed(client, monkeypatch):
    monkeypatch.setattr(
        "service.httpx.AsyncClient.get",
        partialmethod(mock_get_source, source_to_check=1),
    )
    resp = client.get("/")
    assert resp.status_code == 200
    data = []
    for source_id in [2, 3]:
        with open(f"sources/source{source_id}.json", "rt") as source_file:
            data.extend(json.load(source_file))
    assert resp.json == sorted(data, key=lambda item: item["id"])
