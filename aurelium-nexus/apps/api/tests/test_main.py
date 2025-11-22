from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

DEFAULT_HEADERS = {"x-api-key": "dev-api-key"}

def test_root():
    r = client.get('/')
    assert r.status_code == 200
    assert r.json().get('service') == 'aurelium-nexus api'

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'

def test_nft_check_requires_auth():
    r = client.get('/nft-check?address=0xabc')
    assert r.status_code == 401

def test_nft_check_with_key():
    r = client.get('/nft-check?address=0xabc', headers=DEFAULT_HEADERS)
    assert r.status_code == 200
    assert 'owns' in r.json()

def test_tokenize_and_transfer():
    payload = {"asset_id":"asset-123","amount":42}
    r = client.post('/tokenize', json=payload, headers=DEFAULT_HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'tokenized'
    token = data['token_address']

    r2 = client.post('/transfer', json={"token_address": token, "to": "0xdeadbeef", "amount": 1.2}, headers=DEFAULT_HEADERS)
    assert r2.status_code == 200
    assert 'tx_hash' in r2.json()
