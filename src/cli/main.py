#!/usr/bin/env python3
import json
import os
from pathlib import Path

import typer
from app.main import run_backend
from rich import print
from shared.logging.logger import get_logger

from . import __version__
from .service import (
    delete_file_from_storage,
    get_api_url,
    get_config_dir,
    get_file_list,
    save_config,
    upload_file_to_storage,
)

logger = get_logger(__name__)

app = typer.Typer(rich_markup_mode="rich")

CONFIG_DIR = get_config_dir()
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def version_callback(value: bool) -> None:
    """Callback to show version information."""
    if value:
        print(f"[bold]File-Storage CLI[/bold] (version {__version__})")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version of the CLI tool",
    ),
) -> None:
    """
    File Storage Tool CLI for managing file uploads and deletions. 🗂️

    Welcome to the [bold]File Storage Tool CLI[/bold]!
    Use this tool to manage your file uploads and deletions.

    For help, use: [bold]file-storage --help[/bold]
    """


@app.command("set-config")
def set_config(
    host: str = typer.Option(
        None,
        "--host",
        "-h",
        help="Host for the backend server (ignored if --api-url is set)",
    ),
    port: int = typer.Option(
        None,
        "--port",
        "-p",
        help="Port for the backend server (ignored if --api-url is set)",
    ),
    api_url: str = typer.Option(
        None,
        "--api-url",
        "-a",
        help="Full API endpoint URL (e.g. http://localhost:8080)",
    ),
    clear: bool = typer.Option(False, "--clear", "-c", help="Clear the current configuration"),
) -> None:
    """
    Configure the backend server connection settings for the CLI tool. ⚙️

    Parameters:
        host (str, optional): Hostname or IP address of the backend server. Ignored if `api_url` is provided.
        port (int, optional): Port number for the backend server. Ignored if `api_url` is provided.
        api_url (str, optional): Full API endpoint URL (e.g., http://localhost:8080). Takes precedence over `host` and `port`.
        clear (bool, optional): If True, clears the current configuration.

    Behavior:
        - If `api_url` is provided, sets the backend API endpoint to the specified URL.
        - If both `host` and `port` are provided (and `api_url` is not), configures the backend server using these values.
        - If `clear` is True, removes the existing configuration file if it exists.
        - If no configuration is provided, displays a warning message.
    """

    save_config(CONFIG_DIR, CONFIG_PATH, host, port, api_url)
    if api_url:
        print(f"[green]Backend API endpoint set to {api_url}.[/green]")
    elif host and port:
        print(f"[green]Backend server configured to run on [bold]{host}:{port}[/bold].[/green]")
    elif clear:
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
            print("[red]Configuration cleared.[/red]")
        else:
            print("[yellow]No configuration to clear.[/yellow]")
    else:
        print("[yellow]No configuration provided.[/yellow]")


@app.command("get-config")
def get_config() -> None:
    """
    Reads and displays the current configuration from the configuration file. 📄

    Behavior:
        - If the configuration file exists, reads it and prints the API URL, host, and port.
        - If the configuration file does not exist, prints an error message and exits.

    Raises:
        typer.Exit: If the configuration file does not exist.
    """

    if not os.path.exists(CONFIG_PATH):
        print("[red]No configuration found. Please set it using [bold]'set-config'[/bold].[/red]")
        raise typer.Exit(1)

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    if "api_url" in config:
        print(f"[green]API URL: {config['api_url']}[/green]")

    if "host" in config or "port" in config:
        host = config.get("host", "localhost")
        port = config.get("port", 8080)
        print(f"[green]Host: [bold]{host}[/bold], Port: {port}[/green]")

    if "api_url" not in config and ("host" not in config or "port" not in config):
        print("[bold yellow]No API URL or host/port configuration found.[/bold yellow]")

    print("[yellow]-- To set/update the configuration, use [bold]'set-config'[/bold].[/yellow]")
    if "host" in config or "port" in config:
        print("[yellow]-- To run the server, use [bold]'run'[/bold].[/yellow]")


