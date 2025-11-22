from fastapi import FastAPI, Body, Request, HTTPException, Depends, Response
from pydantic import BaseModel
import os
import logging
from typing import Optional
from ai_provider import send_to_provider
from auth import create_token, get_auth_payload_from_request, verify_token
import json

# Basic structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('aurelium.api')

app = FastAPI(title="Aurelium Nexus API (minimal)")


def require_auth_or_api_key(request: Request):
    payload = get_auth_payload_from_request(request)
    if not payload:
        logger.warning('Unauthorized request, missing/invalid credentials')
        raise HTTPException(status_code=401, detail='Unauthorized')
    return payload


def require_role(role: str):
    def _inner(request: Request):
        payload = get_auth_payload_from_request(request)
        if not payload:
            raise HTTPException(status_code=401, detail='Unauthorized')
        # Support passing a comma-separated list or a single role string
        allowed = [r.strip() for r in role.split(',')] if isinstance(role, str) and ',' in role else [role]
        if payload.get('role') not in allowed:
            raise HTTPException(status_code=403, detail='Forbidden')
        return payload
    return _inner


class AIRequest(BaseModel):
    prompt: str


@app.get('/')
async def root():
    return {"status": "ok", "service": "aurelium-nexus api"}


@app.post('/ai')
async def ai_command(req: AIRequest, authorized: dict = Depends(require_auth_or_api_key)):
    prompt = req.prompt
    api_key = os.getenv('AI_API_KEY')
    logger.info('AI request received')
    if api_key:
        try:
            res = send_to_provider(prompt)
            return {"action": "PROXIED", "provider": res.get('provider'), "details": res.get('text'), "raw": res.get('raw')}
        except Exception as e:
            logger.exception('AI provider error')
            raise HTTPException(status_code=502, detail=str(e))
    action = f"RECEIVED: {prompt}"
    return {"action": "EXECUTED", "details": action}


@app.get('/nft-check')
async def nft_check(address: str, authorized: dict = Depends(require_auth_or_api_key)):
    """Check NFT ownership for `address`.

    Behavior:
    - If `ALCHEMY_API_KEY` env var is provided, call Alchemy `getNFTs` for the owner and
      optionally filter by `ALCHEMY_NFT_CONTRACTS` (comma-separated list).
    - Otherwise fall back to a deterministic mock used in dev.
    """
    if not address:
        raise HTTPException(status_code=400, detail='address required')

    # Simple in-memory cache: address -> (owns_bool, expiry_unix, source)
    cache_ttl = int(os.getenv('NFT_CHECK_TTL', '60'))
    now = __import__('time').time()
    if not hasattr(app.state, 'nft_cache'):
        app.state.nft_cache = {}

    cached = app.state.nft_cache.get(address)
    # If Alchemy is configured, prefer a live Alchemy check over a cached fallback result
    alchemy_key = os.getenv('ALCHEMY_API_KEY')
    if cached and cached[1] > now:
        # cached is (owns, expiry, source)
        owns = cached[0]
        source = cached[2] if len(cached) > 2 else 'cache'
        # If Alchemy is configured but cache is from a non-alchemy source, bypass.
        # Conversely, if Alchemy is NOT configured but cache is from an 'alchemy' result,
        # bypass so we don't return stale alchemy results when env has changed.
        if (alchemy_key and source != 'alchemy') or (not alchemy_key and source == 'alchemy'):
            logger.info('nft-check cache bypass due to env/source mismatch (source=%s, alchemy_key_present=%s)', source, bool(alchemy_key))
        else:
            logger.info('nft-check cache hit %s -> %s (source=%s)', address, owns, source)
            return {"address": address, "owns": owns, "cached": True, "source": source}

    alchemy_network = os.getenv('ALCHEMY_NETWORK', 'eth-mainnet')
    contracts = os.getenv('ALCHEMY_NFT_CONTRACTS')

    if alchemy_key:
        try:
            base = f'https://{alchemy_network}.g.alchemy.com/nft/v2/{alchemy_key}'
            url = f'{base}/getNFTs?owner={address}'
            logger.info('nft-check calling alchemy %s', url)
            import requests

            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            total = data.get('totalCount') or len(data.get('ownedNfts', []))
            owns = False
            if contracts:
                want = {c.strip().lower() for c in contracts.split(',') if c.strip()}
                for nft in data.get('ownedNfts', []):
                    try:
                        addr0 = nft.get('contract', {}).get('address', '').lower()
                        if addr0 in want:
                            owns = True
                            break
                    except Exception:
                        continue
            else:
                owns = total > 0

            # cache (include source for later cache hits)
            app.state.nft_cache[address] = (owns, now + cache_ttl, 'alchemy')
            logger.info('nft-check alchemy result %s -> %s (total=%s)', address, owns, total)
            return {"address": address, "owns": owns, "source": "alchemy", "total": total}
        except Exception as e:
            logger.exception('alchemy nft-check failed')
            # fall through to deterministic fallback

    # Deterministic fallback (dev): treat any address ending with an even hex digit as owning
    last = address.strip()[-1].lower()
    owns = last in '02468ace'
    app.state.nft_cache[address] = (owns, now + cache_ttl, 'fallback')
    logger.info('nft-check fallback %s -> %s', address, owns)
    return {"address": address, "owns": owns, "source": "fallback"}


