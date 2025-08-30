#!/usr/bin/env python3
"""
Simple Test MCP Server for Syn OS
Basic MCP server to test the configuration
"""

import asyncio
import json
import logging
from mcp import stdio_server, Tool, McpError, ServerSession
from mcp.server import Server

# Create server instance
server = Server("syn-os-test-mcp")

@server.list_tools()
async def list_tools():
    """List available tools"""
    return [
        Tool(
            name="test_echo",
            description="Simple echo tool for testing MCP connectivity",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="syn_os_status",
            description="Get Syn OS MCP server status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls"""
    if name == "test_echo":
        message = arguments.get("message", "No message provided")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ Syn OS MCP Server Echo: {message}"
                }
            ]
        }
    elif name == "syn_os_status":
        return {
            "content": [
                {
                    "type": "text",
                    "text": "✅ Syn OS MCP Server Status: ONLINE\n🧠 Consciousness Integration: ACTIVE\n🔒 Security Level: MAXIMUM\n🚀 Performance: OPTIMAL"
                }
            ]
        }
    else:
        raise McpError(f"Unknown tool: {name}")

async def main():
    """Main server function"""
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())