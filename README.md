# Sentinel MCP Server

A Python-based MCP server using FastMCP library that provides integration with Microsoft Sentinel using Azure Identity Authentication.

## Overview

This project implements an MCP server that enables:

- Running KQL queries against Microsoft Sentinel
- Listing All Sentinel Tables
- Fetching a specific Senteinl Table for metadata
- Fetching specific Sentinel Table schema

The server acts as a bridge between development environments and Microsoft Sentinel, allowing for testing and execution of KQL queries. It can be built for SSE or STDIO based on the launch flag within the FastMCP configuration.

## Features

- **Sentinel Integration**: Execute KQL queries against your Sentinel workspace
- **Authentication Support**: Multiple authentication methods including interactive browser, client secret, and managed identity

## Prerequisites

- Python 3.8+
- Microsoft Sentinel workspace
- Appropriate Azure permissions for Sentinel

## Installation

### Option 1: Install from source (development mode)

1. Clone the repository:
   ```
   git clone https://github.com/gallis-local/SentinelMCPServer.git
   cd SentinelMCPServer
   ```

2. Install the package in development mode:
   ```
   pip install -e .
   ```

## Usage

### Starting the Server

After installation, run the MCP server using the command:

```
sentinel_mcp
```

You can also run directly from the repository:

```
python -m sentinel_mcp
```


### Available Tools

The MCP server provides the following tools:

1. **sentinel_run_query**: Execute KQL queries in Sentinel
2. **sentinel_get_tables**: List all available tables in your Sentinel workspace
3. **sentinel_get_table_schema**: Fetch the schema for a specific Sentinel table
4. **sentinel_get_table_by_name**: Get information for a specific table by name

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
