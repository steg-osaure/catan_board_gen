"""Method containing the class to store the different option settings"""

import json
from pathlib import Path


class OptionHandler:
    """Class to handle the options for the script"""

    def __init__(self, option_path: Path) -> None:
        """Initialize the option handler with default values"""

        with open(option_path, "r") as option_file:
            self.options = json.load(option_file)

        for key in self.options.keys():
            self.options[key].update({"value": self.options[key]["default"]})

    def get_option(self, key: str) -> bool:
        """Get the value of a specific option"""
        return self.options[key]["value"]

    def set_option(self, key: str, value: bool) -> None:
        """Set an option to a specific value"""
        self.options[key]["value"] = value

    def toggle_option(self, key: str) -> None:
        """Toggle the value of a specific option"""
        self.options[key]["value"] = not self.options[key]["value"]

    def get_all(self) -> list[str]:
        # return {key: self.options[key]["value"] for key in self.options.keys()}
        return list(self.options.keys())

    def get_box_text(self, key: str) -> str:
        """Get the text for the box"""
        return self.options[key]["box_text"]

    def get_description(self, key: str) -> str:
        """Get the description for the box"""
        return self.options[key]["description"]
