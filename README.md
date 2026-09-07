# x402 FastAPI Starter

Minimal FastAPI server with x402 payment-gated endpoints through your configured facilitator.

One free endpoint, one paid endpoint. Uses the official `x402` Python SDK middleware and EVM dependencies. Requires Python 3.10 or newer.

## Setup

`FACILITATOR_URL` and `PAY_TO` are required. Set an operating x402 facilitator that supports your chosen network and your own receiving wallet. Missing, empty, or whitespace-only values stop startup with a named configuration error. Surrounding whitespace is trimmed.

The previously advertised Satoshi Facilitator is paused. These templates no longer default to it or to an example recipient.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set both `FACILITATOR_URL` and `PAY_TO`:

```bash
cp .env.example .env
```

## Run

```bash
python server.py
# or
uvicorn server:app --host 0.0.0.0 --port 4021 --reload
```

## Endpoints

| Endpoint | Price | Description |
|----------|-------|-------------|
| `GET /api/hello` | Free | Returns a greeting |
| `GET /api/premium` | 0.001 USDC | Returns premium content (x402 payment required) |

## Usage

**Free endpoint:**

```bash
curl http://localhost:4021/api/hello
# {"message":"Hello from x402!"}
```

**Paid endpoint (no payment):**

```bash
curl -i http://localhost:4021/api/premium
# HTTP/1.1 402 Payment Required
# PAYMENT-REQUIRED header contains base64-encoded payment requirements
```

**Paid endpoint (with payment):**

An x402 v2 client reads the `PAYMENT-REQUIRED` header, signs a payment authorization, and retries with `PAYMENT-SIGNATURE`. The middleware verifies and settles through the configured facilitator before returning a successful paid response. Use the [x402 Python client](https://pypi.org/project/x402/) to handle this flow.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FACILITATOR_URL` | Required, no default | Operating x402 facilitator endpoint |
| `PAY_TO` | Required, no default | Your receiving wallet address |
| `PRICE` | `$0.001` | Price per request |
| `NETWORK` | `eip155:8453` | Base mainnet |

## Tests

The tests use a local facilitator fixture and a dummy recipient. They verify configuration errors, the free 200 response, and an unpaid 402 response containing the configured recipient, amount, and network. They do not sign, verify, or settle a payment.

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Resources

- [x402 Protocol](https://github.com/coinbase/x402)
- [x402 Python SDK](https://pypi.org/project/x402/)
- [Satoshi Facilitator source (hosted service paused)](https://github.com/Bortlesboat/x402-facilitator)
