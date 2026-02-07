#!/usr/bin/env python3
# test_server.py
import os
import json
import argparse
from dotenv import load_dotenv
from server import (
    get_projects, get_project, create_project, update_project, delete_project,
    get_project_occurrences, get_faults, get_fault_details, get_fault_summary,
    update_fault, delete_fault, get_fault_occurrences, pause_fault_notifications,
    unpause_fault_notifications, bulk_resolve_faults, get_fault_notices, get_notice
)

# Load environment variables from .env file
load_dotenv()

def pretty_print(data):
    """Print data in a readable format"""
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2))
    else:
        print(data)

def main():
    parser = argparse.ArgumentParser(description="Test the Honeybadger MCP server")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Check if HONEYBADGER_API_TOKEN is set
    if not os.environ.get("HONEYBADGER_API_TOKEN"):
        print("Error: HONEYBADGER_API_TOKEN environment variable is not set")
        print("Please set it in your .env file with HONEYBADGER_API_TOKEN=your-api-token-here")
        return 1
    
    # Project commands
    projects_parser = subparsers.add_parser("projects", help="List all projects")
    projects_parser.add_argument("--account-id", type=int, help="Filter by account ID")
    
    project_parser = subparsers.add_parser("project", help="Get project details")
    project_parser.add_argument("project_id", type=int, help="Project ID")
    
    create_project_parser = subparsers.add_parser("create-project", help="Create a new project")
    create_project_parser.add_argument("name", help="Project name")
    create_project_parser.add_argument("--account-id", type=int, help="Account ID")
    create_project_parser.add_argument("--language", choices=["js", "elixir", "golang", "java", "node", "php", "python", "ruby", "other"], help="Project language")
    
    update_project_parser = subparsers.add_parser("update-project", help="Update a project")
    update_project_parser.add_argument("project_id", type=int, help="Project ID")
    update_project_parser.add_argument("--name", help="New project name")
    update_project_parser.add_argument("--language", choices=["js", "elixir", "golang", "java", "node", "php", "python", "ruby", "other"], help="Project language")
    
    delete_project_parser = subparsers.add_parser("delete-project", help="Delete a project")
    delete_project_parser.add_argument("project_id", type=int, help="Project ID")
    
    project_occurrences_parser = subparsers.add_parser("project-occurrences", help="Get project occurrences")
    project_occurrences_parser.add_argument("--project-id", type=int, help="Project ID (optional)")
    project_occurrences_parser.add_argument("--period", choices=["hour", "day", "week", "month"], default="hour", help="Time period")
    project_occurrences_parser.add_argument("--environment", help="Filter by environment")
    
    # Fault commands
    faults_parser = subparsers.add_parser("faults", help="List faults for a project")
    faults_parser.add_argument("project_id", type=int, help="Project ID")
    faults_parser.add_argument("--query", help="Search query")
    faults_parser.add_argument("--limit", type=int, default=25, help="Maximum number of results")
    faults_parser.add_argument("--order", choices=["recent", "frequent"], default="recent", help="Sort order")
    
    fault_parser = subparsers.add_parser("fault", help="Get fault details")
    fault_parser.add_argument("project_id", type=int, help="Project ID")
    fault_parser.add_argument("fault_id", type=int, help="Fault ID")
    
    fault_summary_parser = subparsers.add_parser("fault-summary", help="Get fault summary")
    fault_summary_parser.add_argument("project_id", type=int, help="Project ID")
    fault_summary_parser.add_argument("--query", help="Search query")
    
    update_fault_parser = subparsers.add_parser("update-fault", help="Update a fault")
    update_fault_parser.add_argument("project_id", type=int, help="Project ID")
    update_fault_parser.add_argument("fault_id", type=int, help="Fault ID")
    update_fault_parser.add_argument("--resolved", choices=["true", "false"], help="Set resolved status")
    update_fault_parser.add_argument("--ignored", choices=["true", "false"], help="Set ignored status")
    update_fault_parser.add_argument("--assignee-id", type=int, help="Assignee ID")
    
    delete_fault_parser = subparsers.add_parser("delete-fault", help="Delete a fault")
    delete_fault_parser.add_argument("project_id", type=int, help="Project ID")
    delete_fault_parser.add_argument("fault_id", type=int, help="Fault ID")
    
    fault_occurrences_parser = subparsers.add_parser("fault-occurrences", help="Get fault occurrences")
    fault_occurrences_parser.add_argument("project_id", type=int, help="Project ID")
    fault_occurrences_parser.add_argument("fault_id", type=int, help="Fault ID")
    fault_occurrences_parser.add_argument("--period", choices=["hour", "day", "week", "month"], default="day", help="Time period")

    fault_notices_parser = subparsers.add_parser("fault-notices", help="List notices for a fault")
    fault_notices_parser.add_argument("project_id", type=int, help="Project ID")
    fault_notices_parser.add_argument("fault_id", type=int, help="Fault ID")
    fault_notices_parser.add_argument("--created-after", type=float, dest="created_after", help="Unix timestamp (float ok): only notices created after this time")
    fault_notices_parser.add_argument("--created-before", type=float, dest="created_before", help="Unix timestamp (float ok): only notices created before this time")
    fault_notices_parser.add_argument("--limit", type=int, default=25, help="Number of results to return (max/default 25)")

    notice_parser = subparsers.add_parser("notice", help="Get a single notice by ID")
    notice_parser.add_argument("notice_id", help="Notice UUID (from fault-notices results[].id)")
    notice_parser.add_argument("--compact", choices=["true", "false"], default="true", help="Return compact output (default true)")
    notice_parser.add_argument("--backtrace-limit", type=int, default=5, dest="backtrace_limit", help="Stack frames in compact mode")
    
    pause_fault_parser = subparsers.add_parser("pause-fault", help="Pause fault notifications")
    pause_fault_parser.add_argument("project_id", type=int, help="Project ID")
    pause_fault_parser.add_argument("fault_id", type=int, help="Fault ID")
    pause_fault_parser.add_argument("--time", choices=["hour", "day", "week"], help="Time period to pause")
    pause_fault_parser.add_argument("--count", type=int, choices=[10, 100, 1000], help="Number of occurrences to pause for")
    
    unpause_fault_parser = subparsers.add_parser("unpause-fault", help="Unpause fault notifications")
    unpause_fault_parser.add_argument("project_id", type=int, help="Project ID")
    unpause_fault_parser.add_argument("fault_id", type=int, help="Fault ID")
    
    bulk_resolve_parser = subparsers.add_parser("bulk-resolve", help="Bulk resolve faults")
    bulk_resolve_parser.add_argument("project_id", type=int, help="Project ID")
    bulk_resolve_parser.add_argument("--query", help="Search query to filter faults")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Execute the requested command
        if args.command == "projects":
            print("Fetching projects...")
            result = get_projects(account_id=args.account_id)
        
        elif args.command == "project":
            print(f"Fetching project {args.project_id}...")
            result = get_project(args.project_id)
        
        elif args.command == "create-project":
            print(f"Creating project '{args.name}'...")
            result = create_project(
                name=args.name,
                account_id=args.account_id,
                language=args.language
            )
        
        elif args.command == "update-project":
            print(f"Updating project {args.project_id}...")
            result = update_project(
                project_id=args.project_id,
                name=args.name,
                language=args.language
            )
        
        elif args.command == "delete-project":
            print(f"Deleting project {args.project_id}...")
            result = delete_project(args.project_id)
        
        elif args.command == "project-occurrences":
            print("Fetching project occurrences...")
            result = get_project_occurrences(
                project_id=args.project_id,
                period=args.period,
                environment=args.environment
            )
        
        elif args.command == "faults":
            print(f"Fetching faults for project {args.project_id}...")
            result = get_faults(
                project_id=args.project_id,
                query=args.query,
                limit=args.limit,
                order=args.order
            )
        
        elif args.command == "fault":
            print(f"Fetching fault {args.fault_id} for project {args.project_id}...")
            result = get_fault_details(args.project_id, args.fault_id)
        
        elif args.command == "fault-summary":
            print(f"Fetching fault summary for project {args.project_id}...")
            result = get_fault_summary(args.project_id, args.query)
        
        elif args.command == "update-fault":
            print(f"Updating fault {args.fault_id} for project {args.project_id}...")
            resolved = None
            if args.resolved:
                resolved = args.resolved.lower() == "true"
            
            ignored = None
            if args.ignored:
                ignored = args.ignored.lower() == "true"
            
            result = update_fault(
                project_id=args.project_id,
                fault_id=args.fault_id,
                resolved=resolved,
                ignored=ignored,
                assignee_id=args.assignee_id
            )
        
        elif args.command == "delete-fault":
            print(f"Deleting fault {args.fault_id} for project {args.project_id}...")
            result = delete_fault(args.project_id, args.fault_id)
        
        elif args.command == "fault-occurrences":
            print(f"Fetching occurrences for fault {args.fault_id} in project {args.project_id}...")
            result = get_fault_occurrences(args.project_id, args.fault_id, args.period)

        elif args.command == "fault-notices":
            print(f"Fetching notices for fault {args.fault_id} in project {args.project_id}...")
            result = get_fault_notices(
                project_id=args.project_id,
                fault_id=args.fault_id,
                created_after=args.created_after,
                created_before=args.created_before,
                limit=args.limit,
            )

        elif args.command == "notice":
            print(f"Fetching notice {args.notice_id}...")
            compact = args.compact.lower() == "true"
            result = get_notice(
                notice_id=args.notice_id,
                compact=compact,
                backtrace_limit=args.backtrace_limit,
            )
        
        elif args.command == "pause-fault":
            print(f"Pausing notifications for fault {args.fault_id} in project {args.project_id}...")
            if not (args.time or args.count):
                print("Error: Either --time or --count must be specified")
                return 1
            
            result = pause_fault_notifications(
                project_id=args.project_id,
                fault_id=args.fault_id,
                time=args.time,
                count=args.count
            )
        
        elif args.command == "unpause-fault":
            print(f"Unpausing notifications for fault {args.fault_id} in project {args.project_id}...")
            result = unpause_fault_notifications(args.project_id, args.fault_id)
        
        elif args.command == "bulk-resolve":
            print(f"Bulk resolving faults for project {args.project_id}...")
            result = bulk_resolve_faults(args.project_id, args.query)
        
        # Print the result
        print("\nResult:")
        pretty_print(result)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 
