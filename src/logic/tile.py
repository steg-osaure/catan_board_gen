"""Module containing the Tile class."""

from abc import abstractmethod
import random as r


class Tile:
    """Represents a single tile on the Catan board.
    This is the mother class, specific tile types (resource tiles, ports, sea) should inherit from this class.

    Attributes:
        x (int): The x-coordinate of the tile in hex grid space.
        y (int): The y-coordinate of the tile in hex grid space.
    """

    relative_neighbours = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]

    # coordinates of the corners
    # in hex grid coordinates:
    # corners = [
    #    (1 / 3, 1 / 3),
    #    (-1 / 3, 2 / 3),
    #    (-2 / 3, 1 / 3),
    #    (-1 / 3, -1 / 3),
    #    (1 / 3, -2 / 3),
    #    (2 / 3, -1 / 3),
    # ]

    def __init__(self, x: int, y: int) -> None:
        """Initialize a Tile instance.

        Args:
            x (int): The x-coordinate of the tile in hex grid space.
            y (int): The y-coordinate of the tile in hex grid space.
        """

        # store x, y (hex coordinates)
        self.x, self.y = x, y

    def get_coords(self) -> tuple[int, int]:
        """Getter for (self.x, self.y) tile coordinates."""
        return (self.x, self.y)

    def neighbours(self) -> list[tuple[int, int]]:
        """Calculate the coordinates of neighboring tiles in the hex grid.

        Uses the tile's current position to determine the coordinates of its six neighbors.

        Returns:
            list: A list of tuples representing the coordinates of the neighboring tiles.
        """

        return [(i[0] + self.x, i[1] + self.y) for i in self.relative_neighbours]
