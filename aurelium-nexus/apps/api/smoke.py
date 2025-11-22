from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
headers = {"x-api-key": "dev-api-key"}

def call(path, method='get', json=None, params=None, hdrs=None):
    h = headers.copy()
    if hdrs:
        h.update(hdrs)
    if method == 'get':
        r = client.get(path, headers=h, params=params)
    else:
        r = client.post(path, headers=h, json=json)
    print(f'-> {method.upper()} {path} (status={r.status_code})')
    try:
        print(r.json())
    except Exception:
        print(r.text)

def run_all():
    call('/health')
    call('/bridge')
    call('/nft-check', params={'address': '0xabcdef'})
    call('/tokenize', method='post', json={'asset_id': 'asset-xyz', 'amount': 10})
    call('/transfer', method='post', json={'token_address': '0xdead', 'to': '0xbeef', 'amount': 1.2})

if __name__ == '__main__':
    run_all()
