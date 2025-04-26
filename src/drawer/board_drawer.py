import math

from typing import Any

import toga
from toga.fonts import SANS_SERIF
from toga.constants import Baseline

from logic.ressource_tile import RessourceTile
from logic.port_tile import PortTile


class BoardDrawer:
    """Class to handle the drawing of the Catan board."""

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
        self.offset_x: float = 0
        self.offset_y: float = 0
        self.tile_size: int = 0
        self.board_canvas: toga.Canvas
        self.tiles: list[RessourceTile] = []
        self.ports: list[PortTile] = []
        self.width, self.height = 0, 0

    def convert_coord_to_screen(self, tile_coords: tuple[int, int]) -> tuple[float, float]:
        """Convert hex grid coordinates to screen coordinates for rendering."""
        return (
            self.width // 2 + 2 * self.tile_size * (self.offset_x + tile_coords[0] + math.cos(math.pi / 3) * tile_coords[1]),
            self.height // 2 + 2 * self.tile_size * math.sin(math.pi / 3) * (self.offset_y + tile_coords[1]),
        )

    def convert_coord_to_tile(self, screen_coords: tuple[float, float]) -> tuple[int, int]:
        ty = (screen_coords[1] - self.height / 2) / (2 * self.tile_size * math.sin(math.pi / 3)) - self.offset_y
        tx = (screen_coords[0] - self.width / 2) / (2 * self.tile_size) - self.offset_x - math.cos(math.pi / 3) * ty
        return (round(tx), round(ty))

    def set_tilesize(self) -> None:
        # Adding zero to avoid errors if no tiles are present
        all_x = [0] + [t.x for t in self.tiles + self.ports]
        all_y = [0] + [t.y for t in self.tiles + self.ports]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        n_rows = abs(max_y - min_y) + 1
        n_cols = abs(max_x - min_x) + 1
        self.offset_x = ((n_cols + 1) % 2) / 2
        self.offset_y = ((n_rows + 1) % 2) / 2
        self.tile_size = int(min(self.width / n_cols, self.height / n_rows) / 2)

    def draw(self, board: dict[str, Any], canvas: toga.Canvas, size: tuple[int, int]) -> None:
        """Render the board tiles and ports on the canvas."""

        self.board_canvas = canvas
        self.board_canvas.context.clear()

        self.tiles, self.ports = board["ressources"], board["ports"]
        self.width, self.height = size

        self.set_tilesize()

        # Draw all tiles:
        for t in self.tiles:
            self.draw_tile(t)

        for p in self.ports:
            self.draw_port(p)

    def draw_tile(self, tile: RessourceTile) -> None:
        """Draw a hexagonal tile on the canvas.

        Args:
            x (float): X-coordinate for the tile center.
            y (float): Y-coordinate for the tile center.
            num (int): Number token value for the tile.
            edge_size (int, optional): Size of the hexagonal edges. Defaults to 30.
            fill_color (str, optional): Fill color for the tile. Defaults to "BLANK".
        """
        number, ressource = tile.number, tile.ressource
        x, y = self.convert_coord_to_screen(tile.get_coords())
        fill_color = self.color[ressource]
        font = toga.Font(family=SANS_SERIF, size=self.tile_size // 2)
        w, h = self.board_canvas.measure_text(str(number), font)

        # Drawing the actual hexagonal tile
        with self.board_canvas.Stroke(line_width=2, color="black") as stroker:
            with stroker.Fill(x, y + self.tile_size, fill_color) as filler:
                for n in range(6):
                    filler.line_to(
                        x + self.tile_size * math.sin(n * math.pi / 3),
                        y + self.tile_size * math.cos(n * math.pi / 3),
                    )

        # Drawing the number token
        if number != 7:
            with self.board_canvas.Fill(x, y, color="WHITE") as filler:
                filler.ellipse(x, y, self.tile_size / 2, self.tile_size / 2)
            with self.board_canvas.Stroke(line_width=2) as stroker:
                stroker.arc(x, y, self.tile_size / 2)
            c = "BLACK" * ((number != 6) & (number != 8)) + "RED" * ((number == 6) | (number == 8))
            with self.board_canvas.Fill(x, y, color=c) as text_filler:
                text_filler.write_text(str(number), x - w / 2.0, y - h / 2.0, font, Baseline.TOP)

    def draw_port(self, port: PortTile) -> None:
        """Draw a port on the canvas.

        Args:
            port (tuple): Port details (x, y, resource type, orientation).
        """
        x, y = self.convert_coord_to_screen((port.x, port.y))

        with self.board_canvas.Stroke(line_width=2) as stroker:
            stroker.arc(x, y, self.tile_size / 2)

        c = self.color[port.ressource]

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
        with self.board_canvas.Fill(x, y, color=c) as filler:
            filler.ellipse(x, y, self.tile_size / 2, self.tile_size / 2)

        if port.ressource == "None":
            font = toga.Font(family=SANS_SERIF, size=self.tile_size // 3)
            w, h = self.board_canvas.measure_text("3:1", font)

            with self.board_canvas.Fill(x, y, color="black") as text_filler:
                text_filler.write_text("3:1", x - w / 2.0, y - h / 2.0, font, Baseline.TOP)
