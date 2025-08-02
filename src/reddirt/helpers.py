"""Helper functions for the Reddirt CLI."""

import sys
from dataclasses import fields

import inquirer

from . import console


def show_help():
    """Display the help message."""
    console.print("\n[bright_cyan]Available Commands:[/bright_cyan]")
    console.print("  [white]<username>[/white]              Analyze a Reddit user.")
    console.print("  [white]/config[/white]                View or change settings.")
    console.print("  [white]/help[/white]                  Show this help message.")
    console.print("  [white]/exit[/white]                  Exit the application.")
    console.print()


def handle_exit():
    """Exit the application."""
    console.print("Goodbye!")
    sys.exit(0)


def handle_config(manager):
    """Handle the /config command with an interactive editor."""
    while True:
        console.print("\n[bright_cyan]Current Configuration:[/bright_cyan]")
        config_vars = vars(manager.config)

        # Get descriptions from the Config class metadata
        descriptions = {
            f.name: f.metadata.get("description", "No description available.") for f in fields(manager.config)
        }

        editable_keys = [
            key
            for key in config_vars
            if key not in ["reddit_client_id", "reddit_client_secret", "google_api_key", "reddit_user_agent"]
        ]

        choices = []
        for key in editable_keys:
            description = descriptions.get(key, "No description available.")
            choices.append((f"{key}: {config_vars[key]} ({description})", key))
        choices.append(("exit", "exit"))

        questions = [
            inquirer.List(
                "setting_to_change",
                message="Select a setting to change (or select 'exit')",
                choices=choices,
            )
        ]
        answers = inquirer.prompt(questions)

        if not answers or answers["setting_to_change"] == "exit":
            break

        setting_key = answers["setting_to_change"]
        current_value = getattr(manager.config, setting_key)

        console.print(f"Current value of '{setting_key}' is '{current_value}'. Enter a new value:")
        new_value_str = input("> ").strip()

        if new_value_str:
            try:
                # Convert to the original type of the attribute
                original_type = type(current_value)
                if original_type is bool:
                    new_value = new_value_str.lower() in ["true", "1", "yes"]
                else:
                    new_value = original_type(new_value_str)

                setattr(manager.config, setting_key, new_value)
                console.print(f"[green]'{setting_key}' updated to '{new_value}'[/green]")
            except ValueError:
                console.print(f"[red]Invalid value type for '{setting_key}'. Expected {original_type.__name__}.[/red]")


def handle_command(prompt: str, manager):
    """Handle user commands."""
    stripped_prompt = prompt.strip()
    if not stripped_prompt:
        console.print("[yellow]Please enter a command.[/yellow]\n")
        return True

    if stripped_prompt.startswith("/"):
        if stripped_prompt.lower() == "/help":
            show_help()
        elif stripped_prompt.lower() in ["/exit", "/quit"]:
            handle_exit()
        elif stripped_prompt.lower() == "/config":
            handle_config(manager)
        else:
            console.print("[red]Unknown command. Type '/help' for a list of commands.[/red]")
        return True

    # If it's not a command, treat it as a username
    manager.process_analysis(stripped_prompt)
    return True
