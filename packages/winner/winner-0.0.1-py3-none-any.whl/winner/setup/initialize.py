
import os
import platform
import subprocess
import shlex

from typing import Dict


class Initialize:
    def __init__(self, path):
        self.env = os.environ.copy() 
        self.path = self._set_path(path)

    def _set_path(self, path):
        # get the absolute path from variable path
        self.vPath = os.path.abspath(path)
        fullPath = os.path.join(self.vPath, "bin")
        if platform.system() == "Windows":
            fullPath = os.path.join(self.vPath, "Scripts")
        self.path = fullPath

    def _set_venv_env(self):
        # set fullpath to the environment variable
        self.env["PATH"] = os.pathsep.join([self.path, self.env["PATH"]])

        # remove PYTHONHOME from environment variable
        if "PYTHONHOME" in self.env:
            del self.env["PYTHONHOME"]

    def create_virtual_env(self, path):
        # Create a new virtual environment
        subprocess.run(["python3", "-m", "venv", path])
        self.open_virtual_env(path)
        subprocess.run(["python3", "-m", "pip", "install", "--upgrade", "pip"])


    def open_virtual_env(self, path):
        self._set_path(path)
        self._set_venv_env()

        
    def set_in_env(self, env: Dict[str, str]):
        # Set the environment variable
        for key, value in env.items():
            self.env[key] = value
        return self.env

    def run(self, program_and_args):
        # Run the in the virtual environment the python program and its args
        if not type(program_and_args) is list:
            program_and_args = shlex.split(program_and_args)
        command = [self.get_py_cmd()] + program_and_args
        return subprocess.run(command, env=self.env, cwd=self.vPath)

    def get_pip_cmd(self):
        # Get the pip command
        return os.path.join(self.path, "pip3")

    def get_py_cmd(self):
        # Get the pip command
        return os.path.join(self.path, "python")

    def install_packages(self, requirementsFilename="requirements.txt"):
        # Install all the packages in the requirements.txt file
        pipCmd = self.get_pip_cmd()
        return subprocess.run([pipCmd, "install", "-r", requirementsFilename], env=self.env, cwd=self.vPath)

    def install_package(self, package):
        # Install a package
        pipCmd = self.get_pip_cmd()
        return subprocess.run([pipCmd, "install", package], env=self.env)

