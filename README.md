# Honeybadger MCP Server

An MCP server that provides tools to interact with the Honeybadger API, focusing on retrieving and managing projects and their exceptions (faults).

## Features

- Project management (list, create, update, delete)
- Fault (exception) management
- View fault details and occurrences
- Update fault status (resolve, ignore, assign)
- Pause and unpause fault notifications

## Installation

1. Make sure you have Python 3.12+ installed
2. Install dependencies:

```bash
uv add honeybadger mcp python-dotenv requests
```

3. Configure your Honeybadger API token in the `.env` file:

```
HONEYBADGER_API_TOKEN=your_api_token_here
```

### API Token Requirements

The Honeybadger API token must:

- Be a valid personal access token (not a project API key)
- Have the necessary permissions to access the Data API
- Be associated with an active account

You can find or create your personal access token in the Honeybadger dashboard under your user settings. For more information, see the [Honeybadger API Documentation](https://docs.honeybadger.io/api/).

## Usage

### Running the Server

```bash
python server.py
```

### Using with Claude Desktop

To use this server with Claude Desktop:

```bash
mcp install server.py
```

### Using with MCP Inspector

For development and testing:

```bash
mcp dev server.py
```

### Testing API Functions Directly

You can test the API functions directly using the included test_server.py script:

```bash
# Make the script executable
chmod +x test_server.py

# Show help information
./test_server.py --help

# List all projects
./test_server.py projects

# Get details for a specific project
./test_server.py project 12345

# List faults for a project
./test_server.py faults 12345 --query "environment:production -is:resolved"

# Update a fault
./test_server.py update-fault 12345 67890 --resolved true
```

### Troubleshooting

If you encounter a 403 Forbidden error when using the API:

1. Verify that your API token is correct and has not expired
2. Ensure you're using a personal access token, not a project API key
3. Check that your account has the necessary permissions
4. Confirm that your account is active and in good standing

For more detailed error information, run the test_server.py script, which will display the full error response.

## API Tools

The server provides the following tools:

### Project Management

- `get_projects(account_id)` - List all projects, optionally filtered by account
- `get_project(project_id)` - Get details for a specific project
- `create_project(name, ...)` - Create a new project
- `update_project(project_id, ...)` - Update an existing project
- `delete_project(project_id)` - Delete a project
- `get_project_occurrences(project_id, period, environment)` - Get occurrence data for a project

### Fault Management

- `get_faults(project_id, query, limit, order)` - List faults for a project
- `get_fault_details(project_id, fault_id)` - Get details for a specific fault
- `get_fault_summary(project_id, query)` - Get fault summary statistics
- `update_fault(project_id, fault_id, resolved, ignored, assignee_id)` - Update a fault's status
- `delete_fault(project_id, fault_id)` - Delete a fault
- `get_fault_occurrences(project_id, fault_id, period)` - Get occurrence data over time
- `pause_fault_notifications(project_id, fault_id, time, count)` - Pause notifications
- `unpause_fault_notifications(project_id, fault_id)` - Unpause notifications
- `bulk_resolve_faults(project_id, query)` - Resolve multiple faults at once

## Example Usage

Here's an example of how to use this server with Claude:

```
I want to check the status of exceptions in my Honeybadger project.

Let me list all my projects.

[Claude uses get_projects to list your projects]

I want to see all unresolved exceptions in the production environment for project ID 12345.

[Claude uses get_faults with query="environment:production -is:resolved" to list faults]

Let me get more details about fault ID 67890.

[Claude uses get_fault_details to show fault details]

I'll mark this fault as resolved.

[Claude uses update_fault to resolve the fault]
```

## License

MIT
