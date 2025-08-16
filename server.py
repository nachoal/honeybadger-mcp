#!/usr/bin/env python3
"""
Honeybadger MCP Server

This MCP server provides tools to interact with the Honeybadger API,
focusing on retrieving and managing projects and their exceptions (faults).
"""

import os
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
mcp = FastMCP("Honeybadger API")

# Configuration
HONEYBADGER_API_TOKEN = os.getenv("HONEYBADGER_API_TOKEN")
HONEYBADGER_BASE_URL = "https://app.honeybadger.io/v2"

if not HONEYBADGER_API_TOKEN:
    print("WARNING: HONEYBADGER_API_TOKEN not found in environment variables.")
    print("Please set it in your .env file or environment variables.")


@dataclass
class HoneybadgerConfig:
    """Configuration for Honeybadger API access."""
    api_token: str
    base_url: str = HONEYBADGER_BASE_URL


@mcp.resource("honeybadger://config")
def get_config() -> HoneybadgerConfig:
    """Get the current Honeybadger configuration."""
    return HoneybadgerConfig(
        api_token="[REDACTED]" if HONEYBADGER_API_TOKEN else "Not configured",
        base_url=HONEYBADGER_BASE_URL,
    )


def _make_request(endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, 
                 data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make a request to the Honeybadger API.
    
    Args:
        endpoint: API endpoint to call
        method: HTTP method (GET, POST, PUT, DELETE)
        params: Query parameters
        data: Request body for POST/PUT requests
        
    Returns:
        API response as a dictionary
    """
    if not HONEYBADGER_API_TOKEN:
        return {
            "error": "Honeybadger API token is not configured. Please set HONEYBADGER_API_TOKEN in your .env file."
        }
    
    url = f"{HONEYBADGER_BASE_URL}/{endpoint}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    
    # Using HTTP Basic Authentication with token as username and empty password
    # This is equivalent to curl -u AUTH_TOKEN: format
    auth = (HONEYBADGER_API_TOKEN, "")
    
    try:
        print(f"Making {method} request to {url}")
        print(f"Auth: Using token of length {len(HONEYBADGER_API_TOKEN)} characters")
        
        if method == "GET":
            response = requests.get(url, auth=auth, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, auth=auth, headers=headers, params=params, json=data)
        elif method == "PUT":
            response = requests.put(url, auth=auth, headers=headers, params=params, json=data)
        elif method == "DELETE":
            response = requests.delete(url, auth=auth, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"Error response: {response.text}")
        
        response.raise_for_status()
        
        if response.status_code == 204:  # No content
            return {"status": "success"}
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {str(e)}")
        return {"error": str(e)}


# Project Management Tools

@mcp.tool()
def get_projects(account_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get a list of all projects in your Honeybadger account.
    
    Args:
        account_id: Optional ID of the account to filter projects by
        
    Returns:
        List of projects
    """
    params = {}
    if account_id:
        params["account_id"] = account_id
        
    response = _make_request("projects", params=params)
    return response


@mcp.tool()
def get_project(project_id: int) -> Dict[str, Any]:
    """
    Get details for a specific project.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Project details including:
        - name: Project name
        - token: API token
        - environments: List of environments
        - users: List of users with access
        - teams: List of teams with access
        - fault_count: Total number of faults
        - unresolved_fault_count: Number of unresolved faults
    """
    response = _make_request(f"projects/{project_id}")
    return response


@mcp.tool()
def create_project(name: str, account_id: Optional[int] = None, 
                  resolve_errors_on_deploy: Optional[bool] = None,
                  disable_public_links: Optional[bool] = None,
                  language: Optional[str] = None,
                  user_url: Optional[str] = None,
                  source_url: Optional[str] = None,
                  purge_days: Optional[int] = None,
                  user_search_field: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new project in your Honeybadger account.
    
    Args:
        name: Name of the project
        account_id: Optional ID of the account to create the project in
        resolve_errors_on_deploy: Whether to resolve errors on deploy
        disable_public_links: Whether to disable public links
        language: Programming language (js, elixir, golang, java, node, php, python, ruby, other)
        user_url: URL format for user links
        source_url: URL format for source code links
        purge_days: Number of days to retain data
        user_search_field: Field to use for user search
        
    Returns:
        Created project details
    """
    data = {"project": {"name": name}}
    
    if resolve_errors_on_deploy is not None:
        data["project"]["resolve_errors_on_deploy"] = resolve_errors_on_deploy
    if disable_public_links is not None:
        data["project"]["disable_public_links"] = disable_public_links
    if language:
        data["project"]["language"] = language
    if user_url:
        data["project"]["user_url"] = user_url
    if source_url:
        data["project"]["source_url"] = source_url
    if purge_days is not None:
        data["project"]["purge_days"] = purge_days
    if user_search_field:
        data["project"]["user_search_field"] = user_search_field
        
    params = {}
    if account_id:
        params["account_id"] = account_id
        
    response = _make_request("projects", method="POST", params=params, data=data)
    return response


@mcp.tool()
def update_project(project_id: int, name: Optional[str] = None,
                  resolve_errors_on_deploy: Optional[bool] = None,
                  disable_public_links: Optional[bool] = None,
                  language: Optional[str] = None,
                  user_url: Optional[str] = None,
                  source_url: Optional[str] = None,
                  purge_days: Optional[int] = None,
                  user_search_field: Optional[str] = None) -> Dict[str, Any]:
    """
    Update an existing project in your Honeybadger account.
    
    Args:
        project_id: ID of the project to update
        name: New name for the project
        resolve_errors_on_deploy: Whether to resolve errors on deploy
        disable_public_links: Whether to disable public links
        language: Programming language (js, elixir, golang, java, node, php, python, ruby, other)
        user_url: URL format for user links
        source_url: URL format for source code links
        purge_days: Number of days to retain data
        user_search_field: Field to use for user search
        
    Returns:
        Updated project details
    """
    data = {"project": {}}
    
    if name:
        data["project"]["name"] = name
    if resolve_errors_on_deploy is not None:
        data["project"]["resolve_errors_on_deploy"] = resolve_errors_on_deploy
    if disable_public_links is not None:
        data["project"]["disable_public_links"] = disable_public_links
    if language:
        data["project"]["language"] = language
    if user_url:
        data["project"]["user_url"] = user_url
    if source_url:
        data["project"]["source_url"] = source_url
    if purge_days is not None:
        data["project"]["purge_days"] = purge_days
    if user_search_field:
        data["project"]["user_search_field"] = user_search_field
        
    response = _make_request(f"projects/{project_id}", method="PUT", data=data)
    return response


@mcp.tool()
def delete_project(project_id: int) -> Dict[str, str]:
    """
    Delete a project from your Honeybadger account.
    
    Args:
        project_id: ID of the project to delete
        
    Returns:
        Status message
    """
    response = _make_request(f"projects/{project_id}", method="DELETE")
    return response


@mcp.tool()
def get_project_occurrences(project_id: Optional[int] = None, 
                           period: Optional[str] = "hour",
                           environment: Optional[str] = None) -> List[List[Union[int, float]]]:
    """
    Get occurrence data for a project or all projects over time.
    
    Args:
        project_id: Optional ID of the project (if None, returns data for all projects)
        period: Time period ("hour", "day", "week", or "month")
        environment: Optional environment to filter by
        
    Returns:
        Time series data of error occurrences
    """
    params = {}
    if period:
        params["period"] = period
    if environment:
        params["environment"] = environment
        
    endpoint = "projects/occurrences" if project_id is None else f"projects/{project_id}/occurrences"
    response = _make_request(endpoint, params=params)
    return response


# Fault Management Tools

@mcp.tool()
def get_faults(project_id: int, query: Optional[str] = None, 
              limit: Optional[int] = 25, order: Optional[str] = "recent") -> List[Dict[str, Any]]:
    """
    Get a list of faults (exceptions) for a project.
    
    Args:
        project_id: The ID of the project
        query: Optional search query (e.g., "environment:production -is:resolved")
        limit: Maximum number of results to return (default: 25)
        order: Sort order ("recent" or "frequent")
        
    Returns:
        List of faults
    """
    params = {}
    if query:
        params["q"] = query
    if limit:
        params["limit"] = limit
    if order:
        params["order"] = order
        
    response = _make_request(f"projects/{project_id}/faults", params=params)
    return response


@mcp.tool()
def get_fault_details(project_id: int, fault_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific fault.
    
    Args:
        project_id: The ID of the project
        fault_id: The ID of the fault
        
    Returns:
        Fault details
    """
    response = _make_request(f"projects/{project_id}/faults/{fault_id}")
    return response


@mcp.tool()
def get_fault_summary(project_id: int, query: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a summary of faults for a project, including counts by environment and status.
    
    Args:
        project_id: The ID of the project
        query: Optional search query
        
    Returns:
        Fault summary statistics
    """
    params = {}
    if query:
        params["q"] = query
        
    response = _make_request(f"projects/{project_id}/faults/summary", params=params)
    return response


@mcp.tool()
def update_fault(project_id: int, fault_id: int, 
                resolved: Optional[bool] = None, 
                ignored: Optional[bool] = None,
                assignee_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Update a fault's status.
    
    Args:
        project_id: The ID of the project
        fault_id: The ID of the fault
        resolved: Set to True to mark as resolved, False to mark as unresolved
        ignored: Set to True to ignore the fault, False to unignore
        assignee_id: ID of the user to assign the fault to
        
    Returns:
        Updated fault details
    """
    data = {"fault": {}}
    
    if resolved is not None:
        data["fault"]["resolved"] = resolved
    if ignored is not None:
        data["fault"]["ignored"] = ignored
    if assignee_id is not None:
        data["fault"]["assignee_id"] = assignee_id
        
    response = _make_request(
        f"projects/{project_id}/faults/{fault_id}", 
        method="PUT", 
        data=data
    )
    return response


@mcp.tool()
def delete_fault(project_id: int, fault_id: int) -> Dict[str, str]:
    """
    Delete a fault.
    
    Args:
        project_id: The ID of the project
        fault_id: The ID of the fault
        
    Returns:
        Status message
    """
    response = _make_request(
        f"projects/{project_id}/faults/{fault_id}", 
        method="DELETE"
    )
    return response


@mcp.tool()
def get_fault_occurrences(project_id: int, fault_id: int, 
                         period: Optional[str] = "day") -> List[List[Union[int, float]]]:
    """
    Get occurrence data for a fault over time.
    
    Args:
        project_id: The ID of the project
        fault_id: The ID of the fault
        period: Time period ("hour", "day", "week", or "month")
        
    Returns:
        Time series data of fault occurrences
    """
    params = {}
    if period:
        params["period"] = period
        
    response = _make_request(
        f"projects/{project_id}/faults/{fault_id}/occurrences", 
        params=params
    )
    return response


@mcp.tool()
def get_fault_notices(
    project_id: int,
    fault_id: int,
    created_after: Optional[int] = None,
    created_before: Optional[int] = None,
    limit: Optional[int] = 25,
) -> List[Dict[str, Any]]:
    """
    Get a list of notices for the given fault.

    Args:
        project_id: The ID of the project
        fault_id: The ID of the fault
        created_after: Unix timestamp (seconds since epoch) to filter notices created after this time
        created_before: Unix timestamp (seconds since epoch) to filter notices created before this time
        limit: Number of results to return (max and default are 25)

    Returns:
        List of notices ordered by creation time descending
    """
    params: Dict[str, Any] = {}
    if created_after is not None:
        params["created_after"] = created_after
    if created_before is not None:
        params["created_before"] = created_before
    if limit:
        params["limit"] = limit

    response = _make_request(
        f"projects/{project_id}/faults/{fault_id}/notices",
        params=params,
    )
    return response


@mcp.tool()
def pause_fault_notifications(project_id: int, fault_id: int, 
                            time: Optional[str] = None, 
                            count: Optional[int] = None) -> Dict[str, str]:
    """
    Pause notifications for a fault.
    
    Args:
        project_id: The ID of the project
        fault_id: The ID of the fault
        time: Time period to pause ("hour", "day", or "week")
        count: Number of occurrences to pause for (10, 100, or 1000)
        
    Returns:
        Status message
    """
    data = {}
    if time:
        data["time"] = time
    elif count:
        data["count"] = count
    else:
        return {"error": "Either time or count must be specified"}
        
    response = _make_request(
        f"projects/{project_id}/faults/{fault_id}/pause", 
        method="POST", 
        data=data
    )
    return response


@mcp.tool()
def unpause_fault_notifications(project_id: int, fault_id: int) -> Dict[str, str]:
    """
    Unpause notifications for a fault.
    
    Args:
        project_id: The ID of the project
        fault_id: The ID of the fault
        
    Returns:
        Status message
    """
    response = _make_request(
        f"projects/{project_id}/faults/{fault_id}/unpause", 
        method="POST"
    )
    return response


@mcp.tool()
def bulk_resolve_faults(project_id: int, query: Optional[str] = None) -> Dict[str, str]:
    """
    Mark all faults for a project as resolved.
    
    Args:
        project_id: The ID of the project
        query: Optional search query to filter which faults to resolve
        
    Returns:
        Status message
    """
    params = {}
    if query:
        params["q"] = query
        
    response = _make_request(
        f"projects/{project_id}/faults/resolve", 
        method="POST",
        params=params
    )
    return response


if __name__ == "__main__":
    # Run the server
    mcp.run() 