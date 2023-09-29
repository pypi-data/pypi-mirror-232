#!/usr/bin/env python3

import argparse
from alx_tool.config import (
    load_config,
    configure_email,
    configure_password,
    get_email,
    get_password
)
from alx_tool.utils import (
    get_url,
    init_project,
    load_project,
)
from alx_tool.spider import run_spider
from alx_tool.version import __version__

def setup_arg_parser():
    """Setup the argument parser for the command line tool."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s version {__version__}",
    )

    # configure subcommand
    config_parser = subparsers.add_parser(
        "configure",
        help="Run interactive configuration wizard"
    )

    # init subcommand
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a project"
    )
    init_parser.add_argument("project")

    # list subcommand
    list_parser = subparsers.add_parser(
        "list",
        help="List project tasks"
    )

    return parser

def handle_configure(args):
    """Handle the 'configure' subcommand."""
    config = load_config()

    configure_email(config)
    configure_password(config)

def handle_init(args):
    """Handle the 'init' subcommand."""
    user_login_email = get_email()
    user_login_password = get_password()
    url_to_project = get_url(args.project)
    
    # get project data, if project already initilized else run scraper
    try:
        project = load_project()
    except SystemExit:
        project = run_spider(user_login_email, user_login_password, url_to_project)

    # initialize project files
    init_project(project)
    

def handle_list(args):
    """Handle the 'list' subcommand."""
    project = load_project()

    filtered_tasks = []

    for task in project.get("tasks", []):
        filtered_task = {key: value for key, value in task.items() if value is not None}
        
        if filtered_task:
            filtered_tasks.append(filtered_task)

    for filtered_task in filtered_tasks:
        for file in filtered_task.get("files", []):
            print(file.strip())

def main():
    parser = setup_arg_parser()

    args = parser.parse_args()

    # subcommands and their handlers
    subcommands = {
        "configure": handle_configure,
        "init": handle_init,
        "list": handle_list,
    }

    # execute appropriate subcommand handler 
    subcommand_handler = subcommands.get(args.subcommand)

    if subcommand_handler:
        subcommand_handler(args)

    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    main()
