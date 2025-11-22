import os
import logging

logger = logging.getLogger('aurelium.onchain')


def get_web3():
    # Import web3 lazily so the API can run in environments without the package
    try:
        from web3 import Web3, HTTPProvider
    except Exception:
        return None
    url = os.getenv('WEB3_PROVIDER_URL')
    if not url:
        return None
    return Web3(HTTPProvider(url))


def get_provider_info():
    """Return a small dict describing the configured provider (or lack thereof).

    This is safe to call in environments without `web3` installed; it will
    return `{'available': False}` in that case.
    """
    url = os.getenv('WEB3_PROVIDER_URL')
    if not url:
        return {'available': False, 'reason': 'no_provider_url'}
    try:
        from web3 import Web3, HTTPProvider
    except Exception:
        return {'available': False, 'reason': 'web3_missing'}
    try:
        w3 = Web3(HTTPProvider(url))
        chain_id = None
        try:
            chain_id = w3.eth.chain_id
        except Exception:
            chain_id = None
        return {'available': True, 'provider_url': url, 'chain_id': chain_id}
    except Exception as e:
        logger.exception('provider info error')
        return {'available': False, 'reason': str(e)}


def simulate_transaction(to: str, value: int = 0, data: str | None = None, from_addr: str | None = None):
    w3 = get_web3()
    tx = {
        'to': to,
        'value': int(value),
        'data': data or '0x',
    }
    if from_addr:
        tx['from'] = from_addr

    if not w3:
        # return a simulated raw tx structure
        return {'simulated': True, 'tx': tx}

    # Build transaction fields: nonce, gasPrice, gas estimation
    if 'from' not in tx and from_addr:
        tx['from'] = from_addr

    try:
        tx_est = tx.copy()
        # Remove `data` if empty to avoid estimates problems
        tx_est['data'] = tx_est.get('data', '0x')
        gas = w3.eth.estimate_gas(tx_est)
        chain_id = w3.eth.chain_id
        return {'simulated': False, 'tx': tx, 'gas_estimate': gas, 'chain_id': chain_id}
    except Exception as e:
        logger.exception('simulate tx failed')
        return {'simulated': True, 'tx': tx, 'error': str(e)}


def send_transaction(to: str, value: int = 0, data: str | None = None, private_key: str | None = None, from_addr: str | None = None):
    w3 = get_web3()
    if not w3 or not private_key:
        raise RuntimeError('WEB3_PROVIDER_URL and PRIVATE_KEY must be set to send transactions')

    acct = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = {
        'to': to,
        'value': int(value),
        'data': data or '0x',
        'nonce': nonce,
        'chainId': w3.eth.chain_id,
    }
    # Estimate gas
    try:
        gas = w3.eth.estimate_gas({'to': to, 'from': acct.address, 'value': int(value), 'data': data or '0x'})
        tx['gas'] = gas
    except Exception:
        tx['gas'] = 210000

    # gasPrice / max fees
    try:
        tx['gasPrice'] = w3.eth.gas_price
    except Exception:
        tx['gasPrice'] = None

    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return {'tx_hash': tx_hash.hex(), 'signed': True}
