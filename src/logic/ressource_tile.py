"""Module containing the Tile class."""

import random as r
from logic.tile import Tile


class RessourceTile(Tile):
    """Represents a single tile on the Catan board.

    Attributes:
        x (int): The x-coordinate of the tile in hex grid space.
        y (int): The y-coordinate of the tile in hex grid space.
        ressource (str): The type of resource this tile represents (e.g., "brick", "wood").
        number (int): The number token value assigned to this tile.
        num_collapsed (bool): Whether the number has been assigned (collapsed) for this tile.
        num_options (list): Possible number token values for the tile.
        res_collapsed (bool): Whether the resource has been assigned (collapsed) for this tile.
        ressource_options (list): Possible resource types for the tile.
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialize an un-collapsed RessourceTile instance.

        Args:
            x (int): The x-coordinate of the tile in hex grid space.
            y (int): The y-coordinate of the tile in hex grid space.
        """
        # store x, y (hex coordinates)
        super().__init__(x, y)

        # store ressource
        self.ressource: str
        self.number: int

        self.default_options: dict[str, list[int | str]] = {
            "number": list(range(2, 7)) + list(range(8, 13)),
            "ressource": Tile.ressource_list.copy(),
        }

        self.default_value: dict[str, int | str] = {
            "number": 0,
            "ressource": None,
        }

        # info for Wave Function Collapsed
        self.collapsed: dict[str:bool] = {"number": False, "ressource": False}
        self.options: dict[str : list[str | int]] = self.default_options.copy()
        self.value: dict[str, int | str] = self.default_value.copy()

        # self.reset_collapse("ressource")
        # self.reset_collapse("number")

    def reset_collapse(self, type: str) -> None:
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

        r.shuffle(self.options[type])
        self.value[type] = self.options[type][0]
        self.options[type] = []
        self.collapsed[type] = True

    def print_info(self) -> None:
        """Print the tile's details."""
        print(f"({self.x}, {self.y}) {self.ressource} {self.number}, {self.ressource_options}, {self.num_options}")
