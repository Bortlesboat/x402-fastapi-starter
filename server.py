"""Minimal FastAPI server with x402 payment-gated endpoints."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI

from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.middleware.fastapi import payment_middleware
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.server import x402ResourceServer

load_dotenv()

def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} is required; set it in .env before starting the server")
    return value


# --- Config ---
FACILITATOR_URL = required_env("FACILITATOR_URL")
PAY_TO = required_env("PAY_TO")
PRICE = os.getenv("PRICE", "$0.001")
NETWORK = os.getenv("NETWORK", "eip155:8453")

# --- x402 Setup ---
facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServer(facilitator)
server.register(NETWORK, ExactEvmServerScheme())

# Protected route config — only /api/premium requires payment
routes: dict[str, RouteConfig] = {
    "GET /api/premium": RouteConfig(
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=PAY_TO,
                price=PRICE,
                network=NETWORK,
            ),
        ],
        description="Premium content endpoint",
        mime_type="application/json",
    ),
}

# --- FastAPI App ---
app = FastAPI(title="x402 FastAPI Starter", version="0.2.0")

# Add x402 payment middleware (intercepts requests to protected routes)
app.middleware("http")(payment_middleware(routes, server))


@app.get("/api/hello")
async def hello():
    """Free endpoint — no payment required."""
    return {"message": "Hello from x402!"}


@app.get("/api/premium")
async def premium():
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
