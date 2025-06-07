#!/usr/bin/env python3

from pathlib import Path

import requests
import typer
from app.main import run_backend

app = typer.Typer(help="CLI for interacting with the IAC Migration Tool REST API")

API_URL = "http://localhost:8080"


@app.command("run")
def run(
    host: str = typer.Option("localhost", help="Host to run the backend server on"),
    port: int = typer.Option(8080, help="Port to run the backend server on"),
    reload: bool = typer.Option(False, help="Enable auto-reload for development"),
):
    """Run the backend server."""
    run_backend(host=host, port=port, reload=reload)


@app.command("upload-file")
def upload_file(
    file: Path = typer.Argument(
        ..., exists=True, readable=True, help="Path to the file"
    ),
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Name to store the file as (optional, defaults to original name)",
    ),
    description: str = typer.Option(None, prompt=True, help="File description"),
):
    """Upload a file to the server."""
    filename = name
    with file.open("rb") as f:
        response = requests.post(
            f"{API_URL}/file/{filename}",
            files={"file": (file.name, f)},
            data={"description": description},
        )
    typer.echo(response.json())


@app.command("delete-file")
def delete_file(name: str = typer.Argument(..., help="Name of the file to delete")):
    """Delete a file from the server."""
    response = requests.delete(f"{API_URL}/file/{name}")
    typer.echo(response.json())


@app.command("list-files")
def list_files():
    """List all uploaded files."""
    response = requests.get(f"{API_URL}/files")
    print("List of files:")
    typer.echo(response.json())


def main() -> None:
    app()
