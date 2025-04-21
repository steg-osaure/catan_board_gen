import math

import toga

from toga.fonts import SANS_SERIF
from toga.constants import Baseline


class BoardDrawer:
    color = {
        "brick": "coral",
        "wood": "forestgreen",
        "sheep": "palegreen",
        "wheat": "gold",
        "stone": "slategrey",
        "desert": "peachpuff",
        "None": "white",
    }

    def __init__(self):
        pass

    def draw_board(self, board, size):
        print(board)
        print(size)

        #

    def convert_coord_to_screen(self, tile_coords: tuple[int, int]) -> tuple[float, float]:
        """Convert hex grid coordinates to screen coordinates for rendering."""
        return (
            self.offset + self.width // 2 + 2 * self.tile_size * (tile_coords[0] + math.cos(math.pi / 3) * tile_coords[1]),
            self.height * self.canvas_ratio / 2 - 15 + 2 * self.tile_size * math.sin(math.pi / 3) * tile_coords[1],
        )

    def draw(self, board, canvas) -> None:
        """Render the board tiles and ports on the canvas."""

        self.board_canvas = canvas
        self.canvas_prop_size = self.board_canvas.style.flex
        self.canvas_ratio = self.canvas_prop_size / (1 + self.canvas_prop_size)
        self.board_canvas.context.clear()

        # self.width, self.height = self.main_window.size
        self.width, self.height = 800, 600  # TODO: Placeholder for window size
        self.min_size: int = min(self.width, int(self.height * self.canvas_ratio))

        # TODO: placeholder using 4 player board size
        # generate these from window size and size of row/columns
        self.tile_size: int = max(self.min_size - 15, 2) // (12)
        self.offset = 0

        self.ports = board["ports"]
        self.tiles = board["ressources"]

        # ===
        for i, t in enumerate(self.tiles):
            screen_x, screen_y = self.convert_coord_to_screen((t.x, t.y))

            self.draw_hex(
                screen_x,
                screen_y,
                t.number,
                self.tile_size,
                fill_color=self.color[t.ressource],
            )

        for p in self.ports:
            self.draw_port(p)

    def draw_hex(self, x: float, y: float, num: int, edge_size: int = 30, fill_color: str = "BLANK") -> None:
        """Draw a hexagonal tile on the canvas.

        Args:
            x (float): X-coordinate for the tile center.
            y (float): Y-coordinate for the tile center.
            num (int): Number token value for the tile.
            edge_size (int, optional): Size of the hexagonal edges. Defaults to 30.
            fill_color (str, optional): Fill color for the tile. Defaults to "BLANK".
        """
        font = toga.Font(family=SANS_SERIF, size=edge_size // 2)
        w, h = self.board_canvas.measure_text(str(num), font)

        # Drawing the actual hexagonal tile
        with self.board_canvas.Stroke(line_width=2, color="black") as stroker:
            with stroker.Fill(x, y + edge_size, fill_color) as filler:
                for n in range(6):
                    filler.line_to(
                        x + edge_size * math.sin(n * math.pi / 3),
                        y + edge_size * math.cos(n * math.pi / 3),
                    )

        # Drawing the number token
        if num != 7:
            with self.board_canvas.Fill(x, y, color="WHITE") as filler:
                filler.ellipse(x, y, edge_size / 2, edge_size / 2)
            with self.board_canvas.Stroke(line_width=2) as stroker:
                stroker.arc(x, y, edge_size / 2)
            c = "BLACK" * ((num != 6) & (num != 8)) + "RED" * ((num == 6) | (num == 8))
            with self.board_canvas.Fill(x, y, color=c) as text_filler:
                text_filler.write_text(str(num), x - w / 2.0, y - h / 2.0, font, Baseline.TOP)

    def draw_port(self, port: tuple[float, float, str, int]) -> None:
        """Draw a port on the canvas.

        Args:
            port (tuple): Port details (x, y, resource type, orientation).
        """
        x, y, t, o = port
        x, y = self.convert_coord_to_screen((x, y))

        with self.board_canvas.Stroke(line_width=2) as stroker:
            stroker.arc(x, y, self.tile_size / 2)

        c = self.color[t]

        with self.board_canvas.Stroke(x, y, line_width=2) as stroker:
            stroker.line_to(
                x + self.tile_size * math.sin(o * math.pi / 3),
                y + self.tile_size * math.cos(o * math.pi / 3),
            )
            stroker.move_to(x, y)
            stroker.line_to(
                x + self.tile_size * math.sin((o + 1) * math.pi / 3),
                y + self.tile_size * math.cos((o + 1) * math.pi / 3),
            )
        with self.board_canvas.Fill(x, y, color=c) as filler:
            filler.ellipse(x, y, self.tile_size / 2, self.tile_size / 2)

        if t == "None":
            font = toga.Font(family=SANS_SERIF, size=self.tile_size // 3)
            w, h = self.board_canvas.measure_text("3:1", font)

            with self.board_canvas.Fill(x, y, color="black") as text_filler:
                text_filler.write_text("3:1", x - w / 2.0, y - h / 2.0, font, Baseline.TOP)
