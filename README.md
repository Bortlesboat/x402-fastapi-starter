# x402 FastAPI Starter

Minimal FastAPI server with x402 payment-gated endpoints using the [Satoshi Facilitator](https://github.com/Bortlesboat/x402-facilitator).

One free endpoint, one paid endpoint. Uses the official `x402` Python SDK middleware.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and edit your wallet address:

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
# Returns payment requirements in body
```

**Paid endpoint (with payment):**

An x402-compatible client handles the 402 flow automatically. The flow is:

1. Client requests `/api/premium`
2. Server returns `402` with payment requirements (facilitator URL, payTo address, price, network)
3. Client creates and signs a USDC payment via the facilitator
4. Client retries the request with the payment payload
5. Server verifies the payment via the facilitator and serves content

Use the [x402 Python client](https://pypi.org/project/x402/) or any x402-compatible HTTP client.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FACILITATOR_URL` | Satoshi Facilitator | x402 facilitator endpoint |
| `PAY_TO` | `0xe166...` | Your wallet address (receives USDC on Base) |
| `PRICE` | `$0.001` | Price per request |
| `NETWORK` | `eip155:8453` | Base mainnet |

## Resources

- [x402 Protocol](https://github.com/coinbase/x402)
- [x402 Python SDK](https://pypi.org/project/x402/)
- [Satoshi Facilitator](https://github.com/Bortlesboat/x402-facilitator)
