import subprocess
import os
import tomllib

import requests
from cleo.commands.command import Command
from cleo.helpers import argument


class publish(Command):
    name = "publish"
    description = ""
    arguments = [argument("token", description="gh_token")]

    def handle(self):
        resp = requests.get(
            "https://api.github.com/repos/misspy-development/misspy/releases/latest"
        )
        resp = resp.json()
        token = self.argument("token")
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
            pyproject["tool.poetry"]["version"] = resp["tag_name"]
        subprocess.run(
            f"git remote set-url origin https://{token}@github.com/misspy-development/misspy.git",
            shell=True,
        )
        subprocess.run("poetry config pypi-token.pypi " + os.environ.get('PYPI_TOKEN'))
        subprocess.run('git commit -m "update toml version"', shell=True)
        subprocess.run("git push origin develop", shell=True)
        subprocess.run("git checkout master", shell=True)
        subprocess.run("git merge develop", shell=True)
        subprocess.run("git push origin master", shell=True)
        subprocess.run("poetry publish --build", shell=True)