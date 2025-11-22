import os
import json
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
            raise Exception('http')

    def json(self):
        return self._data


def test_nft_check_alchemy(monkeypatch):
    os.environ['ALCHEMY_API_KEY'] = 'fake-key'
    os.environ['ALCHEMY_NETWORK'] = 'eth-mainnet'

    def fake_get(url, timeout=None):
        # Return a response that mimics Alchemy's getNFTs
        return DummyResp({
            'ownedNfts': [
                {'contract': {'address': '0xabc123'}, 'id': {'tokenId': '1'}}
            ],
            'totalCount': 1,
        })

    monkeypatch.setattr('requests.get', fake_get)
    r = client.get('/nft-check?address=0xabc', headers={'x-api-key': 'dev-api-key'})
    assert r.status_code == 200
    j = r.json()
    assert j.get('source') == 'alchemy'
    assert j.get('owns') is True


def test_nft_check_fallback(monkeypatch):
    # Ensure env not set -> fallback
    os.environ.pop('ALCHEMY_API_KEY', None)
    r = client.get('/nft-check?address=0xabc', headers={'x-api-key': 'dev-api-key'})
    assert r.status_code == 200
    j = r.json()
    assert j.get('source') in ('fallback', None)
