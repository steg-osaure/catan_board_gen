"""Module containing the Tile class."""

from logic.tile import Tile


class PortTile(Tile):
    """Represents a port tile on the Catan board.

    Ports offer resource exchange advantages and are placed on the edge of the board.
    Each port may specialize in a specific resource or be generic (3:1 trade).

    Attributes:
        ressource (str): The resource type the port is associated with.
        orientation (int): The orientation index determining which side of the hexagon the port faces.
    """

    def __init__(self, x: int, y: int, ressource: str, orientation: int) -> None:
        """Initialize a PortTile with coordinates, associated resource, and orientation.

        Args:
            x (int): The x-coordinate of the tile in hex grid space.
            y (int): The y-coordinate of the tile in hex grid space.
            ressource (str): The resource type the port is associated with.
            orientation (int): The orientation index determining which side of the hexagon the port faces.
        """

        super().__init__(x, y)
        self.ressource = ressource
        self.orientation = orientation

    def print_info(self) -> None:
        """Print the tile's details."""
        print(f"({self.x}, {self.y}) {self.ressource} {self.orientation}")

    def get_info_text(self) -> str:
        return f"Port \nCoordinates: ({self.x}, {self.y})\nRessource: {self.ressource}"
