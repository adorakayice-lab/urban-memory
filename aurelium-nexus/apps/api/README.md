# Aurelium Nexus API — On-chain / Provider Notes

This small document describes the on-chain configuration used by the API and
how to run the test suite locally.

Required (for real on-chain operations)

- `WEB3_PROVIDER_URL` — URL of an Ethereum-compatible JSON-RPC provider (e.g. Alchemy, Infura).
- `PRIVATE_KEY` — Hex private key used for signing transactions (only required for sending real transactions).

Behavior when env vars are missing

- If `WEB3_PROVIDER_URL` is not set, the API will run but on-chain endpoints
  will simulate transactions and return deterministic placeholder responses.
- `web3` (the Python library) is imported lazily; the API will continue to work
  without it for dev/testing flows. To enable full on-chain features, install
  `web3` and set `WEB3_PROVIDER_URL`.

Useful endpoints

- `GET /onchain/info` — Returns provider availability and `chain_id` (if available).
- `POST /simulate-tx` — Simulates a transaction (works without `web3`).
- `POST /send-tx` — Sends a signed transaction (requires `WEB3_PROVIDER_URL` and `PRIVATE_KEY`).

Run tests

From `apps/api` run:

```bash
python -m pip install -r requirements.txt
pytest -q
```

If you do not want to install `web3` for the test environment, the tests are
written to exercise the simulated code paths and will pass without `web3`.