@app.command("run")
def run(
    host: str = typer.Option(None, "--host", "-h", help="Host to run the backend server on"),
    port: int = typer.Option(None, "--port", "-p", help="Port to run the backend server on"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload for development"),
) -> None:
    """
    Starts the backend server with the specified host, port, and reload options.

    Parameters:
        host (str, optional): Host address to run the backend server on. If not provided, uses the value from the config file or defaults to "localhost".
        port (int, optional): Port number to run the backend server on. If not provided, uses the value from the config file or defaults to 8080.
        reload (bool, optional): If True, enables auto-reload for development. Defaults to False.

    Reads configuration from CONFIG_PATH if available, and overrides with command-line options if provided.
    """

    server_host = "localhost"
    server_port = 8080

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    if "host" in config and "port" in config:
        server_host = config["host"] or server_host
        server_port = config["port"] or server_port

    server_host = host or server_host
    server_port = port or server_port

    run_backend(server_host, server_port, reload=reload)


@app.command("upload-file")
def upload_file(
    file: Path = typer.Argument(..., exists=True, readable=True, help="Path to the file"),
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Name to store the file as.",
    ),
    destination: str = typer.Option(
        None,
        "--destination",
        "-d",
        help="Destination directory for the file (optional, defaults to root)",
    ),
    tags: str = typer.Option(
        None,
        "--tags",
        "-t",
        help="Comma-separated tags to associate with the file (optional)",
    ),
    description: str = typer.Option(None, "--description", "-desc", help="Description of the file (optional)"),
    api_url: str = typer.Option(None, "--api-url", "-a", help="API URL to use for the upload (overrides config)"),
) -> None:
    """
    Uploads a file to the storage server using the provided API URL and options. 📤

    Args:
        file (Path): Path to the file to upload. Must exist and be readable.
        name (str): Name to store the file as.
        destination (str, optional): Destination directory for the file. Defaults to root if not specified.
        tags (str, optional): Comma-separated tags to associate with the file.
        description (str, optional): Description of the file.
        api_url (str, optional): API URL to use for the upload. Overrides the config if provided.

    Raises:
        Exception: If an error occurs during the upload process.

    Side Effects:
        Prints the result of the upload operation to the console, including success or error messages and response details.
    """

    api_url_for_call = api_url or get_api_url(CONFIG_PATH)
    logger.debug(f"Using the API URL: {api_url_for_call}")
    try:
        response = upload_file_to_storage(
            api_url=api_url_for_call,
            file=file,
            name=name,
            destination=destination or "",
            tags=tags or "",
            description=description,
        )
        if response.status_code == 200:
            print(f"[green]File [bold]'{name}'[/bold] uploaded successfully.[/green]")
            print(f"[yellow]Response: {response.json()}[/yellow]")
        else:
            print("[red]File upload failed or no response received.[/red]")
            print(f"[red]Status Code: {response.status_code}[/red]")
            print(f"[yellow]Response: {response.text}[/yellow]")
    except Exception as e:
        print(f"[red]Error uploading file: {e}[/red]")