@app.get('/bridge')
async def bridge_info(authorized: dict = Depends(require_auth_or_api_key)):
    # Return mocked cross-chain link data used by the visualizer
    logger.info('bridge info requested')
    return {
        "links": [
            {"from": "Ethereum", "to": "Solana", "volume": 124000000},
            {"from": "Ethereum", "to": "Arbitrum", "volume": 54000000},
            {"from": "Base", "to": "Avalanche", "volume": 23000000}
        ]
    }


@app.post('/tokenize')
async def tokenize(asset_id: str = Body(...), amount: float = Body(...), authorized: dict = Depends(require_role('admin'))):
    # Mock tokenization endpoint — returns a fake token contract address and status
    logger.info('tokenize asset=%s amount=%s', asset_id, amount)
    token_address = '0x' + os.urandom(8).hex()
    return {"status": "tokenized", "token_address": token_address, "asset_id": asset_id, "amount": amount}


@app.post('/transfer')
async def transfer(token_address: str = Body(...), to: str = Body(...), amount: float = Body(...), authorized: dict = Depends(require_role('admin'))):
    # Mock transfer — in production this would call web3/ethers provider
    logger.info('transfer token=%s to=%s amount=%s', token_address, to, amount)
    tx_hash = '0x' + os.urandom(12).hex()
    return {"status": "submitted", "tx_hash": tx_hash}


@app.post('/simulate-tx')
async def simulate_tx(payload: dict = Body(...), authorized: dict = Depends(require_auth_or_api_key)):
    from onchain import simulate_transaction

    to = payload.get('to')
    value = int(payload.get('value', 0))
    data = payload.get('data')
    from_addr = payload.get('from')
    res = simulate_transaction(to=to, value=value, data=data, from_addr=from_addr)
    return res


@app.post('/send-tx')
async def send_tx(payload: dict = Body(...), authorized: dict = Depends(require_role('admin'))):
    from onchain import send_transaction

    to = payload.get('to')
    value = int(payload.get('value', 0))
    data = payload.get('data')
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        raise HTTPException(status_code=400, detail='PRIVATE_KEY not configured for sending transactions')
    try:
        res = send_transaction(to=to, value=value, data=data, private_key=private_key)
        return res
    except Exception as e:
        logger.exception('send tx failed')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/estimate-gas')
async def estimate_gas(payload: dict = Body(...), authorized: dict = Depends(require_auth_or_api_key)):
    from onchain import get_web3

    w3 = get_web3()
    if not w3:
        raise HTTPException(status_code=400, detail='WEB3_PROVIDER_URL not configured')
    tx = payload.get('tx')
    try:
        gas = w3.eth.estimate_gas(tx)
        return {'gas': gas}
    except Exception as e:
        logger.exception('estimate gas failed')
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/metrics')
async def metrics(authorized: dict = Depends(require_auth_or_api_key)):
    # Minimal prometheus-style metrics stub
    metrics_text = "# HELP api_requests_total Total API requests (mock)\n# TYPE api_requests_total counter\napi_requests_total 42\n"
    return Response(content=metrics_text, media_type='text/plain')


