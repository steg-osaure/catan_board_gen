import math

from typing import Any

import toga
from toga.fonts import SANS_SERIF
from toga.constants import Baseline

from logic.ressource_tile import RessourceTile
from logic.port_tile import PortTile


class BoardDrawer:
    """Handles rendering of the Catan game board on a Toga canvas.

    This class is responsible for drawing hexagonal resource tiles and circular port tiles
    on a Toga canvas. It supports coordinate conversions between hex grid space and screen
    space, dynamic tile sizing, and visual rendering of game elements.

    Attributes:
        color (dict[str, str]): Mapping of resource types to display colors.
        offset_x (float): Horizontal offset to center the board on the canvas.
        offset_y (float): Vertical offset to center the board on the canvas.
        tile_size (int): Pixel size of each hexagonal tile.
        board_canvas (toga.Canvas): Canvas used for drawing.
        tiles (list[RessourceTile]): List of resource tiles to render.
        ports (list[PortTile]): List of port tiles to render.
        width (int): Width of the canvas.
        height (int): Height of the canvas.
    """

    color = {
        "brick": "coral",
        "wood": "forestgreen",
        "sheep": "palegreen",
        "wheat": "gold",
        "stone": "slategrey",
        "desert": "peachpuff",
        "None": "white",
    }

    def __init__(self) -> None:
        """Initialize the BoardDrawer with default canvas and board settings."""
        self.offset_x: float = 0
        self.offset_y: float = 0
        self.tile_size: int = 0
        self.board_canvas: toga.Canvas
        self.tiles: list[RessourceTile] = []
        self.ports: list[PortTile] = []
        self.width, self.height = 0, 0

    def convert_coord_to_screen(self, tile_coords: tuple[int, int]) -> tuple[float, float]:
        """Convert board (hex grid) coordinates to screen (pixel) coordinates.

        Args:
            tile_coords (tuple[int, int]): Coordinates in hex grid space.

        Returns:
            tuple[float, float]: Corresponding screen coordinates for rendering.
        """
        return (
            self.width // 2 + 2 * self.tile_size * (self.offset_x + tile_coords[0] + math.cos(math.pi / 3) * tile_coords[1]),
            self.height // 2 + 2 * self.tile_size * math.sin(math.pi / 3) * (self.offset_y + tile_coords[1]),
        )

    def convert_coord_to_tile(self, screen_coords: tuple[float, float]) -> tuple[int, int]:
        """Convert screen (pixel) coordinates to the nearest board (hex grid) coordinates.

        Args:
            screen_coords (tuple[float, float]): Screen coordinates (usually from mouse input).

        Returns:
            tuple[int, int]: Nearest tile coordinates in the hex grid.
        """
        ty = (screen_coords[1] - self.height / 2) / (2 * self.tile_size * math.sin(math.pi / 3)) - self.offset_y
        tx = (screen_coords[0] - self.width / 2) / (2 * self.tile_size) - self.offset_x - math.cos(math.pi / 3) * ty
        return (round(tx), round(ty))

    def set_size(self, canvas_size: tuple[int, int]) -> None:
        """Update the information about the size of the canvas and re-computes the size of the tiles.

        Args:
            size (tuple[int, int]): Width and height of the canvas.
        """
        self.width, self.height = canvas_size
        self.set_tilesize()

    def set_tilesize(self) -> None:
        """Calculate and set the tile size and offset based on current canvas and tile layout."""
        all_x = [0] + [t.x for t in self.tiles + self.ports]
        all_y = [0] + [t.y for t in self.tiles + self.ports]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        n_rows = abs(max_y - min_y) + 1
        n_cols = abs(max_x - min_x) + 1
        self.offset_x = ((n_cols + 1) % 2) / 2
        self.offset_y = ((n_rows + 1) % 2) / 2
        self.tile_size = int(min(self.width / n_cols, self.height / n_rows) / 2)

    def set_canvas(self, canvas: toga.Canvas) -> None:
        """Update the information about the size of the canvas and re-computes the size of the tiles.

        Args:
            canvas (toga.Canvas): The Toga canvas where tiles and ports will be drawn.
        """
        self.board_canvas = canvas

    def set_board(self, board: dict[str, Any]) -> None:
        """Update the information about the tiles present on the board.

        Args:
            board (dict[str, Any]): Dictionary with "ressources" and "ports" lists.
        """
        self.tiles, self.ports = board["ressources"], board["ports"]
        self.set_tilesize()

    def draw(self) -> None:
        """Draw the entire board onto a Toga canvas."""
        self.board_canvas.context.clear()

        for t in self.tiles:
            self.draw_tile(t)

        for p in self.ports:
            self.draw_port(p)

    def draw_tile(self, tile: RessourceTile) -> None:
        """Draw a single resource tile with a hexagon and optional number token.

        Args:
            tile (RessourceTile): The tile to draw, including position, resource, and number.
        """
        number, ressource = tile.value["number"], tile.value["ressource"]
        x, y = self.convert_coord_to_screen(tile.get_coords())
        fill_color = self.color[ressource]
        font = toga.Font(family=SANS_SERIF, size=self.tile_size // 2)
        w, h = self.board_canvas.measure_text(str(number), font)

        # Draw hex tile
        with self.board_canvas.Stroke(line_width=2, color="black") as stroker:
            with stroker.Fill(x, y + self.tile_size, fill_color) as filler:
                for n in range(6):
                    filler.line_to(
                        x + self.tile_size * math.sin(n * math.pi / 3),
                        y + self.tile_size * math.cos(n * math.pi / 3),
                    )

        # Draw number token (excluding desert/robber)
        if number != 7:
            with self.board_canvas.Fill(x, y, color="WHITE") as filler:
                filler.ellipse(x, y, self.tile_size / 2, self.tile_size / 2)
            with self.board_canvas.Stroke(line_width=2) as stroker:
                stroker.arc(x, y, self.tile_size / 2)

            c = "BLACK" * ((number != 6) and (number != 8)) + "RED" * ((number == 6) or (number == 8))
            with self.board_canvas.Fill(x, y, color=c) as text_filler:
                text_filler.write_text(str(number), x - w / 2.0, y - h / 2.0, font, Baseline.TOP)

    def draw_port(self, port: PortTile) -> None:
        """Draw a port on the canvas as a directional arc with a resource indicator.

        Args:
            port (PortTile): The port tile including position, resource type, and orientation.
        """
        x, y = self.convert_coord_to_screen((port.x, port.y))

        # Outer arc
        with self.board_canvas.Stroke(line_width=2) as stroker:
            stroker.arc(x, y, self.tile_size / 2)

        # Directional lines
        with self.board_canvas.Stroke(x, y, line_width=2) as stroker:
            stroker.line_to(
                x + self.tile_size * math.sin(port.orientation * math.pi / 3),
                y + self.tile_size * math.cos(port.orientation * math.pi / 3),
            )
            stroker.move_to(x, y)
            stroker.line_to(
                x + self.tile_size * math.sin((port.orientation + 1) * math.pi / 3),
                y + self.tile_size * math.cos((port.orientation + 1) * math.pi / 3),
            )

        # Fill and label
        c = self.color[port.ressource]
        with self.board_canvas.Fill(x, y, color=c) as filler:
            filler.ellipse(x, y, self.tile_size / 2, self.tile_size / 2)

        # Text for generic port
        if port.ressource == "None":
            font = toga.Font(family=SANS_SERIF, size=self.tile_size // 3)
            w, h = self.board_canvas.measure_text("3:1", font)
            with self.board_canvas.Fill(x, y, color="black") as text_filler:
                text_filler.write_text("3:1", x - w / 2.0, y - h / 2.0, font, Baseline.TOP)
