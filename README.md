# File Storage Service

### Table of Contents
- [File Storage Service](#file-storage-service)
    - [Overview](#overview)
        - [Features](#features)
    - [Getting Started](#getting-started)
        - [Prerequisites](#prerequisites)
        - [App Installation using docker](#app-installation-using-docker-recommended)
        - [Local Installation](#local-installation)
        - [CLI Installation](#cli-installation)
        - [Testing and format checks](#testing-and-format-checks)
    - [Accessing the Server](#accessing-the-server)
        - [RESTful APIs](#restful-apis)
        - [Command Line Interface (CLI)](#command-line-interface-cli)
    - [Configurations](#configurations)
    - [Project Structure](#project-structure)


## Overview

The File Storage Service is a Python-based application built with FastAPI, designed to function as a blob storage solution for saving files. This project offers RESTful APIs for file management, including uploading, listing, and deleting files, along with metadata handling. Additionally, it provides a Command-Line Interface (CLI) for easy server interaction.

### Features

- **HTTP Endpoints**:
    - **POST**: Upload a file to the storage
    - **DELETE**: Remove a file from storage
    - **GET**: List all files available in storage
- **CLI**: Interact with the server through a command-line interface.
- **Modular Architecture**: Structured for flexibility.
- **Dockerization**: Simplified deployment using Docker.
- **Database Integration**: Utilizes SQLAlchemy for ORM and Alembic for migrations.
- **Configurable Storage Options**: Supports Amazon S3, Google Cloud Storage, and local file storage.

## Getting Started

### Prerequisites

To run the File Storage server and CLI efficiently, the following are required:
- **Python 3.12**
- **Poetry 1.8** (for dependency management)
- **Pip 24.1** (for installing CLI globally)
- **Docker** (for containerized deployment)

### App Installation using docker (*Recommended)

For an easier and quicker installation, it is recommended to use Docker. Before installation, it is important to create a configuration file, please check [Configuration](#configuration) section for more details. To install the application using Docker, run the following command (ensure that the Docker daemon is up and running):

``` sh
docker compose up --build
```
This will start the application container along with PostgreSQL and a MinIO container, which are used by the backend of the application. Once the server is up and running, you can access the API endpoints at the configured host and port (defaults to `http://localhost:8080`).

You can use the Swagger UI at `{your_api_url}/doc` or Postman to make API calls to the server.

### Local Installation

To install the application locally without Docker, you can use Poetry to run the server. However, in this setup, a PostgreSQL server and an Amazon S3 server are required. Alternatively, local file storage can be used as blob storage if S3 is not available. Before installation, it is important to create a configuration file, please check [Configuration](#configuration) section for more details. Ensure that the configurations for PostgreSQL and S3 are correctly set in the `.env` file.

Follow the steps below to run the server locally:

1. **Install dependencies:**
``` sh
poetry install
```
2. **Run data migration:**
``` sh
alembic upgrade head
```
3. **Run the server:**
``` sh
poetry run uvicorn app.main:app --port 8080
```

Once the server is running, you can access the Swagger UI at `http://localhost:8080/docs`.

### CLI Installation

The CLI for this tool can be installed using the wheel file located in the `dist/` directory of this project. To install it, navigate to the root folder of the project and run the following command:
``` sh
pip install dist/file_storage-0.1.0-py3-none-any.whl 
```
To verify the installation, run the following command:
``` sh
fs-store -v
```
This will return the version of the File-Storage CLI. To learn more about the available CLI commands, you can run the following command:
``` sh
fs-store --help
```
This will display a list of all available commands and options for the File-Storage CLI.

### Testing and format checks

To run the unit tests and check the coverage, use the following command:
``` sh
poe unit-tests
```
To check import formatting, code formatting, whitespace formatting and linting automation, you can run the following commands:

- **Check import formatting**
``` sh
poe import-check
```

- **Check code formatting**
``` sh
poe format-check
```

- **Check whitespace formatting**
``` sh
poe whitespace-check
```

- **Linting automation**
``` sh
poe lint-check
```

The commands mentioned above should be executed within the `poetry shell`. To activate the Poetry shell, run:
``` sh
poetry shell
```
Once inside the Poetry shell, you can execute the commands for unit tests, formatting checks, and linting as outlined earlier.

## Accessing the Server
There are two ways to interact with the server of this application: through **RESTful APIs** and the **Command Line Interface (CLI)**. Below are the details for using both methods:

### RESTful APIs
The server currently supports three actions via API calls. You can access these actions by making the respective HTTP requests to the server’s configured host and port.


- **POST Endpoint**: `http://{api_url}/file/{name}`
``` sh
# Usage:

curl -X 'POST' \
  'http://localhost:8080/file/demo.pdf' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=dir/test.pdf;type=application/pdf' \
  -F 'destination=PDFs' \
  -F 'tags=test, pdf, sample' \
  -F 'description=This is a test for the POST endpoint'
```
    Uploads a file to the storage server with the specified metadata.

    Args:
        name        (str)           : Name of the file to upload (from path parameter).
        file        (UploadFile)    : The file to be uploaded.
        destination (str, optional) : Destination directory for the file.
        tags        (str, optional) : Tags to associate with the file.
        description (str, optional) : Description of the file.

    Returns:
        Details of the uploaded file upon successful upload.

    Raises:
        Exception: If an error occurs during the upload process.

- **DELETE Endpoint:** `http://{api_url}/file/{name}`
``` sh
# Usage:

curl -X 'DELETE' \
  'http://localhost:8080/file/demo.pdf?destination=PDFs&delete_permanently=false' \
  -H 'accept: application/json'
```
    Deletes a file either permanently or by soft deletion.
    Args:
        name               (str)            : Name of the file to delete (from path parameter).
        destination        (str, optional)  : Destination directory of the file (from query parameter). Defaults to "".
        delete_permanently (bool, optional) : If True, deletes the file permanently; otherwise, performs a soft delete. Defaults to False.

    Returns:
        A message indicating the result of the deletion operation.

    Raises:
        HTTPException:
            - 404 if the file is not found.
            - 500 if there is an error during the deletion process.

- **GET Endpoint:** `http://{api_url}/files`
``` sh
# Usage:

curl -X 'GET' \
  'http://localhost:8080/files?order_by_name=false&order_by_updated_at=true&order_by_size=false&destination=PDFs&verbose=false' \
  -H 'accept: application/json'
```
    Lists all files in the storage server, with optional filtering and sorting.

    Args:
        order_by_name       (bool) : Sort files by name if True (a -> z).
        order_by_updated_at (bool) : Sort files by last update date if True (recently updated first).
        order_by_size       (bool) : Sort files by size if True (smallest first).
        destination         (str)  : Filter files by destination directory.
        tag                 (str)  : Filter files by tag.
        verbose             (bool) : Include additional version information if True.

    Returns:
        List of file details or error message.

    Raises:
        Exception: If an error occurs while retrieving the file list.

### Command Line Interface (CLI)
Another way to interact with the server is through the CLI. The following are the commands supported by the File-Storage CLI:

- **`fs-store`**
``` sh
fs-store --help
                                                                                                                                                                                                                                                                      
 Usage: fs-store [OPTIONS] COMMAND [ARGS]...                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                      
 File Storage Tool CLI for managing file uploads and deletions. 🗂️                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                      
 Welcome to the File Storage Tool CLI!                                                                                                                                                                                                                                
 Use this tool to manage your file uploads and deletions.                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                      
 For help, use: file-storage --help                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                      
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version             -v        Show the version of the CLI tool                                                     │
│ --install-completion            Install completion for the current shell.                                            │
│ --show-completion               Show completion for the current shell, to copy it or customize the installation.     │
│ --help                          Show this message and exit.                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ set-config    Configure the backend server connection settings for the CLI tool. ⚙️                                  │
│ get-config    Reads and displays the current configuration from the configuration file. 📄                           │
│ upload-file   Uploads a file to the storage server using the provided API URL and options. 📤                        │
│ delete-file   Deletes a file from storage, with optional permanent deletion and API URL override. 🗑️                 │
│ list-files    List all uploaded files with optional sorting and filtering. 📚                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- **`fs-store set-config`**
**Note: This does not set the application configurations, it is only used for CLI configurations.**
``` sh
fs-store set-config --help
                                                                                                                                                                                                                                                                      
 Usage: fs-store set-config [OPTIONS]                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                      
 Configure the backend server connection settings for the CLI tool. ⚙️                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                      
 Parameters:                                                                                                                                                                                                                                                          
     host    (str, optional)  : Hostname or IP address of the backend server. Ignored if `api_url` is provided.                                                                                                                                                            
     port    (int, optional)  : Port number for the backend server. Ignored if `api_url` is provided.                                                                                                                                                                      
     api_url (str, optional)  : Full API endpoint URL (e.g., http://localhost:8080). Takes precedence over `host` and `port`.                                                                                                                                           
     clear   (bool, optional) : If True, clears the current configuration.                                                                                                                                                                                               
                                                                                                                                                                                                                                                                      
 Behavior:                                                                                                                                                                                                                                                            
     - If `api_url` is provided, sets the backend API endpoint to the specified URL.                                                                                                                                                                                  
     - If both `host` and `port` are provided (and `api_url` is not), configures the backend server using these values.                                                                                                                                               
     - If `clear` is True, removes the existing configuration file if it exists.                                                                                                                                                                                      
     - If no configuration is provided, displays a warning message.                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                      
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --host     -h      TEXT     Host for the backend server (ignored if --api-url is set) [default: None]                │
│ --port     -p      INTEGER  Port for the backend server (ignored if --api-url is set) [default: None]                │
│ --api-url  -a      TEXT     Full API endpoint URL (e.g. http://localhost:8080) [default: None]                       │
│ --clear    -c               Clear the current configuration                                                          │
│ --help                      Show this message and exit.                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- **`fs-store get-config`**
**Note: This does not display the application configurations, it only displays CLI configurations.**
``` sh
fs-store get-config --help

 Usage: fs-store get-config [OPTIONS]                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                      
 Reads and displays the current configuration from the configuration file. 📄                                                                                                                                                                                         
                                                                                                                                                                                                                                                                      
 Behavior:                                                                                                                                                                                                                                                            
     - If the configuration file exists, reads it and prints the API URL, host, and port.                                                                                                                                                                             
     - If the configuration file does not exist, prints an error message and exits.                                                                                                                                                                                   
                                                                                                                                                                                                                                                                      
 Raises:                                                                                                                                                                                                                                                              
     typer.Exit: If the configuration file does not exist.                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                      
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- **`fs-store upload-file`**
``` sh
fs-store upload-file --help
                                                                                                                                                                                                                                                                      
 Usage: fs-store upload-file [OPTIONS] FILE                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                      
 Uploads a file to the storage server using the provided API URL and options. 📤                                                                                                                                                                                      
                                                                                                                                                                                                                                                                      
 Args:                                                                                                                                                                                                                                                                
     file        (Path)          : Path to the file to upload. Must exist and be readable.                                                                                                                                                                                             
     name        (str)           : Name to store the file as.                                                                                                                                                                                                                           
     destination (str, optional) : Destination directory for the file. Defaults to root if not specified.                                                                                                                                                              
     tags        (str, optional) : Comma-separated tags to associate with the file.                                                                                                                                                                                           
     description (str, optional) : Description of the file.                                                                                                                                                                                                            
     api_url     (str, optional) : API URL to use for the upload. Overrides the config if provided.                                                                                                                                                                        
                                                                                                                                                                                                                                                                      
 Raises:                                                                                                                                                                                                                                                              
     Exception: If an error occurs during the upload process.                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                      
 Side Effects:                                                                                                                                                                                                                                                        
     Prints the result of the upload operation to the console, including success or error messages and response details.                                                                                                                                              
                                                                                                                                                                                                                                                                      
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    file      PATH  Path to the file [default: None] [required]                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --name         -n         TEXT  Name to store the file as. [default: None] [required]                             │
│    --destination  -d         TEXT  Destination directory for the file (optional, defaults to root) [default: None]   │
│    --tags         -t         TEXT  Comma-separated tags to associate with the file (optional) [default: None]        │
│    --description  -desc      TEXT  Description of the file (optional) [default: None]                                │
│    --api-url      -a         TEXT  API URL to use for the upload (overrides config) [default: None]                  │
│    --help                          Show this message and exit.                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- **`fs-store delete-file`**
``` sh
fs-store delete-file --help
                                                                                                                                                                                                                                                                      
 Usage: fs-store delete-file [OPTIONS] NAME                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                      
 Deletes a file from storage, with optional permanent deletion and API URL override. 🗑️                                                                                                                                                                                
                                                                                                                                                                                                                                                                      
 Args:                                                                                                                                                                                                                                                                
     name               (str)            : Name of the file to delete.                                                                                                                                                                                                                          
     destination        (str, optional)  : Destination directory of the file. Defaults to None.                                                                                                                                                                                
     delete_permanently (bool, optional) : If True, deletes the file permanently after user confirmation. Defaults to False.                                                                                                                                           
     api_url            (str, optional)  : API URL to use for the deletion, overrides config if provided. Defaults to None.                                                                                                                                                        
                                                                                                                                                                                                                                                                      
 Raises:                                                                                                                                                                                                                                                              
     typer.Exit: If the user cancels the permanent deletion confirmation.                                                                                                                                                                                             
     Exception: If an error occurs during the deletion process.                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                      
 Side Effects:                                                                                                                                                                                                                                                        
     Prints status messages to the console regarding the deletion outcome.                                                                                                                                                                                            
                                                                                                                                                                                                                                                                      
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    name      TEXT  Name of the file to delete [default: None] [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --destination  -d      TEXT  Destination directory of the file (optional) [default: None]                            │
│ --force        -f            Delete file permanently (default is false)                                              │
│ --api-url      -a      TEXT  API URL to use for the deletion (overrides config) [default: None]                      │
│ --help                       Show this message and exit.                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- **`fs-store list-files`**
``` sh
fs-store list-files --help
                                                                                                                                                                                                                                                                      
 Usage: fs-store list-files [OPTIONS]                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                      
 List all uploaded files with optional sorting and filtering. 📚                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                      
 Parameters:                                                                                                                                                                                                                                                          
     order_by_name       (bool) : If True, sort files by name.                                                                                                                                                                                                               
     order_by_updated_at (bool) : If True, sort files by last updated date (latest first).                                                                                                                                                                             
     order_by_size       (bool) : If True, sort files by size (smallest first).                                                                                                                                                                                              
     destination         (str)  : Filter files by destination directory.                                                                                                                                                                                                        
     tag                 (str)  : Filter files by tag.                                                                                                                                                                                                                                  
     api_url             (str)  : API URL to use for listing files (overrides config).                                                                                                                                                                                              
     verbose             (bool) : If True, include detailed information in the output.                                                                                                                                                                                             
                                                                                                                                                                                                                                                                      
 Displays:                                                                                                                                                                                                                                                            
     - A list of files matching the criteria, or a message if no files are found.                                                                                                                                                                                     
     - Error messages if the request fails or an exception occurs.                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                      
 Raises:                                                                                                                                                                                                                                                              
     Exception: If there is an error retrieving the file list.                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                      
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --name         -n            Sort files by name (a -> z)                                                             │
│ --update       -u            Sort files by last updated date (latest first)                                          │
│ --size         -s            Sort files by size (smallest first)                                                     │
│ --destination  -d      TEXT  Filter files by destination directory                                                   │
│ --tag          -t      TEXT  Filter files by tag                                                                     │
│ --api-url      -a      TEXT  API URL to use for listing files (overrides config) [default: None]                     │
│ --verbose      -v            Include detailed information in the output                                              │
│ --help                       Show this message and exit.                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Configurations
1. Create a `.env` file in the project root directory.
2. Populate the .env file with following environment variables.

**Note: You don't need to create an .env file for now, it has been included in the ZIP file for easy setup and installation.**

| **Category**    | **Environment Variable**          | **Description**                                                      | **Example/Dwfault**       |
|-----------------|--------------------------------|-------------------------------------------------------------------------|---------------------------|
| **General**     | PROJECT_NAME                   | Name of the project.                                                    | file-storage-tool         |
|                 | CONSOLE_LOG_LEVEL              | Log level for the console logs. (e.g., INFO, DEBUG, WARNING, ERROR)     | INFO                      |
|                 | FILE_LOG_LEVEL                 | Log level for the  app.log. (e.g., INFO, DEBUG, WARNING, ERROR)         | DEBUG                     |
|                 | DEV_MODE                       | Development mode (Y for yes, N for no)                                  | Y                         |
|                 | ALLOWED_ORIGINS                | Allowed origins for CORS                                                | "http://localhost:8080"   |
| **Database**    | DB_TYPE                        | Type of DB to be used to save metadata (postgresql or mysql or sqlite)  | postgresql                |
|                 | DB_HOST                        | Database host (IP or localhost or postgres)                             | postgres                  |
|                 | DB_PORT                        | Database port                                                           | 5432                      |
|                 | DB_NAME                        | Name of the database to use for metadata storage                        | file_storage              |
|                 | DB_USER                        | Database username                                                       | postgres                  |
|                 | DB_PASSWORD                    | Database password                                                       | postgres                  |
|                 | DB_POOL_SIZE                   | Number of connections to keep in the pool                               | 10                        |
|                 | DB_MAX_OVERFLOW                | Maximum overflow connections above pool size                            | 20                        |
| **File Storage**| STORAGE_TYPE                   | Type of storage backend (s3, gcs, local)                                | s3                        |
|                 | STORAGE_BUCKET_NAME            | Name of the storage bucket                                              | temp                      |
| **AWS S3**      | S3_ENDPOINT_URL                | S3-compatible endpoint URL                                              | "http://localhost:9000"   |
|                 | STORAGE_AWS_ACCESS_KEY_ID      | AWS access key ID                                                       | minioadmin                |
|                 | STORAGE_AWS_SECRET_ACCESS_KEY  | AWS secret access key                                                   | minioadmin123             |
|                 | STORAGE_REGION_NAME            | AWS region name                                                         | us-east-1                 |
| **GCS**         | STORAGE_GCS_LOCATION           | GCS location (not in use currently)                                     | us-central1               | 



## Project Structure
This section outlines the important directories and files in the project.
```
├── src/
│   ├── app/                # Application entrypoint
│   │   ├── api/            # API Endpoints
│   │   ├── core/           # Config, database, logging, storage logic
│   │   ├── entity/         # ORM entities/models
│   │   ├── model/          # Pydantic models and enums
│   │   ├── repository/     # Data access layer
│   │   └── service/        # Business logic
│   └── cli/                # Command-line interface
├── tests/                  # Unit tests
├── alembic/                # Database migrations
├── .github/                # Github Actions Workflows
├── dist/                   # Distributable CLI package
├── docker-compose.yml      # Multi-container orchestration
├── Dockerfile              # Docker container definition
├── pyproject.toml          # Project dependencies and settings
├── .env                    # Configurations
├── README.md               # Readme file
```