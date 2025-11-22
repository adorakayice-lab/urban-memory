import os
import json
import requests
import pytest

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class DummyResp:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError('err')

    def json(self):
        return self._data


def test_ai_proxy(monkeypatch):
    # Ensure provider logic is called and endpoint returns PROXIED when key present
    os.environ['AI_API_KEY'] = 'fake-key'
    os.environ['AI_PROVIDER'] = 'openai'

    def fake_post(url, json=None, headers=None, timeout=None):
        return DummyResp({'choices': [{'message': {'content': 'OK from fake provider'}}]})

    monkeypatch.setattr('requests.post', fake_post)

    r = client.post('/ai', json={'prompt': 'Test prompt'}, headers={'x-api-key': 'dev-api-key'})
    assert r.status_code == 200
    body = r.json()
    assert body['action'] == 'PROXIED'
    assert 'OK from fake provider' in body.get('details', '')
