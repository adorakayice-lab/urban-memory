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
        'jti': os.urandom(8).hex(),
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
        payload = verify_token(token)
        # Check token blacklist in app state (token -> expiry)
        try:
            bl = getattr(request.app.state, 'token_blacklist', {})
        except Exception:
            bl = {}
        if token in bl:
            # If the token is expired, remove from blacklist and continue
            now = int(time.time())
            expiry = bl.get(token)
            if expiry and expiry < now:
                try:
                    del request.app.state.token_blacklist[token]
                except Exception:
                    pass
            else:
                raise HTTPException(status_code=401, detail='Token revoked')
        # Check revoked subjects (global sign-out) stored in app state
        try:
            rs = getattr(request.app.state, 'revoked_subjects', {})
        except Exception:
            rs = {}
        sub = payload.get('sub')
        if sub and sub in rs:
            now = int(time.time())
            exp = rs.get(sub)
            if exp and exp < now:
                try:
                    del request.app.state.revoked_subjects[sub]
                except Exception:
                    pass
            else:
                raise HTTPException(status_code=401, detail='Subject revoked')
        return payload
    # Fallback to x-api-key dev flow
    key = request.headers.get('x-api-key')
    default = os.getenv('DEFAULT_API_KEY', 'dev-api-key')
    if key and key == default:
        # dev API key => admin role for backwards-compat
        return {'sub': 'dev-key', 'role': 'admin'}
    return None