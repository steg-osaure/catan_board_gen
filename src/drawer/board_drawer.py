import math

import toga

from toga.fonts import SANS_SERIF
from toga.constants import Baseline


class BoardDrawer:
    def __init__(self):
        self.test = "test"

    def draw_board(self, board, size):
        print(board)
        print(size)

        #

    def convert_coord_to_screen(self) -> None:
        """Convert hex grid coordinates to screen coordinates for rendering."""
        # set size of tile based on window size
        # self.tile_size: int = max(self.min_size - 15, 2) // (12 + 4 * self.options["More_players"])

        # offset, to center the board
        # offset = 0 * ~self.options["More_players"] + self.tile_size * math.cos(math.pi / 6) * self.options["More_players"]

        # convert hex grid coordinates of tiles to screen coordinates
        self.tile_cart = [
            (
                self.offset + self.width // 2 + 2 * self.tile_size * (i[0] + math.cos(math.pi / 3) * i[1]),
                self.height * self.canvas_ratio / 2 - 15 + 2 * self.tile_size * math.sin(math.pi / 3) * i[1],
            )
            for i in self.tile_centers
        ]

        self.screen_ports = [
            (
                self.offset + self.width // 2 + 2 * self.tile_size * (i[0] + math.cos(math.pi / 3) * i[1]),
                self.height * self.canvas_ratio / 2 - 15 + 2 * self.tile_size * math.sin(math.pi / 3) * i[1],
                i[2],
                i[3],
            )
            for i in self.ports
        ]

    def draw(self, canvas) -> None:
        """Render the board tiles and ports on the canvas."""

        self.board_canvas = canvas
        self.canvas_prop_size = self.board_canvas.style.flex
        self.canvas_ratio = self.canvas_prop_size / (1 + self.canvas_prop_size)
        self.board_canvas.context.clear()

        # self.width, self.height = self.main_window.size
        self.width, self.height = 800, 600  # Placeholder for window size
        self.min_size: int = min(self.width, int(self.height * self.canvas_ratio))

        # TODO: placeholder using 4 player board size
        # generate these from window size and size of row/columns
        self.tile_size: int = max(self.min_size - 15, 2) // (12)
        self.offset = 0
        self.tile_centers = [
            (i, j) for j in range(-2 - self.offset, 3 + self.offset) for i in range(max(-2 - j - self.offset, -2 - self.offset), min(3 - j, 3))
        ]

        # TODO: pass these from board generator
        self.ports = [
            (2, -3, "sheep", -1),
            (0, -3, "None", 0),
            (-2, -1, "stone", 1),
            (-3, 1, "wheat", 1),
            (-3, 3, "None", 2),
            (-1, 3, "wood", -3),
            (1, 2, "brick", -3),
            (3, 0, "None", -2),
            (3, -2, "None", -1),
        ]
        self.deck = (
            (3 + 2 * self.offset) * ["brick"]
            + (4 + 2 * self.offset) * ["wood"]
            + (4 + 2 * self.offset) * ["sheep"]
            + (4 + 2 * self.offset) * ["wheat"]
            + (3 + 2 * self.offset) * ["stone"]
            + (1 + 1 * self.offset) * ["desert"]
        )
        self.numbers_deck = [2, 12] * (1 + self.offset) + [3, 4, 5, 6, 8, 9, 10, 11] * (2 + self.offset) + [7]

        # ===
        self.convert_coord_to_screen()
        for i, t in enumerate(self.tile_cart):
            color = {
                "brick": "coral",
                "wood": "forestgreen",
                "sheep": "palegreen",
                "wheat": "gold",
                "stone": "slategrey",
                "desert": "peachpuff",
            }[self.deck[i]]
            self.draw_hex(
                t[0],
                t[1],
                self.numbers_deck[i],
                self.tile_size,
                fill_color=color,
            )

        for p in self.screen_ports:
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

        with self.board_canvas.Stroke(line_width=2) as stroker:
            stroker.arc(x, y, self.tile_size / 2)

        c = {
            "brick": "coral",
            "wood": "forestgreen",
            "sheep": "palegreen",
            "wheat": "gold",
            "stone": "slategrey",
            "None": "white",
        }[t]

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
