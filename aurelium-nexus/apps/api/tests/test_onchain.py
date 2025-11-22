import os
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_simulate_tx_without_provider():
    os.environ.pop('WEB3_PROVIDER_URL', None)
    r = client.post('/simulate-tx', json={'to':'0xabc','value':100}, headers={'x-api-key':'dev-api-key'})
    assert r.status_code == 200
    j = r.json()
    assert j.get('simulated') is True


def test_send_tx_requires_private_key(monkeypatch):
    # Ensure PRIVATE_KEY not set -> failure
    os.environ.pop('PRIVATE_KEY', None)
    r = client.post('/send-tx', json={'to':'0xabc','value':1}, headers={'x-api-key':'dev-api-key'})
    assert r.status_code == 400
