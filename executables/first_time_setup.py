#!/usr/bin/env python

import os
import pwd
import json
import getpass
import platform
import subprocess
from pathlib import Path


class EnvironmentSetup:
    """Handles the setup of the catan_board_gen environment."""

    def __init__(self) -> None:
        """Initialize environment setup."""
        self.user = getpass.getuser()
        self.config_file = Path(f"./settings/{self.user}.json")
        self.python_version = platform.python_version()

        self.load_config()
        self.load_user_settings()

    def load_config(self) -> None:
        """Load the user config file or create a default one if it doesn't exist."""
        if not self.config_file.exists():
            print(f"  --> {self.config_file} does not exist. Creating default config.")
            self.create_default_config()

        with self.config_file.open("r") as config_file:
            self.config = json.load(config_file)

    def create_default_config(self) -> None:
        """Create a default configuration file for the user."""
        shell = (
            "sh"
            if (pwd.getpwuid(os.getuid()).pw_shell.split("/")[-1] in ["bash", "zsh"])
            else "csh"
        )
        cbgen_path = os.getcwd()

        try:
            output_path = Path(f"/eos/user/{self.user[0]}/{self.user}/")
            if not output_path.exists():
                output_path = Path(cbgen_path)
        except Exception:  # pylint: disable=W0718
            output_path = Path(cbgen_path)

        config = {
            "username": self.user,
            "shell": shell,
            "cbgen": cbgen_path,
        }

        with self.config_file.open("w") as outfile:
            json.dump(config, outfile, indent=4)
        print(f"Default config created for user '{self.user}':")
        print(json.dumps(config, indent=8))

    def load_user_settings(self) -> None:
        """Load user-specific settings from the configuration."""
        self.user_cbgen = self.config["cbgen"]
        self.user_shell = self.config["shell"]

    def get_setup_env(self) -> str:
        """Generate the environment setup script."""
        lines = ["#!/bin/bash"]

        # Add commands to set up the virtual Python environment.
        lines.append("# Virtual python environment: beeware")
        lines = check_folder(
            lines=lines,
            command="python3 -m venv beeware",
            directory="beeware",
        )
        lines.append("")
        lines.append("source beeware/bin/activate")
        lines.append("")

        return "\n".join(lines)

    def get_paths(self) -> str:
        """Generate the environment paths for the setup."""
        action, sep = ("export", "=")
        # Generate shell commands for exporting or setting environment variables.
        lines = [
            "# Path for catan_board_gen environment",
            f"{action} CBGEN_PATH{sep}{os.getcwd()}",
            f"{action} PATH{sep}${{CBGEN_PATH}}/executables:${{PATH}}",
            f"{action} PYTHONPATH{sep}${{CBGEN_PATH}}:${{PYTHONPATH}}",
            "",
            "# Path for beeware environment",
            f"{action} PATH{sep}${{CBGEN_PATH}}/beeware/bin:${{PATH}}",
            f"{action} PYTHONPATH{sep}${{CBGEN_PATH}}/beeware/lib/{self.python_version}/site-packages:${{PYTHONPATH}}",
            f"{action} PYTHONPATH{sep}${{CBGEN_PATH}}/beeware/lib64/{self.python_version}/site-packages:${{PYTHONPATH}}",
            "",
        ]
        return "\n".join(lines)

    def get_dependencies(self) -> str:
        """Generate the setup commands for dependencies."""
        lines = []
        req_scripts = "settings/requirements.txt"
        req_beeware = "beeware/requirements.txt"
        pip_install_cmd = "python -m pip install --force-reinstall"

        # TODO: packages dependencies for linux
        # ubuntu:
        # sudo apt update
        # sudo apt install git build-essential pkg-config python3-dev python3-venv libgirepository1.0-dev libcairo2-dev gir1.2-gtk-3.0 libcanberra-gtk3-module

        # Ensure beeware requirements file exists and is updated
        lines = check_file(
            lines,
            command=f"cp {req_scripts} {req_beeware}\n    python -m pip install pip==23.1.2\n    {pip_install_cmd} -r {req_scripts}",
            file_to_check=req_beeware,
        )
        lines = diff_file(
            lines,
            command=f"cp {req_scripts} {req_beeware}\n    {pip_install_cmd} -r {req_scripts}",
            file1=req_scripts,
            file2=req_beeware,
        )
        lines.append("")

        return "\n".join(lines)

    def get_logo(self) -> str:
        """Return the command to display the catan_board_gen logo."""
        return "cat settings/cbgen-logo"

    def get_environment_summary(self) -> str:
        """Return commands to print out the environment settings."""
        return "\n".join(
            [
                "echo ''",
                "echo 'INFO :: Printing out environment settings ...'",
                "echo ''",
                "echo '  -->  CBGEN_PATH :: '$CBGEN_PATH",
                "echo '  -->  CBGEN_OUTPUTPATH :: '$CBGEN_OUTPUTPATH",
                "echo ''",
            ]
        )

    def generate_setup(self) -> None:
        """Generate the setup environment script."""
        with open("./setup_environment.sh", "w") as outputfile:
            outputfile.write(self.get_setup_env() + "\n")
            outputfile.write(self.get_paths() + "\n")
            outputfile.write(self.get_dependencies() + "\n")
            outputfile.write(self.get_logo() + "\n")
            outputfile.write(self.get_environment_summary() + "\n")


def check_folder(lines: list[str], command: str, directory: str) -> list[str]:
    """Check if a folder exists and create it if it doesn't."""
    lines.extend([f'if ! [ -d "{directory}" ] ; then', f"    {command}", "fi"])
    return lines


def check_file(lines: list[str], command: str, file_to_check: str) -> list[str]:
    """Append shell commands to check if a file exists and execute a command if not."""
    lines.extend([f'if ! [ -f "{file_to_check}" ] ; then', f"    {command}", "fi"])
    return lines


def diff_file(lines: list[str], command: str, file1: str, file2: str) -> list[str]:
    """Append shell commands to check if two files differ and execute a command if they do."""
    diff_command = f"diff {file1} {file2}"
    lines.extend(
        [
            f"if ! ( {diff_command} > /dev/null) then",
            f"    {diff_command}",
            f"    {command}",
            "fi",
        ]
    )
    return lines


def main() -> None:
    """Main entry point for the setup script."""
    print("INFO:: Starting first time setup for catan_board_gen")
    cbgen_env_setup = EnvironmentSetup()
    cbgen_env_setup.generate_setup()

    # with subprocess.Popen("chmod a+x setup_environment.sh", shell=True) as process:
    #    process.wait()

    print(
        "INFO:: catan_board_gen setup completed. Use `source setup_environment.sh` to initialize the environment."
    )


if __name__ == "__main__":
    main()
