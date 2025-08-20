# MCP File Reader Server

A lightweight MCP (Model Context Protocol) server for reading and parsing various document formats.

## Features

### Core Functionality
- Unified interface for multiple file formats
- Automatic parser selection based on file extension
- Configurable parameters (rows, pages, character limits)
- Comprehensive error handling

### Supported Formats

| Format Category | Extensions | Features |
|----------------|------------|----------|
| Text | `.txt`, `.md` | Encoding detection, word/line count |
| Data | `.csv` | Data preview, column info, statistics |
| Documents | `.pdf`, `.docx` | Text extraction, metadata, tables |

## Quick Start

### Installation
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Running the Server
```bash
# Direct execution
uv run python main.py

# Or using entry point
uv run file-reader-mcp
```

## MCP Client Configuration

### Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "file-reader": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/path/to/mcp_server"
    }
  }
}
```

### Cursor IDE
Create `mcp.json` in project root:
```json
{
  "file-reader": {
    "command": "uv",
    "args": ["run", "python", "main.py"],
    "cwd": "./mcp_server"
  }
}
```

## Available Tools

### read_file
Read and parse file content

Parameters:
- `file_path` (required): Path to the file
- `max_rows` (optional): Maximum rows for table files, default 1000
- `max_pages` (optional): Maximum pages for PDF files, default 10
- `max_chars` (optional): Maximum characters for text files, default 10000
- `encoding` (optional): Text encoding, auto-detected by default

### get_formats
Get list of supported file formats

Returns supported formats with descriptions

## Response Format

All parsing results include standard fields:
```json
{
  "success": true,
  "type": "file_type",
  "file_path": "path/to/file",
  "file_name": "filename",
  "file_size": 1234,
  "file_extension": ".ext",
  "data": {...}
}
```

## Project Structure

```
mcp_server/
├── main.py              # MCP server main program
├── file_parsers.py      # File parser modules
├── pyproject.toml       # Project configuration
└── README.md           # Documentation
```

## Design Principles

### Simple Architecture
- Single responsibility: focused on file reading
- Unified interface: one parser manager handles all formats
- Configurable: flexible parameter options

### Extensibility
- Easy to add new file format support
- Format-specific parsing parameters
- Consistent error handling

## Performance Features

- Memory control: automatic truncation for large files
- Encoding detection: automatic text encoding detection
- Error recovery: isolated failure handling
- Type safety: structured data returns

## License

MIT License

---

MCP (Model Context Protocol) is a standard protocol for connecting AI with external tools, enabling AI assistants to safely and efficiently access various data sources.