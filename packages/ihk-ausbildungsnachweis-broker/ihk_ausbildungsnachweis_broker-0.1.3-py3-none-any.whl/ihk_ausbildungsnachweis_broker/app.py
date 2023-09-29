#!/usr/bin/env python
# encoding: utf-8
import json
import os
import time

from flask import Flask
from werkzeug.exceptions import HTTPException, NotFound

from ihk_ausbildungsnachweis_broker.azubi_repo import AzubiRepo


flask_app = app = Flask("ihk_ausbildungsnachweis_broker")

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
AUSBILDER_WHITELIST = os.environ["AUSBILDER_WHITELIST"]


@flask_app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


@flask_app.route("/repo/<org>/<repo>/sign")
def sign(org: str, repo: str):
    azubi_repo = AzubiRepo(org, repo, GITHUB_TOKEN, AUSBILDER_WHITELIST)

    print(azubi_repo.local_repo_dirpath)

    azubi_repo.revert_unapproved_commits()
    azubi_repo.sign_ausbildungsnachweise()
    azubi_repo.push("master")


@flask_app.route("/repo/<org>/<repo>/<branch>/build")
def build(org: str, repo: str, branch: str):
    azubi_repo = AzubiRepo(org, repo, GITHUB_TOKEN, AUSBILDER_WHITELIST)

    print(azubi_repo.local_repo_dirpath)

    azubi_repo.checkout(branch)
    azubi_repo.build_ausbildungsnachweise(branch)
    azubi_repo.push(branch)

    return json.dumps({"status": "0"})


@flask_app.route("/")
def index():
    raise NotFound


def start():
    flask_app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    start()
