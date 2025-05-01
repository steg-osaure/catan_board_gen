"""Module containing the Tile class."""

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
        self.default_options: dict[str, list[int | str]] = {
            "number": list(range(2, 7)) + list(range(8, 13)),
            "ressource": Tile.ressource_list.copy(),
        }

        self.default_value: dict[str, int | str] = {
            "number": 0,
            "ressource": None,
        }

        # info for Wave Function Collapse
        self.collapsed: dict[str:bool] = {"number": False, "ressource": False}
        self.options: dict[str : list[str | int]] = self.default_options.copy()
        self.value: dict[str, int | str] = self.default_value.copy()

        # self.reset_collapse("ressource")
        # self.reset_collapse("number")

    def reset_collapse(self, type: str) -> None:
        """Reset the collapse state for a specific attribute ('number' or 'ressource').

        Args:
            type (str): The attribute to reset. Must be either 'number' or 'ressource'.
        """
        self.collapsed[type] = False

        if type == "number" and self.value["ressource"] == "desert":
            self.options[type] = []
            self.collapsed[type] = True
            self.value[type] = 7
            return

        self.options[type] = self.default_options[type]
        self.collapsed[type] = False
        self.value[type] = self.default_value[type]

    def collapse(self, type: str) -> None:
        """Collapse a specific attribute by selecting a single, random  value among the tile's options.

        Args
            type (str): The attribute to collapse ('number' or 'ressource').
        """

        r.shuffle(self.options[type])
        self.value[type] = self.options[type][0]
        self.options[type] = []
        self.collapsed[type] = True

    def print_info(self) -> None:
        """Print the tile's details."""
        print(f'({self.x}, {self.y}) {self.value["ressource"]} {self.value["number"]}, {self.options["ressource"]}, {self.options["number"]}')
