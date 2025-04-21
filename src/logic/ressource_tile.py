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
        res_options (list): Possible resource types for the tile.
    """

    def __init__(self, x: int = 0, y: int = 0, ressource: str = "desert", number: int = None):
        """Initialize a Tile instance.

        Args:
            x (int, optional): The x-coordinate of the tile in hex grid space. Defaults to 0.
            y (int, optional): The y-coordinate of the tile in hex grid space. Defaults to 0.
            ressource (str, optional): The type of resource the tile represents.\
                Defaults to "desert".
            number (int, optional): The number token value assigned to this tile. Defaults to None.
        """
        # store x, y (hex coordinates)
        super().__init__(x, y)

        # store ressource
        self.ressource = ressource

        # store number
        self.number = number

        # info for Wave Function Collapsed for numbers
        self.num_collapsed = False
        self.num_options = list(range(2, 7)) + list(range(8, 13))

        # info for WFC for ressources
        self.res_collapsed = False
        self.res_options = []

    def num_collapse(self, num=None):
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
            return True

        r.shuffle(self.num_options)
        self.number = self.num_options[0]
        self.num_collapsed = True
        return True

    def res_collapse(self, res=None):
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
            self.res_options = []
            self.res_collapsed = True
            return True

        r.shuffle(self.res_options)
        self.ressource = self.res_options[0]
        self.res_collapsed = True
        return True

    def Print(self):
        """Print the tile's details.

        Returns:
            str: A string representation of the tile's coordinates, resource type, and number token.
        """
        print(f"({self.x}, {self.y}) {self.ressource} {self.number}")
