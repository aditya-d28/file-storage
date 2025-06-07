import json
import platform
from unittest import mock

import cli.service as service
import pytest


@pytest.fixture
def temp_config_dir(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return str(config_dir)


@pytest.fixture
def temp_config_file(tmp_path):
    config_file = tmp_path / "config.json"
    return str(config_file)


def test_get_config_dir_windows(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")
    result = service.get_config_dir()
    assert "file-storage-cli" in result
    assert result.startswith("C:\\Users\\Test\\AppData\\Roaming")


def test_get_config_dir_linux(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", "/home/test/.config")
    result = service.get_config_dir()
    assert "file-storage-cli" in result
    assert result.startswith("/home/test/.config")


def test_save_and_load_config(temp_config_dir, temp_config_file):
    service.save_config(temp_config_dir, temp_config_file, host="localhost", port=1234, api_url="http://test")
    config = service.load_config(temp_config_file)
    assert config["host"] == "localhost"
    assert config["port"] == 1234
    assert config["api_url"] == "http://test"


def test_load_config_missing_file(tmp_path):
    config_path = tmp_path / "missing.json"
    result = service.load_config(str(config_path))
    assert result is None


def test_get_api_url_with_api_url_key(temp_config_file):
    config = {"api_url": "http://custom:9000"}
    with open(temp_config_file, "w") as f:
        json.dump(config, f)
    url = service.get_api_url(temp_config_file)
    assert url == "http://custom:9000"


def test_get_api_url_with_host_port(temp_config_file):
    config = {"host": "myhost", "port": 5555}
    with open(temp_config_file, "w") as f:
        json.dump(config, f)
    url = service.get_api_url(temp_config_file)
    assert url == "http://myhost:5555"


def test_get_api_url_no_config(monkeypatch, tmp_path):
    config_path = tmp_path / "no_config.json"
    with mock.patch.object(service.logger, "debug") as mock_debug:
        url = service.get_api_url(str(config_path))
        assert url == service.API_URL
        mock_debug.assert_called()


@mock.patch("cli.service.requests.post")
def test_upload_file_to_storage_success(mock_post, tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("data")
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = mock.Mock()
    mock_post.return_value = mock_response

    resp = service.upload_file_to_storage("http://api", file_path, "test.txt")
    assert resp.status_code == 200
    mock_post.assert_called_once()


@mock.patch("cli.service.requests.post")
def test_upload_file_to_storage_failure(mock_post, tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("data")
    mock_response = mock.Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status = mock.Mock()
    mock_post.return_value = mock_response

    resp = service.upload_file_to_storage("http://api", file_path, "test.txt")
    assert resp.status_code == 400


@mock.patch("cli.service.requests.post")
def test_upload_file_to_storage_exception(mock_post, tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("data")
    mock_post.side_effect = Exception("fail")
    with pytest.raises(Exception):
        service.upload_file_to_storage("http://api", file_path, "test.txt")


@mock.patch("cli.service.requests.delete")
def test_delete_file_from_storage_success(mock_delete):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = mock.Mock()
    mock_delete.return_value = mock_response

    resp = service.delete_file_from_storage("http://api", "test.txt")
    assert resp.status_code == 200
    mock_delete.assert_called_once()


@mock.patch("cli.service.requests.delete")
def test_delete_file_from_storage_failure(mock_delete):
    mock_response = mock.Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status = mock.Mock()
    mock_delete.return_value = mock_response

    resp = service.delete_file_from_storage("http://api", "test.txt")
    assert resp.status_code == 404


@mock.patch("cli.service.requests.delete")
def test_delete_file_from_storage_exception(mock_delete):
    mock_delete.side_effect = Exception("fail")
    with pytest.raises(Exception):
        service.delete_file_from_storage("http://api", "test.txt")


@mock.patch("cli.service.requests.get")
def test_get_file_list_success(mock_get):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = mock.Mock()
    mock_get.return_value = mock_response

    resp = service.get_file_list("http://api")
    assert resp.status_code == 200
    mock_get.assert_called_once()


@mock.patch("cli.service.requests.get")
def test_get_file_list_failure(mock_get):
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status = mock.Mock()
    mock_get.return_value = mock_response

    resp = service.get_file_list("http://api")
    assert resp.status_code == 500


@mock.patch("cli.service.requests.get")
def test_get_file_list_exception(mock_get):
    mock_get.side_effect = Exception("fail")
    with pytest.raises(Exception):
        service.get_file_list("http://api")
