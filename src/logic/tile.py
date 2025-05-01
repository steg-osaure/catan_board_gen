"""Module containing the Tile class."""


class Tile:
    """Base class representing a generic hexagonal tile on the Catan board.

    This abstract class provides coordinate handling and neighbor calculation for hex-based grid tiles.
    Specific types of tiles (e.g. resource tiles, sea tiles, or ports) should inherit from this class.

    Attributes:
        x (int): The x-coordinate in the hex grid.
        y (int): The y-coordinate in the hex grid.
        relative_neighbours (list[tuple[int, int]]): Relative offsets to neighboring tiles in a hex grid.
        ressource_list (list[str]): List of all possible resource types.
    """

    relative_neighbours = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    ressource_list: list[str] = ["brick", "wood", "sheep", "wheat", "stone", "desert"]

    def __init__(self, x: int, y: int) -> None:
        """Initialize a Tile instance at a given hex grid coordinate.

        Args:
            x (int): The x-coordinate of the tile in hex grid space.
            y (int): The y-coordinate of the tile in hex grid space.
        """

        # store x, y (hex coordinates)
        self.x, self.y = x, y

    def get_coords(self) -> tuple[int, int]:
        """Return the tile's coordinates in the hex grid.

        Returns:
            tuple[int, int]: A tuple (x, y) representing the tile's coordinates.
        """

        return (self.x, self.y)

    def neighbours(self) -> list[tuple[int, int]]:
        """Calculate and return the coordinates of the six neighboring tiles.

        Returns:
            list[tuple[int, int]]: List of coordinate tuples for neighboring tiles.
        """

        return [(i[0] + self.x, i[1] + self.y) for i in self.relative_neighbours]
