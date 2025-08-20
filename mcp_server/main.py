#!/usr/bin/env python3
"""
File reader MCP server
"""
import asyncio
import json
from typing import Any

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from file_parsers import FileParserManager

server = Server("file-reader-mcp")
parser = FileParserManager()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_file",
            description="Read and parse file content - supports TXT, CSV, PDF, DOCX, XLSX, PPTX, JSON, images",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path"
                    },
                    "max_rows": {
                        "type": "integer",
                        "default": 1000,
                        "description": "Max rows for table files"
                    },
                    "max_pages": {
                        "type": "integer", 
                        "default": 10,
                        "description": "Max pages for PDF"
                    },
                    "max_chars": {
                        "type": "integer",
                        "default": 10000,
                        "description": "Max chars for text files"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Text encoding (auto-detect)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="get_formats",
            description="Get supported file formats",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "read_file":
            result = parser.parse_file(**arguments)
        elif name == "get_formats":
            result = {
                "success": True,
                "supported_extensions": parser.get_supported_extensions(),
                "total_formats": len(parser.get_supported_extensions())
            }
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}
        
        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({
            "success": False, "error": f"Tool execution failed: {str(e)}"
        }, ensure_ascii=False, indent=2))]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="file-reader-mcp",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())