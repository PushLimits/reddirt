"""CLI entry point for the Reddirt application."""

import os
import sys

from rich.text import Text

from reddirt import console
from reddirt.helpers import handle_command
from reddirt.manager import Manager


def display_application_banner():
    """Display the application banner."""
    banner_text = """
██████╗  ███████╗ ██████╗  ██████╗  ██╗ ██████╗  ████████╗
██╔══██╗ ██╔════╝ ██╔══██╗ ██╔══██╗ ██║ ██╔══██╗ ╚══██╔══╝
██████╔╝ █████╗   ██║  ██║ ██║  ██║ ██║ ██████╔╝    ██║   
██╔══██╗ ██╔══╝   ██║  ██║ ██║  ██║ ██║ ██╔══██╗    ██║   
██║  ██║ ███████╗ ██████╔╝ ██████╔╝ ██║ ██║  ██║    ██║   
╚═╝  ╚═╝ ╚══════╝ ╚═════╝  ╚═════╝  ╚═╝ ╚═╝  ╚═╝    ╚═╝   
"""
    lines = banner_text.strip().split("\n")
    gradient_colors = ["purple", "blue_violet", "medium_purple", "royal_blue", "dodger_blue", "deep_sky_blue"]

    styled_lines = []
    for i, line in enumerate(lines):
        color = gradient_colors[i % len(gradient_colors)]
        styled_lines.append(Text(line, style=f"bold {color}"))

    full_banner = Text()
    full_banner.append("\n\n")
    for line in styled_lines:
        full_banner.append(line)
        full_banner.append("\n")

    subtitle = Text("Interactive Reddit User Analysis", style="bold purple")
    full_banner.append("\n")
    full_banner.append(subtitle)
    full_banner.append("\n")

    console.print(full_banner)


def interactive_shell():
    """Run the interactive shell."""
    os.system("cls" if os.name == "nt" else "clear")
    display_application_banner()

    console.print("This application analyzes a Reddit user's activity and provides insights into their behavior.")
    console.print("To get started, simply enter a Reddit username below.")
    console.print("For a list of commands, type '/help'.\n")

    manager = Manager()

    console.print("Type your commands below. Press Ctrl+C to exit.\n")
    try:
        while True:
            console.print("[bright_cyan]> [/bright_cyan]", end="")
            user_input = input()

            if user_input.strip():
                if not handle_command(user_input, manager):
                    console.print("[red]Unknown command. Type '/help' for a list of commands.[/red]")
            else:
                console.print("[yellow]Please enter a command.[/yellow]\n")

    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)


def main():
    """Main entry point."""
    interactive_shell()


if __name__ == "__main__":
    main()
