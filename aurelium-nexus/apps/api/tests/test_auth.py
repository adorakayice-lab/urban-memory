import os
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_issue_token_with_default_key():
    default = os.getenv('DEFAULT_API_KEY', 'dev-api-key')
    r = client.post('/auth/token', json={'api_key': default, 'role': 'admin'})
    assert r.status_code == 200
    assert 'token' in r.json()


def test_use_jwt_to_call_protected():
    default = os.getenv('DEFAULT_API_KEY', 'dev-api-key')
    r = client.post('/auth/token', json={'api_key': default, 'role': 'admin'})
    token = r.json()['token']
    r2 = client.post('/tokenize', json={'asset_id':'a','amount':1}, headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200
    assert r2.json()['status'] == 'tokenized'
