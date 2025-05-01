"""Method containing the class to store the different option settings"""

import json
from pathlib import Path


class OptionHandler:
    """Handles configurable script options defined in a JSON file.

    This class loads toggleable options from a JSON file, each of which includes
    a default value, UI text, and description. These options are typically used
    for controlling behavior and constraints in a game setup UI.

    Attributes:
        options (dict): A dictionary mapping option keys to their metadata and state.
    """

    def __init__(self, option_path: Path) -> None:
        """Initialize the OptionHandler and load options from a JSON file.

        Each option is initialized with its default value and associated metadata
        (box text and description).

        Args:
            option_path (Path): Path to the JSON file containing the options.
        """
        with open(option_path, "r") as option_file:
            self.options = json.load(option_file)

        for key in self.options.keys():
            self.options[key].update({"value": self.options[key]["default"]})

    def get_option(self, key: str) -> bool:
        """Retrieve the current value of a specific option.

        Args:
            key (str): The option key.

        Returns:
            bool: The current value (True/False) of the option.
        """
        return self.options[key]["value"]

    def set_option(self, key: str, value: bool) -> None:
        """Set a specific option to the given value.

        Args:
            key (str): The option key.
            value (bool): The new value to set.
        """
        self.options[key]["value"] = value

    def toggle_option(self, key: str) -> None:
        """Toggle the boolean value of a specific option.

        Args:
            key (str): The option key to toggle.
        """
        self.options[key]["value"] = not self.options[key]["value"]

    def get_all(self) -> list[str]:
        """Get a list of all available option keys.

        Returns:
            list[str]: A list of all option keys.
        """
        return list(self.options.keys())

    def get_box_text(self, key: str) -> str:
        """Get the UI label (box text) associated with a specific option.

        Args:
            key (str): The option key.

        Returns:
            str: The text displayed on the UI checkbox or toggle.
        """
        return self.options[key]["box_text"]

    def get_description(self, key: str) -> str:
        """Get the detailed description of what a specific option does.

        Args:
            key (str): The option key.

        Returns:
            str: The option's description, often shown as a tooltip or help text.
        """
        return self.options[key]["description"]
