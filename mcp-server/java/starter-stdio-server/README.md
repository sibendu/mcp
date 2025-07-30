# Spring AI MCP Weather STDIO Server

Refer - https://github.com/spring-projects/spring-ai-examples/tree/main/model-context-protocol/weather/starter-stdio-server

Provides two sample tools - getAllCustomers and getCustomer  


## For Claude Desktop

    "mcpstdioserver": {
      "command": "java",
      "args": [
	"-jar",
	"C:\\Temp\\mcp-stdio-server-0.1.jar"
      ]
    }

## Key Configuration Notes

### STDIO Mode Requirements

Disable web application type (spring.main.web-application-type=none)
Disable Spring banner (spring.main.banner-mode=off)
Clear console logging pattern (logging.pattern.console=)

### Server Type

SYNC (default): Uses McpSyncServer for straightforward request-response patterns
ASYNC: Uses McpAsyncServer for non-blocking operations with Project Reactor support



