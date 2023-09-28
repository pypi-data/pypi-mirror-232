"""./tests/test_crumbcutter.py"""

from unittest.mock import patch

import requests

import click
import click.testing
import crumbcutter
import pytest

SAMPLE_GIST = {
    "description": "sample_gist",
    "files": {
        "crumbcutter.json": {
            "raw_url": "https://gist.githubusercontent.com/jonathanagustin/957047cb8d5275d46ba2a0360a789e86/raw/2786d9bd8254ae2c15374cb5f7ee6871881ba192/crumbcutter.json"
        },
        "template.txt": {
            "raw_url": "https://gist.githubusercontent.com/jonathanagustin/957047cb8d5275d46ba2a0360a789e86/raw/27b3448465f32f8e19f415867314930c18401ae8/index.html"
        },
    },
}

SAMPLE_INVALID_GIST = {"description": "invalid_gist", "files": {}}


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        @staticmethod
        def json():
            return [SAMPLE_GIST]

        def raise_for_status(self):
            pass

        text = '{"project_name": "sample_project"}'
        status_code = 200

    return MockResponse()


def mocked_requests_500_error(*args, **kwargs):
    class MockResponse:
        def raise_for_status(self):
            raise requests.exceptions.HTTPError("Mocked 500 Error")

        status_code = 500

    return MockResponse()


def mocked_requests_invalid_json(*args, **kwargs):
    class MockResponse:
        def json(self):
            raise ValueError("Invalid JSON")

        def raise_for_status(self):
            pass

        status_code = 200

    return MockResponse()


@patch("crumbcutter.fetch_gist", return_value=SAMPLE_GIST)
def test_fetch_gist(mock_fetch_gist):
    gist = crumbcutter.fetch_gist("sample_user", "sample_gist")
    mock_fetch_gist.assert_called_once_with("sample_user", "sample_gist")
    assert gist == SAMPLE_GIST


@patch("crumbcutter.fetch_gist", side_effect=ValueError("Invalid JSON"))
def test_fetch_gist_invalid_json(mock_fetch_gist):
    with pytest.raises(ValueError, match="Invalid JSON"):
        crumbcutter.fetch_gist("sample_user", "sample_gist")


def test_validate_gist():
    assert crumbcutter.validate_gist(SAMPLE_GIST)
    with pytest.raises(ValueError):
        crumbcutter.validate_gist(SAMPLE_INVALID_GIST)


@patch("requests.get", side_effect=mocked_requests_get)
def test_extract_content_from_gist(mock_get):
    json_content, template, filename = crumbcutter.extract_content_from_gist(SAMPLE_GIST)
    assert json_content == {"project_name": "sample_project"}
    assert template == '{"project_name": "sample_project"}'
    assert filename == "template.txt"


def test_fetch_nonexistent_gist():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = []
        with pytest.raises(ValueError, match=r"Gist not found"):
            crumbcutter.fetch_gist("nonexistent_user", "nonexistent_gist")


@patch("requests.get", side_effect=mocked_requests_get)
def test_extract_content_no_crumbcutter(mock_get):
    modified_gist = SAMPLE_GIST.copy()
    if "crumbcutter.json" in modified_gist["files"]:
        modified_gist["files"].pop("crumbcutter.json")
    json_content, template, filename = crumbcutter.extract_content_from_gist(modified_gist)
    assert json_content == {}
    assert template == '{"project_name": "sample_project"}'
    assert filename == "template.txt"


def test_main_no_input():
    with patch("cookiecutter.prompt.prompt_for_config") as mock_prompt:
        mock_prompt.return_value = {"project_name": "test_project"}
        with patch("crumbcutter.crumbcutter.fetch_gist", return_value=SAMPLE_GIST):
            runner = click.testing.CliRunner()
            runner.invoke(crumbcutter.main, ["sample_user/sample_gist", "--no-input"])


def test_main_with_input():
    with patch("cookiecutter.prompt.prompt_for_config") as mock_prompt:
        mock_prompt.return_value = {"project_name": "test_project"}
        with patch("crumbcutter.crumbcutter.fetch_gist", return_value=SAMPLE_GIST):
            runner = click.testing.CliRunner()
            runner.invoke(crumbcutter.main, ["sample_user/sample_gist"])


def test_cli_verbose_mode():
    runner = click.testing.CliRunner()
    with patch("crumbcutter.crumbcutter.fetch_gist", return_value=SAMPLE_GIST):
        result = runner.invoke(crumbcutter.main, ["sample_user1/sample_gist99", "-v"])
        assert "Running in verbose mode..." in result.output


def test_cli_invalid_url_format():
    runner = click.testing.CliRunner()
    result = runner.invoke(crumbcutter.main, ["invalid_format"])
    assert "Invalid format <username>/<gist-name>" in result.output


@patch("requests.get", side_effect=mocked_requests_500_error)
def test_fetch_gist_server_error(mock_get):
    with pytest.raises(requests.exceptions.HTTPError, match="Mocked 500 Error"):
        crumbcutter.fetch_gist("sample_user", "sample_gist")


SAMPLE_GIST_NO_TEMPLATE = {
    "description": "sample_gist",
    "files": {
        "crumbcutter.json": {
            "raw_url": "https://gist.githubusercontent.com/jonathanagustin/957047cb8d5275d46ba2a0360a789e86/raw/2786d9bd8254ae2c15374cb5f7ee6871881ba192/crumbcutter.json"
        },
    },
}


def test_extract_content_no_template():
    with pytest.raises(ValueError, match="No template file found in the gist"):
        crumbcutter.extract_content_from_gist(SAMPLE_GIST_NO_TEMPLATE)


def test_validate_empty_gist():
    with pytest.raises(ValueError, match="Gist is empty"):
        crumbcutter.validate_gist({})


def test_validate_username_gistname_pair_valid():
    username, gist_name = crumbcutter.validate_username_gistname_pair("sample_user/sample_gist")
    assert username == "sample_user"
    assert gist_name == "sample_gist"


def test_validate_username_gistname_pair_invalid_format():
    with pytest.raises(ValueError, match=r"Invalid format for username_gistname_pair"):
        crumbcutter.validate_username_gistname_pair("sample_user_sample_gist")


def test_validate_username_gistname_pair_invalid_characters():
    with pytest.raises(ValueError, match=r"Invalid GitHub username format"):
        crumbcutter.validate_username_gistname_pair("sample!user/sample_gist")

    with pytest.raises(ValueError, match=r"Invalid gist name format"):
        crumbcutter.validate_username_gistname_pair("sample_user/sample!gist")


def test_validate_username_gistname_pair_empty_parts():
    with pytest.raises(ValueError, match=r"Neither username nor gist name can be empty."):
        crumbcutter.validate_username_gistname_pair("/sample_gist")

    with pytest.raises(ValueError, match=r"Neither username nor gist name can be empty."):
        crumbcutter.validate_username_gistname_pair("sample_user/")


@patch("crumbcutter.fetch_gist", return_value=SAMPLE_GIST)
def test_main_invalid_username_format(mock_fetch_gist):
    with patch("crumbcutter.crumbcutter.fetch_gist", return_value=SAMPLE_GIST):
        runner = click.testing.CliRunner()
        runner.invoke(crumbcutter.main, ["sample!user/sample_gist"])


@patch("crumbcutter.fetch_gist", return_value=SAMPLE_GIST)
def test_main_invalid_gistname_format(mock_fetch_gist):
    with patch("crumbcutter.crumbcutter.fetch_gist", return_value=SAMPLE_GIST):
        runner = click.testing.CliRunner()
        runner.invoke(crumbcutter.main, ["sample_user/sample!gist"])
