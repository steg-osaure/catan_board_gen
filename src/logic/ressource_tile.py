"""Module containing the Tile class."""

from typing import Any

import random as r
from logic.tile import Tile


class RessourceTile(Tile):
    """Represents a resource-producing tile on the Catan board.

    Inherits from the Tile class and supports collapse mechanics for assigning resources and number tokens
    using a Wave Function Collapse-inspired approach.

    Attributes:
        collapsed (dict[str, bool]): Tracks whether the resource or number has been finalized.
        options (dict[str, list[str | int]]): Possible values still available for resource and number assignment.
        value (dict[str, str | int]): The currently assigned resource and number (may be incomplete).
        default_options (dict[str, list[str | int]]): Initial option pool for both attributes.
        default_value (dict[str, str | int]): Placeholder values before collapse.
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialize an un-collapsed RessourceTile instance.

        Args:
            x (int): The x-coordinate of the tile in hex grid space.
            y (int): The y-coordinate of the tile in hex grid space.
        """
        # store x, y (hex coordinates)
        super().__init__(x, y)

        # Default options for the Wave Function Collapse
        self.default_options: dict[str, Any] = {
            "number": list(range(2, 7)) + list(range(8, 13)),
            "ressource": Tile.ressource_list.copy(),
        }

        self.default_value: dict[str, Any] = {
            "number": 0,
            "ressource": "None",
        }

        # info for Wave Function Collapse
        self.collapsed: dict[str, bool] = {"number": False, "ressource": False}
        self.options: dict[str, Any] = self.default_options.copy()
        self.value: dict[str, Any] = self.default_value.copy()

        # self.reset_collapse("ressource")
        # self.reset_collapse("number")

    def reset_collapse(self, attribute: str) -> None:
        """Reset the collapse state for a specific attribute ('number' or 'ressource').

        Args:
            attribute (str): The attribute to reset. Must be either 'number' or 'ressource'.
        """
        self.collapsed[attribute] = False

        if attribute == "number" and self.value["ressource"] == "desert":
            self.options[attribute] = []
            self.collapsed[attribute] = True
            self.value[attribute] = 7
            return

        self.options[attribute] = self.default_options[attribute]
        self.collapsed[attribute] = False
        self.value[attribute] = self.default_value[attribute]

    def collapse(self, attribute: str) -> None:
        """Collapse a specific attribute by selecting a single, random  value among the tile's options.

        Args
            attribute (str): The attribute to collapse ('number' or 'ressource').
        """

        r.shuffle(self.options[attribute])
        self.value[attribute] = self.options[attribute][0]
        self.options[attribute] = []
        self.collapsed[attribute] = True

    def print_info(self) -> None:
        """Print the tile's details."""
        print(f'({self.x}, {self.y}) {self.value["ressource"]} {self.value["number"]}, {self.options["ressource"]}, {self.options["number"]}')

    def get_info_text(self) -> str:
        return f"Ressource Tile\nCoordinates: ({self.x}, {self.y})\nRessource: {self.value['ressource']}\nNumber: {self.value['number']}"
