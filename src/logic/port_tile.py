"""Module containing the Tile class."""

from logic.tile import Tile


class PortTile(Tile):
    """Represents a single port tile on the Catan board.

    Attributes:
        x (int): The x-coordinate of the tile in hex grid space.
        y (int): The y-coordinate of the tile in hex grid space.
        coords (tuple): A tuple containing the (x, y) coordinates of the tile.
        ressource (str): The type of resource this tile represents (e.g., "brick", "wood").
        number (int): The number token value assigned to this tile.
        num_collapsed (bool): Whether the number has been assigned (collapsed) for this tile.
        num_options (list): Possible number token values for the tile.
        res_collapsed (bool): Whether the resource has been assigned (collapsed) for this tile.
        res_options (list): Possible resource types for the tile.
    """

    def __init__(self, x: int, y: int, ressource: str, orientation: int) -> None:
        """Initialize a Tile instance.

        Args:
            x (int): The x-coordinate of the tile in hex grid space. Defaults to 0.
            y (int): The y-coordinate of the tile in hex grid space. Defaults to 0.
            ressource (str): The type of resource the tile represents.\
                Defaults to "desert".
            number (int): The number token value assigned to this tile. Defaults to None.
        """
        super().__init__(x, y)
        self.ressource = ressource
        self.orientation = orientation

    def print_info(self) -> None:
        """Print the tile's details."""
        print(f"({self.x}, {self.y}) {self.ressource} {self.orientation}")
