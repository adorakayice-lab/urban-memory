import os
import time
import jwt
from fastapi import HTTPException, Request
from typing import Optional

SECRET = os.getenv('JWT_SECRET', 'dev-jwt-secret')
ALGO = 'HS256'


def create_token(subject: str, role: str = 'user', expires_in: int = 3600) -> str:
    now = int(time.time())
    payload = {
        'sub': subject,
        'role': role,
        'iat': now,
        'exp': now + expires_in,
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')


def get_auth_payload_from_request(request: Request) -> Optional[dict]:
    # Prefer Authorization Bearer
    auth = request.headers.get('authorization')
    if auth and auth.lower().startswith('bearer '):
        token = auth.split(None, 1)[1].strip()
        return verify_token(token)
    # Fallback to x-api-key dev flow
    key = request.headers.get('x-api-key')
    default = os.getenv('DEFAULT_API_KEY', 'dev-api-key')
    if key and key == default:
        # dev API key => admin role for backwards-compat
        return {'sub': 'dev-key', 'role': 'admin'}
    return None