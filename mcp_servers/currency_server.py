# MCP server exposing currency conversion via the Frankfurter API (no API key required)
from __future__ import annotations

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("currency-converter")

FRANKFURTER_URL = "https://api.frankfurter.app/latest"


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount from one currency to another using current exchange rates."""
    from_currency = from_currency.strip().upper()
    to_currency = to_currency.strip().upper()

    if amount <= 0:
        return {"error": "amount must be a positive number."}

    try:
        resp = requests.get(
            FRANKFURTER_URL,
            params={"amount": amount, "from": from_currency, "to": to_currency},
            timeout=15,
        )
        if resp.status_code == 404:
            return {"error": f"Unsupported currency code: '{from_currency}' or '{to_currency}'."}
        resp.raise_for_status()
        data = resp.json()
        converted = data["rates"].get(to_currency)
        if converted is None:
            return {"error": f"Could not get a rate for {to_currency}."}

        return {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "converted_amount": converted,
            "rate_date": data["date"],
            "source": "Frankfurter API (ECB reference rates, frankfurter.app)",
        }
    except requests.RequestException as exc:
        return {"error": f"Currency conversion service unavailable: {exc}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
