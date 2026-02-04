import asyncio
from typing import Dict, List  
import json, os  
from dotenv import load_dotenv
from mcp_client import MCPClient  
from openai import AzureOpenAI        

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv('AZURE_OPENAI_API_VERSION', "2024-08-01-preview"),
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)
DEPLOYMENT = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")   # deployment name, NOT model-name  

'''  
def _dispatch(mcp_client: MCPClient, name: str, args: Dict):  
    #print(f"Dispatching tool call: {name} with args: {args}")
    if name == "customer_get_by_email":  
        return mcp_client.call_tool("customer_get_by_email", {"email": args["email"]})  
    if name == "customer_get_products":  
        return mcp_client.call_tool("customer_get_products", {"customer_id": args["customer_id"]})  
    raise ValueError(f"Unknown tool: {name}")  
'''  
  
# Helper funciton  
async def fetch_user_and_products(REMOTE_MCP_URL, email, max_rounds=5) -> Dict:  

    mcp_client = MCPClient(REMOTE_MCP_URL)  
    await mcp_client.setup()

    query = f"I need customer and product details for {email}. Fetch following details - customer name, id, date of birth, email and products"

    messages = [{"role": "user", "content": query}]  
    user_rec, product_rec = None, None  

    #print("Available Tools:")
    #print(mcp_client.OPENAI_TOOLS)
  
    for _ in range(max_rounds):  
        resp = client.chat.completions.create(  
            model      = DEPLOYMENT,       
            messages   = messages,  
            tools      = mcp_client.OPENAI_TOOLS,   
            tool_choice= "auto",  
        )  
  
        assistant_msg = resp.choices[0].message  
        print(f"LLM Message {assistant_msg}")

        messages.append(assistant_msg)     # keep context  
  
        # a) The model wants to call a tool  
        if assistant_msg.tool_calls:  
            for call in assistant_msg.tool_calls:  
                name      = call.function.name  
                arguments = json.loads(call.function.arguments)  

                #print(f"Model wants to call tool: {name} with arguments: {arguments}")
                
                #result  = _dispatch(mcp_client, name, arguments)  
                result  = await mcp_client.call_tool(name, arguments)  
                #print(f"Tool {name} Result: {result}")
                
                #print(f"Result: {json.dumps(result)}")

                if name == "customer_get_by_email":   user_rec     = result  
                if name == "customer_get_products":   product_rec  = result  

                messages.append(  
                    {  
                        "role":         "tool",  
                        "tool_call_id": call.id,  
                        "content": json.dumps(result),  
                    }  
                )  
            continue    # let model think again with new info
        
        else: 
            ## No further tool calls → final answer
            break    

    await mcp_client.cleanup()

    # b) No further tool calls → final answer  
    return {  
        "assistant_answer": assistant_msg.content,  
        "user_record":      user_rec,  
        "products":         product_rec,  
    }  
  
    #raise RuntimeError("Exceeded maximum tool-calling turns.")  
  
  

if __name__ == "__main__":  
    
    REMOTE_MCP_URL = "http://localhost:3000/mcp"
    email  = "jane.smith@example.com"

    res = asyncio.run(fetch_user_and_products(REMOTE_MCP_URL, email)) 
    print("**************************************")  
    #print(json.dumps(res, indent=2)) 
    print(res['assistant_answer'])
    print("**************************************")  
    