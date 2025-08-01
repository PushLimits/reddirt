"""Helper functions for the Reddirt CLI."""

import sys
from . import console


def show_help():
    """Display the help message."""
    console.print("\n[bright_cyan]Available Commands:[/bright_cyan]")
    console.print("  [white]analyze <username>[/white]    Analyze a Reddit user.")
    console.print("  [white]/help[/white]                  Show this help message.")
    console.print("  [white]/exit[/white]                  Exit the application.")
    console.print()


def handle_exit():
    """Exit the application."""
    console.print("Goodbye!")
    sys.exit(0)


def handle_command(prompt: str, manager):
    """Handle user commands."""
    if prompt.lower().strip() == "/help":
        show_help()
        return True
    if prompt.lower().strip() in ["/exit", "/quit"]:
        handle_exit()
        return True
    if prompt.lower().strip().startswith("analyze"):
        parts = prompt.strip().split()
        if len(parts) < 2:
            console.print("[red]Usage: analyze <username>[/red]")
        else:
            username = parts[1]
            manager.process_analysis(username)
        return True

    # If no command was handled, return False
    return False
