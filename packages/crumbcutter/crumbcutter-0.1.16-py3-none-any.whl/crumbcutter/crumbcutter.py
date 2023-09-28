"""./crumbcutter/crumbcutter.py"""
import json
import logging
import pathlib
import re

import requests

import click
from cookiecutter.prompt import prompt_for_config
from jinja2 import Environment, FileSystemLoader

GITHUB_API_BASE_URL = "https://api.github.com"
GIST_FETCH_LIMIT = 100
REQUEST_TIMEOUT = 60 * 5


def fetch_gist(username: str, gist_name: str) -> dict:
    """
    Fetch a specific gist by name from a user's gists.

    :param username: The GitHub username.
    :type username: str
    :param gist_name: The description name of the gist to fetch.
    :type gist_name: str
    :return: The gist data if found.
    :rtype: dict
    :raises ValueError: If the gist is not found.
    """
    page = 1
    while True:
        endpoint_url = f"{GITHUB_API_BASE_URL}/users/{username}/gists"
        query_params = {"per_page": GIST_FETCH_LIMIT, "page": page}
        response = requests.get(endpoint_url, params=query_params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        gists = response.json()
        if not gists:
            break

        for gist in gists:
            if gist["description"] == gist_name:
                return gist

        page += 1

    raise ValueError(f"Gist not found: {username}/{gist_name}")


def validate_gist(gist: dict) -> bool:
    """
    Validate the structure and content of a fetched gist.

    :param gist: The gist data fetched from GitHub.
    :type gist: dict
    :return: True if the gist is valid, otherwise raises a ValueError.
    :rtype: bool
    :raises ValueError: If the gist structure or content is not as expected.
    """
    if not gist:
        raise ValueError("Gist is empty")

    files = gist.get("files", {})

    if not files:
        raise ValueError("Gist has no files")

    if "crumbcutter.json" not in files and len(files) != 1:
        raise ValueError("Gist should have only one template file if crumbcutter.json is absent.")

    if "crumbcutter.json" in files and len(files) != 2:
        raise ValueError("Gist should have at most two files: crumbcutter.json and the template.")

    return True


def extract_content_from_gist(gist: dict) -> tuple:
    """
    Extract the configuration and template content from a valid gist.

    :param gist: The gist data fetched from GitHub.
    :type gist: dict
    :return: A tuple containing the configuration (if any), template content, and template filename.
    :rtype: tuple
    :raises ValueError: If no template file or if there's an error parsing.
    """
    files = gist.get("files", {})

    crumbcutter_json = {}
    if "crumbcutter.json" in files:
        crumbcutter_raw_url = files["crumbcutter.json"]["raw_url"]
        crumbcutter_text = requests.get(crumbcutter_raw_url, timeout=60 * 5).text
        del files["crumbcutter.json"]

        try:
            crumbcutter_json = json.loads(crumbcutter_text)
        except json.JSONDecodeError as ex:
            raise ValueError(f"Invalid crumbcutter.json: {ex}") from ex

    if not files:
        raise ValueError("No template file found in the gist")
    template_filename = list(files.keys())[0]
    template_url = files[template_filename]["raw_url"]
    template = requests.get(template_url, timeout=60 * 5).text

    return crumbcutter_json, template, template_filename


def validate_username_gistname_pair(pair: str) -> tuple:
    """
    Validate and extract username and gist name from the input pair.

    :param pair: The combined username and gist name.
    :type pair: str
    :return: Tuple containing username and gist name.
    :rtype: tuple
    :raises ValueError: If the input format is incorrect or doesn't match the expected pattern.
    """
    if pair.count("/") != 1:
        raise ValueError("Invalid format for username_gistname_pair. Expected format: 'username/gistname'")

    username, gist_name = pair.split(r"/", 1)

    if not username or not gist_name:
        raise ValueError("Neither username nor gist name can be empty.")

    username_pattern = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-_]{0,38}[a-zA-Z0-9])?$")
    gist_name_pattern = re.compile(r"^[a-zA-Z0-9-_\.]+$")

    if not username_pattern.match(username):
        raise ValueError(f"Invalid GitHub username format: {username}")

    if not gist_name_pattern.match(gist_name):
        raise ValueError(f"Invalid gist name format: {gist_name}")

    return username, gist_name


def run(username_gistname_pair: str, output_dir: str = ".", no_input: bool = False):
    """
    Main function to fetch a gist by a given username and gist name, then render and save its content.

    :param username_gistname_pair: The combined username and gist name in the format 'username/gistname'.
    :type username_gistname_pair: str
    :param output_dir: Directory where the rendered content should be saved, defaults to the current directory.
    :type output_dir: str, optional
    :param no_input: If True, it won't prompt the user for input and will use the provided configuration. Defaults to False.
    :type no_input: bool, optional
    """
    username, gist_name = validate_username_gistname_pair(username_gistname_pair)
    gist = fetch_gist(username, gist_name)
    validate_gist(gist)

    crumbcutter_json, template, template_filename = extract_content_from_gist(gist)

    if no_input:
        user_inputs = crumbcutter_json
    else:
        context = {"cookiecutter": crumbcutter_json}
        user_inputs = prompt_for_config(context)

    raw_project_name = crumbcutter_json.get("project_name", gist["description"])
    project_name = raw_project_name.lower().replace(" ", "_")
    if "project_name" not in user_inputs:
        user_inputs["project_name"] = project_name

    jinja_env = Environment(loader=FileSystemLoader("/"))
    jinja_template = jinja_env.from_string(template)
    rendered_content = jinja_template.render(cookiecutter=user_inputs, crumbcutter=user_inputs)

    output_path = pathlib.Path(output_dir) / template_filename
    output_path.write_text(rendered_content)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("username_gistname_pair", metavar="<username>/<gist-name>")
@click.option(
    "-o",
    "--output-dir",
    default=".",
    type=click.Path(),
    show_default=True,
    help="Directory where file will render to. Defaults to current directory.",
)
@click.option("--no-input", "-x", is_flag=True, help="eXtremely fast rendering. No user input. Use default values.")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose output for debugging.",
)
@click.version_option(version="0.1.11", prog_name="crumbcutter")
def main(username_gistname_pair: str, output_dir: str, no_input: bool, verbose: bool):
    """
    crumbcutter

        template a single-file GitHub gist

    - Template ONE gist file.
    - Nothing else!

    Use cookiecutter for more than one file.

    Given a GitHub username and gist name,
    crumbcutter fetches the gist, prompts for required inputs,
    and renders the template. The file is saved to a specified
    directory or current working directory if none specified.

    Usage:

        crumbcutter <username>/<gist-name>
        crumbcutter octocat/crumbcutter-file
    """
    if verbose:
        click.echo("Running in verbose mode...")
        logging.basicConfig(level=logging.DEBUG)
    try:
        run(username_gistname_pair, output_dir, no_input)
    except ValueError:
        click.echo("Invalid format <username>/<gist-name>")
    except Exception as ex:  # pylint: disable=broad-except
        click.echo(f"Error: {ex}", err=True)
        if verbose:
            logging.exception("Detailed error:")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
