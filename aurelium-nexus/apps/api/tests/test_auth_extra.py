import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_auth_me_and_refresh_flow():
    default = os.getenv('DEFAULT_API_KEY', 'dev-api-key')
    r = client.post('/auth/token', json={'api_key': default, 'role': 'user'})
    assert r.status_code == 200
    token = r.json()['token']

    # introspect
    r2 = client.get('/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200
    assert r2.json()['role'] == 'user'

    # refresh
    r3 = client.post('/auth/refresh', headers={'Authorization': f'Bearer {token}'})
    assert r3.status_code == 200
    assert 'token' in r3.json()
