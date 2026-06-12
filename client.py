import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import OpenAI
from dotenv import load_dotenv
import time
import os
import json
import re

load_dotenv()

# NVIDIA Nemotron client
nemotron = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

NEMOTRON_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1.5"

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

async def _call_tool(tool_name: str, arguments: dict):
    async with sse_client("http://127.0.0.1:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text

async def _get_tools():
    async with sse_client("http://127.0.0.1:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                }
                for tool in tools.tools
            ]

def call_tool(tool_name: str, arguments: dict):
    return run_async(_call_tool(tool_name, arguments))

def get_tools():
    return run_async(_get_tools())

def parse_text_tool_call(content: str):
    """Detect if the model returned a tool call as text instead of function call"""
    try:
        data = json.loads(content)
        if "type" in data and data["type"] == "function":
            return data["name"], data.get("parameters", {})
    except:
        pass
    return None, None

def chat_with_nemotron(messages: list):
    print("1. Getting tools...")
    tools = get_tools()
    print("2. Got tools, calling Nemotron...")

    for attempt in range(5):
        try:
            response = nemotron.chat.completions.create(
            model=NEMOTRON_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
            )
            print("3. Got Nemotron response!")
            print("4. Message content:", response.choices[0].message.content)
            print("5. Tool calls:", response.choices[0].message.tool_calls)
            break
        except Exception as e:
            if "429" in str(e):
                wait = (attempt + 1) * 15
                print(f"Rate limit hit, waiting 10 seconds... (attempt {attempt + 1})")
                time.sleep(10)
            else:
                raise e

    if response is None:
        return type('obj', (object,), {'content': 'Sorry I am currently rate limited. Please try again in a minute.', 'tool_calls': None})(), None

    message = response.choices[0].message
    
    if message.tool_calls:
        tool_results = []
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = call_tool(tool_name, arguments)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "tool_name": tool_name,
                "result": result
            })
        return message, tool_results
    
    if message.content:
        tool_name, arguments = parse_text_tool_call(message.content)
        if tool_name:
            print(f"Text-based tool call detected: {tool_name}")
            result = call_tool(tool_name, arguments)
            print(f"Tool result: {result}")
            return message, [{
                "tool_call_id": "text_tool_call",
                "tool_name": tool_name,
                "result": result
            }]
    
    return message, None