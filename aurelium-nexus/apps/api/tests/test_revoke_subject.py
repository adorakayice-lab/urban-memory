import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_revoke_subject_by_admin():
    default = os.getenv('DEFAULT_API_KEY', 'dev-api-key')
    # issue a user token (subject=dev-user)
    r = client.post('/auth/token', json={'api_key': default, 'role': 'user'})
    assert r.status_code == 200
    user_token = r.json()['token']

    # issue an admin token
    r2 = client.post('/auth/token', json={'api_key': default, 'role': 'admin'})
    assert r2.status_code == 200
    admin_token = r2.json()['token']

    # admin revokes subject 'dev-user'
    r3 = client.post('/auth/revoke-subject', json={'subject': 'dev-user'}, headers={'Authorization': f'Bearer {admin_token}'})
    assert r3.status_code == 200

    # subsequent user token should be rejected
    r4 = client.get('/auth/me', headers={'Authorization': f'Bearer {user_token}'})
    assert r4.status_code == 401