@app.command("delete-file")
def delete_file(
    name: str = typer.Argument(..., help="Name of the file to delete"),
    destination: str = typer.Option(None, "--destination", "-d", help="Destination directory of the file (optional)"),
    delete_permanently: bool = typer.Option(False, "--force", "-f", help="Delete file permanently (default is false)"),
    api_url: str = typer.Option(
        None,
        "--api-url",
        "-a",
        help="API URL to use for the deletion (overrides config)",
    ),
) -> None:
    """
    Deletes a file from storage, with optional permanent deletion and API URL override. 🗑️

    Args:
        name (str): Name of the file to delete.
        destination (str, optional): Destination directory of the file. Defaults to None.
        delete_permanently (bool, optional): If True, deletes the file permanently after user confirmation. Defaults to False.
        api_url (str, optional): API URL to use for the deletion, overrides config if provided. Defaults to None.

    Raises:
        typer.Exit: If the user cancels the permanent deletion confirmation.
        Exception: If an error occurs during the deletion process.

    Side Effects:
        Prints status messages to the console regarding the deletion outcome.
    """

    api_url_for_call = api_url or get_api_url(CONFIG_PATH)
    logger.debug(f"Using the API URL: {api_url_for_call}")
    if delete_permanently:
        print(
            f"[bold red]Are you sure you want to permanently delete the file '{destination}/{name}'? This action cannot be undone.[/bold red]"
        )
        confirmation = typer.prompt("Type 'yes' to confirm", default="no", show_default=False)
        if confirmation.lower() != "yes":
            print("[red]File deletion cancelled.[/red]")
            raise typer.Exit(0)
    try:
        response = delete_file_from_storage(
            api_url=api_url_for_call,
            name=name,
            destination=destination or "",
            delete_permanently=delete_permanently,
        )
        if response.status_code == 200:
            if delete_permanently:
                print(f"[green]File '{name}' [red]deleted[/red] permanently.[/green]")
            else:
                print(f"[green]File '{name}' [red]deleted[/red] successfully.[/green]")
        else:
            print(f"[red]Failed to delete file '{name}'.[/red]")
            print(f"[yellow]Status Code: {response.status_code}[/yellow]")
            print(f"[yellow]Response: {response.text}[/yellow]")
    except Exception as e:
        print(f"[red]Error deleting file: {e}[/red]")


@app.command("list-files")
def list_files(
    order_by_name: bool = typer.Option(False, "--name", "-n", help="Sort files by name (a -> z)"),
    order_by_updated_at: bool = typer.Option(
        False, "--update", "-u", help="Sort files by last updated date (latest first)"
    ),
    order_by_size: bool = typer.Option(False, "--size", "-s", help="Sort files by size (smallest first)"),
    destination: str = typer.Option("", "--destination", "-d", help="Filter files by destination directory"),
    tag: str = typer.Option("", "--tag", "-t", help="Filter files by tag"),
    api_url: str = typer.Option(
        None,
        "--api-url",
        "-a",
        help="API URL to use for listing files (overrides config)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Include detailed information in the output"),
) -> None:
    """
    List all uploaded files with optional sorting and filtering. 📚

    Parameters:
        order_by_name (bool): If True, sort files by name.
        order_by_updated_at (bool): If True, sort files by last updated date (latest first).
        order_by_size (bool): If True, sort files by size (smallest first).
        destination (str): Filter files by destination directory.
        tag (str): Filter files by tag.
        api_url (str): API URL to use for listing files (overrides config).
        verbose (bool): If True, include detailed information in the output.

    Displays:
        - A list of files matching the criteria, or a message if no files are found.
        - Error messages if the request fails or an exception occurs.

    Raises:
        Exception: If there is an error retrieving the file list.
    """

    api_url_for_call = api_url or get_api_url(CONFIG_PATH)
    logger.debug(f"Using the API URL: {api_url_for_call}")
    try:
        response = get_file_list(
            api_url=api_url_for_call,
            order_by_name=order_by_name,
            order_by_updated_at=order_by_updated_at,
            order_by_size=order_by_size,
            destination=destination.strip("/"),
            tag=tag,
            verbose=verbose,
        )
        if response.status_code == 200:
            files = response.json()
            if not files:
                print("[yellow]No files found.[/yellow]")
                return
            if verbose:
                print("[bold][yellow]Following are the details of files saved in the storage:[/yellow][/bold]")
                print(files)
            else:
                print("[bold][yellow]Following files are saved in the storage:[/yellow][/bold]")
                print(files)
        else:
            print("[red]Failed to retrieve file list.[/red]")
            print(f"[yellow]Status Code: {response.status_code}[/yellow]")
            print(f"[yellow]Response: {response.text}[/yellow]")
            return
    except Exception as e:
        print(f"[red]Error listing files: {e}[/red]")


def main() -> None:
    app()
