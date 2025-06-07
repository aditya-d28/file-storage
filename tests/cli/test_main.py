import json
from unittest import mock

import pytest
import typer
from typer.testing import CliRunner

from cli import main

runner = CliRunner()


@pytest.fixture(autouse=True)
def mock_config_dir(monkeypatch, tmp_path):
    # Patch get_config_dir to use a temp directory
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    monkeypatch.setattr(main, "CONFIG_DIR", str(config_dir))
    monkeypatch.setattr(main, "CONFIG_PATH", str(config_dir / "config.json"))
    yield


def test_version_callback_prints_version(capsys):
    with pytest.raises(typer.Exit):
        main.version_callback(True)
    captured = capsys.readouterr()
    assert "File-Storage CLI" in captured.out


def test_set_config_api_url(monkeypatch):
    with mock.patch("cli.main.save_config") as save_config:
        result = runner.invoke(main.app, ["set-config", "--api-url", "http://test"])
        assert result.exit_code == 0
        assert "Backend API endpoint set to http://test." in result.output
        save_config.assert_called()


def test_set_config_host_port(monkeypatch):
    with mock.patch("cli.main.save_config") as save_config:
        result = runner.invoke(main.app, ["set-config", "--host", "127.0.0.1", "--port", "9000"])
        assert result.exit_code == 0
        assert "Backend host and port set to 127.0.0.1:9000." in result.output
        save_config.assert_called()


def test_set_config_clear(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{}")
    monkeypatch.setattr(main, "CONFIG_PATH", str(config_path))
    result = runner.invoke(main.app, ["set-config", "--clear"])
    assert "Configuration cleared." in result.output
    assert not config_path.exists()


def test_set_config_no_config(monkeypatch):
    with mock.patch("cli.main.save_config"):
        result = runner.invoke(main.app, ["set-config"])
        assert "No configuration provided." in result.output


def test_get_config_no_file(monkeypatch):
    monkeypatch.setattr(main, "CONFIG_PATH", "nonexistent.json")
    result = runner.invoke(main.app, ["get-config"])
    assert "No configuration found" in result.output
    assert result.exit_code != 0


def test_get_config_api_url_and_host_port(tmp_path, monkeypatch):
    config = {"api_url": "http://api", "host": "h", "port": 1234}
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    monkeypatch.setattr(main, "CONFIG_PATH", str(config_path))
    result = runner.invoke(main.app, ["get-config"])
    assert "API URL: http://api" in result.output
    assert "Host: h, Port: 1234" in result.output


def test_upload_file_success(monkeypatch, tmp_path):
    file_path = tmp_path / "f.txt"
    file_path.write_text("data")
    mock_response = mock.Mock(status_code=200, json=lambda: {"ok": True})
    monkeypatch.setattr(main, "upload_file_to_storage", lambda **kwargs: mock_response)
    monkeypatch.setattr(main, "get_api_url", lambda path: "http://api")
    result = runner.invoke(main.app, ["upload-file", str(file_path), "--name", "f"])
    assert "uploaded successfully" in result.output


def test_upload_file_failure(monkeypatch, tmp_path):
    file_path = tmp_path / "f.txt"
    file_path.write_text("data")
    mock_response = mock.Mock(status_code=400, text="fail")
    monkeypatch.setattr(main, "upload_file_to_storage", lambda **kwargs: mock_response)
    monkeypatch.setattr(main, "get_api_url", lambda path: "http://api")
    result = runner.invoke(main.app, ["upload-file", str(file_path), "--name", "f"])
    assert "File upload failed" in result.output


def test_delete_file_success(monkeypatch):
    mock_response = mock.Mock(status_code=200)
    monkeypatch.setattr(main, "delete_file_from_storage", lambda **kwargs: mock_response)
    monkeypatch.setattr(main, "get_api_url", lambda path: "http://api")
    result = runner.invoke(main.app, ["delete-file", "f"])
    assert "deleted successfully" in result.output


def test_delete_file_permanent_cancel(monkeypatch):
    monkeypatch.setattr(main, "delete_file_from_storage", lambda **kwargs: None)
    monkeypatch.setattr(main, "get_api_url", lambda path: "http://api")
    with mock.patch("typer.prompt", return_value="no"):
        result = runner.invoke(main.app, ["delete-file", "f", "--force"])
        assert "File deletion cancelled" in result.output


def test_delete_file_failure(monkeypatch):
    mock_response = mock.Mock(status_code=400, text="fail")
    monkeypatch.setattr(main, "delete_file_from_storage", lambda **kwargs: mock_response)
    monkeypatch.setattr(main, "get_api_url", lambda path: "http://api")
    result = runner.invoke(main.app, ["delete-file", "f"])
    assert "Failed to delete file" in result.output


def test_list_files_success(monkeypatch):
    mock_response = mock.Mock(status_code=200, json=lambda: [{"name": "f"}])
    monkeypatch.setattr(main, "get_file_list", lambda **kwargs: mock_response)
    monkeypatch.setattr(main, "get_api_url", lambda path: "http://api")
    result = runner.invoke(main.app, ["list-files"])
    assert "Following files are saved" in result.output


def test_list_files_empty(monkeypatch):
    mock_response = mock.Mock(status_code=200, json=lambda: [])
    monkeypatch.setattr(main, "get_file_list", lambda **kwargs: mock_response)
    monkeypatch.setattr(main, "get_api_url", lambda path: "http://api")
    result = runner.invoke(main.app, ["list-files"])
    assert "No files found" in result.output


def test_list_files_failure(monkeypatch):
    mock_response = mock.Mock(status_code=400, text="fail")
    monkeypatch.setattr(main, "get_file_list", lambda **kwargs: mock_response)
    monkeypatch.setattr(main, "get_api_url", lambda path: "http://api")
    result = runner.invoke(main.app, ["list-files"])
    assert "Failed to retrieve file list" in result.output
