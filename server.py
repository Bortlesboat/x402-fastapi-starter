"""Minimal FastAPI server with x402 payment-gated endpoints."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request

from x402 import x402ResourceServer
from x402.http import FacilitatorConfig, HTTPFacilitatorClient
from x402.http.middleware.fastapi import PaymentMiddlewareASGI, payment_middleware
from x402.mechanisms.evm.exact import ExactEvmServerScheme

load_dotenv()

# --- Config ---
FACILITATOR_URL = os.getenv(
    "FACILITATOR_URL",
    "https://x402-facilitator.happysmoke-e4fd0a77.eastus.azurecontainerapps.io",
)
PAY_TO = os.getenv("PAY_TO", "0xe166267c3648b5ca4419f2c58faed8cd4df87d54")
PRICE = os.getenv("PRICE", "$0.001")
NETWORK = os.getenv("NETWORK", "eip155:8453")

# --- x402 Setup ---
facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServer(facilitator)
server.register("eip155:*", ExactEvmServerScheme())

# Protected route config — only /api/premium requires payment
routes = {
    "GET /api/premium": {
        "accepts": {
            "scheme": "exact",
            "payTo": PAY_TO,
            "price": PRICE,
            "network": NETWORK,
        },
        "description": "Premium content endpoint",
    },
}

# --- FastAPI App ---
app = FastAPI(title="x402 FastAPI Starter", version="0.1.0")

# Add x402 payment middleware (intercepts requests to protected routes)
app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)


@app.get("/api/hello")
async def hello():
    """Free endpoint — no payment required."""
    return {"message": "Hello from x402!"}


@app.get("/api/premium")
async def premium(request: Request):
    """Paid endpoint — requires x402 payment (0.001 USDC on Base)."""
    return {
        "message": "You have accessed premium content!",
        "data": {
            "secret": "The answer is 42.",
            "tip": "x402 makes micropayments simple.",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=4021, reload=True)
