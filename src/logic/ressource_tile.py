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
        """Initialize a Tile instance.

        Args:
            x (int): The x-coordinate of the tile in hex grid space. Defaults to 0.
            y (int): The y-coordinate of the tile in hex grid space. Defaults to 0.
            ressource (str): The type of resource the tile represents.\
                Defaults to "desert".
            number (int): The number token value assigned to this tile. Defaults to None.
        """
        # store x, y (hex coordinates)
        super().__init__(x, y)

        # store ressource
        self.ressource: str
        self.number: int

        # info for Wave Function Collapsed for numbers
        self.num_collapsed: bool
        self.num_options: list[int]

        # info for WFC for ressources
        self.res_collapsed: bool
        self.ressource_options: list[str]

        self.reset_ressource_options()
        self.reset_number_options()

    def reset_number_options(self) -> None:
        """Reset the number options for the tile.

        This method clears the current number options and reinitializes them
        to the default range of values (2-6, 8-12).
        """
        if self.res_collapsed and self.ressource == "desert":
            self.num_options = []
            self.num_collapsed = True
            self.number = 7
            return

        self.num_options = list(range(2, 7)) + list(range(8, 13))
        self.num_collapsed = False
        self.number = 0

    def reset_ressource_options(self) -> None:
        """Reset the resource options for the tile.

        This method clears the current resource options and reinitializes them
        to the default list of resources.
        """
        self.ressource_options = self.ressource_list.copy()
        self.res_collapsed = False
        self.ressource = "None"

    def num_collapse(self, num: int | None = None) -> None:
        """Assign a number token to the tile using Wave Function Collapse.

        If a specific number is provided, it is directly assigned. Otherwise,
        the method randomly selects from available options.

        Args:
            num (int, optional): A specific number token to assign to the tile.
                                If not provided, one is randomly chosen.

        Returns:
            bool: True if the number was successfully assigned, False otherwise.
        """

        # option to manually set the number to collapse to
        if num is not None:
            self.number = num
            self.num_options = []
            self.num_collapsed = True
            return

        r.shuffle(self.num_options)
        self.number = self.num_options[0]
        self.num_collapsed = True

    def res_collapse(self, res: str | None = None) -> None:
        """Assign a resource type to the tile using Wave Function Collapse.

        If a specific resource is provided, it is directly assigned. Otherwise,
        the method randomly selects from available options.

        Args:
            res (str, optional): A specific resource type to assign to the tile.
                                If not provided, one is randomly chosen.

        Returns:
            bool: True if the resource was successfully assigned, False otherwise.
        """

        # option to manually set the ressource to collapse to
        if res is not None:
            self.ressource = res
            self.ressource_options = []
            self.res_collapsed = True
            return

        r.shuffle(self.ressource_options)
        self.ressource = self.ressource_options[0]
        self.res_collapsed = True

    def print_info(self) -> None:
        """Print the tile's details.

        Returns:
            str: A string representation of the tile's coordinates, resource type, and number token.
        """
        print(f"({self.x}, {self.y}) {self.ressource} {self.number}")
