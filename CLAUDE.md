# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An MCP (Model Context Protocol) server that provides tools to interact with the Honeybadger error monitoring API. Built with Python using the FastMCP framework.

## Commands

```bash
# Install dependencies
uv sync

# Run the MCP server
python server.py

# Test API functions directly
./test_server.py projects                              # List all projects
./test_server.py project 12345                         # Get project details
./test_server.py faults 12345 --query "environment:production -is:resolved"
./test_server.py fault-notices 12345 67890 --limit 10  # Get notices for a fault
./test_server.py update-fault 12345 67890 --resolved true
```

## Architecture

Single-file MCP server (`server.py`) using FastMCP:
- `_make_request()` - Central HTTP handler using Basic Auth with `requests` library
- `@mcp.tool()` decorated functions expose Honeybadger API endpoints as MCP tools
- `@mcp.resource()` provides configuration resource

The server requires `HONEYBADGER_API_TOKEN` in a `.env` file (personal access token, not project API key).

## API Tool Categories

**Project Management**: `get_projects`, `get_project`, `create_project`, `update_project`, `delete_project`, `get_project_occurrences`

**Fault Management**: `get_faults`, `get_fault_details`, `get_fault_summary`, `update_fault`, `delete_fault`, `get_fault_occurrences`, `get_fault_notices`, `pause_fault_notifications`, `unpause_fault_notifications`, `bulk_resolve_faults`

## Claude Code Integration

```bash
claude mcp add honeybadger -s user -- ~/.cargo/bin/uv --directory ~/code/mcp-servers/honeybadger-mcp run server.py
```