@app.get('/onchain/info')
async def onchain_info(authorized: dict = Depends(require_auth_or_api_key)):
    """Return information about the configured on-chain provider (if any).

    This endpoint is useful for diagnostics in environments where provider
    configuration may be optional (dev vs prod).
    """
    from onchain import get_provider_info

    info = get_provider_info()
    # Do not expose private keys; only report that a private key is present
    private_key_set = bool(os.getenv('PRIVATE_KEY'))
    info['private_key_present'] = private_key_set
    return info


@app.post('/auth/token')
async def auth_token(request: Request):
    # issue a short-lived JWT when DEFAULT_API_KEY is provided in header or body
    key_header = request.headers.get('x-api-key')
    default = os.getenv('DEFAULT_API_KEY', 'dev-api-key')
    body = await request.json()
    key_body = body.get('api_key') if isinstance(body, dict) else None
    if key_header == default or key_body == default:
        role = body.get('role', 'user') if isinstance(body, dict) else 'user'
        token = create_token(subject='dev-user', role=role, expires_in=3600)
        return {'token': token}
    raise HTTPException(status_code=401, detail='Unauthorized')


@app.get('/auth/me')
async def auth_me(request: Request):
    """Return the decoded auth payload for the current request (introspection)."""
    payload = get_auth_payload_from_request(request)
    if not payload:
        raise HTTPException(status_code=401, detail='Unauthorized')
    # do not return full JWT internals; return safe fields only
    return {'sub': payload.get('sub'), 'role': payload.get('role')}


@app.post('/auth/refresh')
async def auth_refresh(request: Request):
    """Refresh a valid JWT by issuing a new token with the same subject and role."""
    payload = get_auth_payload_from_request(request)
    if not payload:
        raise HTTPException(status_code=401, detail='Unauthorized')
    # Issue a new token with a fresh expiry
    token = create_token(subject=payload.get('sub'), role=payload.get('role'), expires_in=3600)
    return {'token': token}


@app.post('/auth/logout')
async def auth_logout(request: Request):
    """Revoke the provided Bearer token immediately.

    The token string is added to an in-memory blacklist until its natural expiry.
    """
    auth = request.headers.get('authorization')
    if not auth or not auth.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='Authorization Bearer token required')
    token = auth.split(None, 1)[1].strip()
    # validate token first
    payload = verify_token(token)
    exp = payload.get('exp', int(__import__('time').time()))
    if not hasattr(app.state, 'token_blacklist'):
        app.state.token_blacklist = {}
    # cleanup expired entries
    now = int(__import__('time').time())
    for t, e in list(app.state.token_blacklist.items()):
        if e < now:
            try:
                del app.state.token_blacklist[t]
            except Exception:
                pass
    app.state.token_blacklist[token] = exp
    return {'status': 'revoked'}


@app.post('/auth/revoke-subject')
async def auth_revoke_subject(body: dict = Body(...), authorized: dict = Depends(require_role('admin'))):
    """Revoke all tokens for a given subject (admin-only).

    Body: {"subject": "dev-user"}
    """
    subject = body.get('subject') if isinstance(body, dict) else None
    if not subject:
        raise HTTPException(status_code=400, detail='subject required')
    if not hasattr(app.state, 'revoked_subjects'):
        app.state.revoked_subjects = {}
    now = int(__import__('time').time())
    # Revoke for a long period (1 year) or until explicit removal
    app.state.revoked_subjects[subject] = now + 365 * 24 * 3600
    # Also add any currently-blacklisted tokens for the subject (best-effort)
    try:
        bl = getattr(app.state, 'token_blacklist', {})
        for t in list(bl.keys()):
            try:
                # decode without verification to inspect subject safely
                import jwt as _jwt
                payload = _jwt.decode(t, options={"verify_signature": False})
                if payload.get('sub') == subject:
                    # keep existing expiry
                    app.state.token_blacklist[t] = bl.get(t, now)
            except Exception:
                continue
    except Exception:
        pass
    return {'status': 'revoked', 'subject': subject}


@app.get('/health')
async def health():
    return {"status": "ok"}
