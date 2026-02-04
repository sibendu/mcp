import asyncio
import os
from typing import Dict, List, Any, Optional
from datetime import timedelta

from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

class MCPClient:

    def __init__(self, server_url: Optional[str] = None):
        self.server_url = server_url or os.getenv('MCP_SERVER_URL', '')
        self.headers = None
        self.read, self.write, self.session_id = None, None, None
        self.session: Optional[ClientSession] = None
        self.tools = None
        self.OPENAI_TOOLS = None
        self.stack = AsyncExitStack()

    async def setup(self):

        try:
            
            # 1. Establish the transport connection
            transport = await self.stack.enter_async_context(
                streamablehttp_client(
                    self.server_url,
                    headers=self.headers,
                    timeout=timedelta(seconds=30),
                    sse_read_timeout=timedelta(seconds=300),
                    terminate_on_close=True,
                )
            )
            self.read, self.write, self.session_id = transport
            print(f"Connection established, Session ID: {self.session_id}")

            # 2. Create and initialize the MCP client session
            self.session = await self.stack.enter_async_context(ClientSession(self.read, self.write))
            await self.session.initialize()
            print("MCP session initialized")


            # 3. Use the session (e.g., list tools or call a tool)
            # Example: List available tools
            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools
            #print("\nAvailable Tools:", [tool.name for tool in self.tools])

            '''    
            for tool in self.tools:
                print(tool)
                print("*****************")
            '''
            
            self.OPENAI_TOOLS = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                } for tool in self.tools
            ]
            print(f"Listed available tools")
            #print(json.dumps(OPENAI_TOOLS, indent=2)) 


        except Exception as e:
            print(f"Failed to connect to the server: {e}")
            raise

    async def call_tool(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        if not self.session:
            raise RuntimeError("Session not initialized. Call setup() first.")
        
        result = await self.session.call_tool(tool_name, payload)
        #print(f"Tool Result: {result.content}")

        # MCP call_tool result contains complex objects that need to be properly extracted.
        # Extract the actual content from the result
        content_list = []
        for content_item in result.content:
            if hasattr(content_item, 'text'):
                # TextContent
                content_list.append({
                    "type": "text",
                    "text": content_item.text
                })
            elif hasattr(content_item, 'data'):
                # ImageContent or other data content
                content_list.append({
                    "type": getattr(content_item, 'type', 'unknown'),
                    "data": content_item.data
                })
            else:
                # Fallback - try to convert to dict
                content_list.append(str(content_item))
        
        # Create a serializable result
        serializable_result = {
            "content": content_list,
            "isError": getattr(result, 'isError', False)
        }

        return serializable_result

    async def cleanup(self):
        """Cleanup resources"""
        await self.stack.aclose()

async def execute(server_url: str):
    
    client = MCPClient(server_url)
    try:
        await client.setup()
        result = await client.call_tool("customer_get_by_email", {"email": "jane.smith@example.com"})
        print(result)
    finally:
        await client.cleanup()

if __name__ == "__main__":
    
    REMOTE_URL = "http://localhost:3000/mcp"

    asyncio.run(execute(REMOTE_URL))