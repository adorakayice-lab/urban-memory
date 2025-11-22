import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_logout_revokes_token():
    default = os.getenv('DEFAULT_API_KEY', 'dev-api-key')
    r = client.post('/auth/token', json={'api_key': default, 'role': 'user'})
    assert r.status_code == 200
    token = r.json()['token']

    # introspect to confirm token works
    r2 = client.get('/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200

    # logout
    r3 = client.post('/auth/logout', headers={'Authorization': f'Bearer {token}'})
    assert r3.status_code == 200
    assert r3.json().get('status') == 'revoked'

    # subsequent calls should be unauthorized
    r4 = client.get('/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert r4.status_code == 401
