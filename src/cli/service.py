import json
import os
import platform
from pathlib import Path

import requests
from shared.logging.logger import get_logger

logger = get_logger(__name__)

API_URL = "http://localhost:8080"


def get_config_dir():
    if platform.system() == "Windows":
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "file-storage-cli")
    return os.path.join(
        os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
        "file-storage-cli",
    )


def save_config(
    config_dir: str,
    config_path: str,
    host: str = None,
    port: int = None,
    api_url: str = None,
):
    os.makedirs(config_dir, exist_ok=True)
    config = {}
    if api_url:
        config["api_url"] = api_url
    if host:
        config["host"] = host
    if port:
        config["port"] = port
    with open(config_path, "w") as f:
        json.dump(config, f)


def load_config(config_path: str):
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return None


def get_api_url(config_path: str, api_url: str = None):
    if not os.path.exists(config_path):
        logger.debug("No configuration found. Please set it using 'set-config'.")
    else:
        with open(config_path, "r") as f:
            config = json.load(f)

        if "api_url" in config:
            return config["api_url"]
        else:
            host = config.get("host", "localhost")
            port = config.get("port", 8080)
            return f"http://{host}:{port}"
    return API_URL


def upload_file_to_storage(
    api_url: str,
    file: Path,
    name: str,
    destination: str = "",
    tags: str = "",
    description: str = "",
):
    try:
        with file.open("rb") as f:
            response = requests.post(
                f"{api_url}/file/{name}",
                files={"file": (file.name, f)},
                data={
                    "destination": destination,
                    "tags": tags,
                    "description": description,
                },
            )
        response.raise_for_status()
        if response.status_code == 200:
            logger.debug("File uploaded successfully.")
            return response
        else:
            logger.debug(f"Failed to upload file: {response.text}")
            return response
    except requests.RequestException as e:
        logger.debug(f"Error uploading file: {e}")
        raise Exception(e) from e


def delete_file_from_storage(
    api_url: str,
    name: str,
    destination: str = "",
    delete_permanently: bool = False,
):
    try:
        response = requests.delete(
            f"{api_url}/file/{name}",
            params={
                "destination": destination,
                "delete_permanently": delete_permanently,
            },
        )
        response.raise_for_status()
        if response.status_code == 200:
            logger.debug("File deleted successfully.")
            return response
        else:
            logger.debug(f"Failed to delete file: {response.text}")
            return response
    except requests.RequestException as e:
        logger.debug(f"Error deleting file: {e}")
        raise Exception(e) from e


def get_file_list(
    api_url: str,
    order_by_name: bool = False,
    order_by_updated_at: bool = False,
    order_by_size: bool = False,
    destination: str = "",
    tag: str = "",
    verbose: bool = False,
):
    params = {
        "order_by_name": order_by_name,
        "order_by_updated_at": order_by_updated_at,
        "order_by_size": order_by_size,
        "destination": destination,
        "tag": tag,
        "verbose": verbose,
    }

    try:
        response = requests.get(f"{api_url}/files", params=params)
        response.raise_for_status()
        if response.status_code == 200:
            logger.debug("File list retrieved successfully.")
            return response
        else:
            logger.debug(f"Failed to retrieve file list: {response.text}")
            return response
    except requests.RequestException as e:
        logger.debug(f"Error retrieving file list: {e}")
        raise Exception(e) from e
