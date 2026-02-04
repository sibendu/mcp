"""
Customer API – MCP Server  (Streamable HTTP, port 3000)

Uses FastMCP's native streamable-http transport.  No manual Starlette
or SSE wiring – the SDK handles everything.

Usage:
    pip install -r requirements.txt
    python server.py                        # starts on http://localhost:3000/mcp

Claude Desktop config:
    {
      "mcpServers": {
        "customer-products-http": {
          "command": "npx",
          "args": ["mcp-remote", "http://localhost:3000/mcp"]
        }
      }
    }
"""

import json
import sys
import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Config  – adjust these two values to match your environment
# ---------------------------------------------------------------------------
CUSTOMER_API_URL = "http://localhost:8000"   # your Customer API base URL
MCP_PORT         = 3000                      # port this MCP server listens on
HTTPX_TIMEOUT    = 10.0                      # seconds

# ---------------------------------------------------------------------------
# Logging  – stderr only, never touches the HTTP stream
# ---------------------------------------------------------------------------
logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                    format="%(asctime)s [customer_mcp] %(levelname)s %(message)s")
logger = logging.getLogger("customer_mcp")

# ---------------------------------------------------------------------------
# Shared async HTTP client (created lazily, reused across calls)
# ---------------------------------------------------------------------------
_http: Optional[httpx.AsyncClient] = None

async def _get_http() -> httpx.AsyncClient:
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(base_url=CUSTOMER_API_URL, timeout=HTTPX_TIMEOUT)
    return _http

# ===========================================================================
# Formatting helpers
# ===========================================================================
def _fmt_customer(c: dict) -> str:
    return (
        f"- **ID:** {c['id']}\n"
        f"  **Name:** {c['name']}\n"
        f"  **Email:** {c['email']}\n"
        f"  **Date of Birth:** {c['dob']}"
    )

def _fmt_product(p: dict) -> str:
    warranty = (
        f"\n  **Warranty Expires:** {p.get('warranty_date', 'N/A')}"
        if p.get("has_warranty") else ""
    )
    return (
        f"- **Code:** {p['code']}  |  **Name:** {p['name']}\n"
        f"  **List Price:** ${p['list_price']:.2f}  |  "
        f"**Buy Price:** ${p['buy_price']:.2f}\n"
        f"  **Purchase Date:** {p['date']}\n"
        f"  **Has Warranty:** {'Yes' if p['has_warranty'] else 'No'}"
        f"{warranty}"
    )

def _api_error(e: Exception) -> str:
    """Translate any HTTP / network exception into a user-friendly string."""
    if isinstance(e, httpx.HTTPStatusError):
        s = e.response.status_code
        if s == 404:
            return "Error: Resource not found. Double-check the ID or email."
        if s == 422:
            try:
                return f"Error: Validation failed – {e.response.json().get('detail', [])}"
            except Exception:
                return "Error: Validation failed. Check your input parameters."
        if s == 429:
            return "Error: Rate limit hit. Please wait and retry."
        return f"Error: API returned status {s}."
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Try again shortly."
    if isinstance(e, httpx.ConnectError):
        return f"Error: Cannot connect to Customer API at {CUSTOMER_API_URL}. Is it running?"
    return f"Error: {type(e).__name__} – {e}"

# ===========================================================================
# FastMCP server instance
# ===========================================================================
mcp = FastMCP(
    name="customer_mcp",
    host="127.0.0.1",
    port=MCP_PORT,
)

# ===========================================================================
# Tool 1 – customer_get_by_email
# ===========================================================================
@mcp.tool()
async def customer_get_by_email(email: str, response_format: str = "markdown") -> str:
    """Look up a single customer by their email address.

    Returns the customer's id, name, email and date of birth.
    Use response_format='json' for machine-readable output.

    Args:
        email: Customer email address (e.g. jane@example.com)
        response_format: 'markdown' (default, human-readable) or 'json'
    """
    email = email.strip().lower()
    http = await _get_http()
    try:
        resp = await http.get("/customer", params={"email": email})
        resp.raise_for_status()
        customer = resp.json()
    except Exception as e:
        return _api_error(e)

    if response_format == "json":
        return json.dumps(customer, indent=2)
    return f"### Customer\n{_fmt_customer(customer)}"


# ===========================================================================
# Tool 2 – customer_list_all
# ===========================================================================
@mcp.tool()
async def customer_list_all(response_format: str = "markdown") -> str:
    """Retrieve every customer currently in the database.

    Args:
        response_format: 'markdown' (default, human-readable) or 'json'
    """
    http = await _get_http()
    try:
        resp = await http.get("/customers")
        resp.raise_for_status()
        customers: list[dict] = resp.json()
    except Exception as e:
        return _api_error(e)

    if response_format == "json":
        return json.dumps(customers, indent=2)
    if not customers:
        return "### All Customers\n_No customers found._"
    body = "\n\n".join(_fmt_customer(c) for c in customers)
    return f"### All Customers (total: {len(customers)})\n\n{body}"


# ===========================================================================
# Tool 3 – customer_get_products
# ===========================================================================
@mcp.tool()
async def customer_get_products(customer_id: int, response_format: str = "markdown") -> str:
    """Get all products purchased by a customer.

    IMPORTANT: This tool requires a numeric customer_id, NOT an email.
    If you only have an email address, call customer_get_by_email first
    to look up the customer and retrieve their numeric 'id' field, then
    pass that id here.

    Args:
        customer_id: Numeric customer ID (e.g. 42). Call customer_get_by_email first if you only have an email.
        response_format: 'markdown' (default, human-readable) or 'json'
    """
    if customer_id < 1:
        return "Error: customer_id must be a positive integer (>= 1)."

    http = await _get_http()
    try:
        resp = await http.get(f"/customer/{customer_id}/products")
        resp.raise_for_status()
        products: list[dict] = resp.json()
    except Exception as e:
        return _api_error(e)

    if response_format == "json":
        return json.dumps(products, indent=2)
    if not products:
        return f"### Products for Customer {customer_id}\n_No purchases recorded._"
    body = "\n\n".join(_fmt_product(p) for p in products)
    return f"### Products for Customer {customer_id} (total: {len(products)})\n\n{body}"


# ===========================================================================
# Entry point
# ===========================================================================
if __name__ == "__main__":
    logger.info("Starting customer_mcp on port %d → Customer API at %s", MCP_PORT, CUSTOMER_API_URL)
    mcp.run(transport="streamable-http")