
import argparse
import typer
import json

from typing import Optional
from typing_extensions import Annotated

from winner.setup import Initialize

app = typer.Typer()

class Cli:
    def __init__(self):
        self.parser = argparse.ArgumentParser()

    def run(self):
        print("In Cli run")
        self.parser.parse_args()
        pass

    def setVenv(self, path):
        i = Initialize()


@app.command("init_venv")
def initVenv(path: str, env: Annotated[Optional[str], typer.Argument(help="The environment variables to be set to be passed as a json object string eg: {'PORT'=5800, 'HOST'=localhost}")] = None):
    ''' 
        Initialize the Virtual Environment
    '''
    i = Initialize(path)
    i.create_virtual_env(path)
    if (env != None):
        envDict = json.loads(env)
        i.set_in_env(envDict)
    # i.install_packages()

@app.command()
def installPackages(path: Annotated[str, typer.Option(help="Path to the initialized virtual environment")],
                    requirements: Annotated[str, typer.Option(help="The pip requirements file to be installed")]="requirements.txt"
                    ):
    '''
        Install the packages from the requirements file
    '''
    i = Initialize(path)
    i.open_virtual_env(path)
    i.install_packages(requirements)

@app.command("run")
def runInVenv(path: Annotated[str, typer.Option(help="Path to the initialized virtual environment")], 
              program: Annotated[str, typer.Option(help="The python program and its args to be run")],
              env: Annotated[Optional[str], typer.Option(help="The environment variables to be set to be passed as a json object string eg: {'PORT'=5800, 'HOST'=localhost}")] = None
              ):
    '''
        Initialize a Virtual Environment on the given path and install requirements
    '''
    i = Initialize(path)
    i.open_virtual_env(path)
    if (env != None):
        envDict = json.loads(env)
        if (type(envDict) is list):
            envList = envDict
            envDict = {}
            for e in envList:
                if "=" in e:
                    key, value = e.split("=")
                    envDict[key] = value
        i.set_in_env(envDict)
    i.run(program)
