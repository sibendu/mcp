# MCP Server Setup Guide - HTTP Mode

This project shows how to  
- set up the MCP server that calls the FastAPI endpoints via HTTP
- MCP clients calling the tools exposed by MCP server via Streamable HTTP

# Architecture

```
Claude Desktop → MCP Server (mcp_server_http.py) → HTTP Requests → FastAPI Server (api.py)
```

```
mcp_client.py → MCP Server (mcp_server_http.py) → HTTP Requests → FastAPI Server (api.py)
```

A client sample that orchestrator multiple tool calls using LLM (Azure OpenAI) 
```
mcp_orchestrator.py → mcp_client.py → MCP Server (mcp_server_http.py) → HTTP Requests → FastAPI Server (api.py)
```

# Prerequisites

1. Python 3.12+
2. Claude Desktop installed
3. All dependencies installed

# Run MCP Server

## Installation Steps

## Step 1: Install Dependencies

use uv:
```bash
uv sync
```

## Step 2: Run the Mock APIs (FastAPI Server)

```bash
python api.py
```

The API server will run on `http://localhost:8000`

Docs: `http://localhost:8000/docs`

### Customer Endpoint

```bash
curl "http://localhost:8000/customer?email=john.doe@example.com"
```

### Products Endpoint

```bash
curl http://localhost:8000/customer/1/products
```


## Step 3: Run the MCP Server 

```bash
python mcp_server_http.py
```

This will run API server will run on `http://localhost:8000`

At this point, we can test using the Postman collection and responses from MCP Server

# Test with MCP Clients

## 1: Test with Claude Desktop

1. Add the following configuration in claude_desktop_config.json 

```json
{
  "mcpServers": {
    "customer-products-http": {
	"command": "npx",
      	"args": [
            "mcp-remote",
            "http://localhost:3000/mcp"
      	]
    }
  }
}
```

After restarting Claude Desktop, try these prompts:

1. "Get customer information for jane.smith@example.com"
2. "Show me all products for customer ID 2"
3. "What products did john.doe@example.com purchase?"

## 2. Test using MCP client program

```bash
python mcp_client.py
```

## 3. Test Orchestration using MCP

```bash
python mcp_orchestrator.py
```

# Appendix

## Available MCP Tools

Once configured, the MCP server exposed following tools:

### 1. get_customer_by_email

Get customer information by email address.

**Input:**
- `email` (string, required): Customer's email address

**Example usage in Claude Desktop:**
```
Can you get the customer information for john.doe@example.com?
```

**Returns:**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "name": "John Doe",
  "dob": "1990-05-15"
}
```

### 2. get_customer_products

Get all products purchased by a customer.

**Input:**
- `customer_id` (integer, required): The customer's ID

**Example usage in Claude Desktop:**
```
Show me all products purchased by customer ID 1
```

**Returns:**
```json
[
  {
    "code": "LAP001",
    "name": "Dell XPS 15 Laptop",
    "list_price": 1899.99,
    "buy_price": 1699.99,
    "date": "2024-01-15",
    "has_warranty": true,
    "warranty_date": "2027-01-15"
  },
  ...
]
```

## Troubleshooting

### MCP Server Can't Connect to API

**Error:** "Cannot connect to API server"

**Solution:**
- Ensure the Mock APIs (FastAPI server) is running on port 8000
- Check if another application is using port 8000
- Verify the URL in `server_http.py` matches your API server

### Claude Desktop Doesn't Show Tools

**Solution:**
1. Check the config file syntax is valid JSON
2. Verify the paths in the config are correct and use double backslashes on Windows
3. Restart Claude Desktop completely
4. Check Claude Desktop logs for errors

## Next Steps

- Modify `api.py` to connect to a real database
- Add authentication to the API endpoints
- Add more tools/endpoints as needed
- Deploy the FastAPI server to a production environment
