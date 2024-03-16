"""
Generate random, balanced boards for the board game Catan
"""

import math

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.fonts import SANS_SERIF
from toga.constants import Baseline
from toga.colors import WHITE, rgb


class BalancedCatanBoardGenerator(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """

        #####  Initiate the window and its content  #####

        # debug on linux: pass same size as for android (my FP3 phone),
        # debug on linux: make un-resizable
        self.main_window = toga.MainWindow(
            title=self.formal_name,
            # size=(450, 772),
            # resizable=False,
        )

        # options, for the logic:
        self.options = {
            "More_players": False,
            "Ressource_clusters": True,
            "Balanced_ports": True,
            "Number_clusters": True,
            "Number_repeats": True,
        }

        # initiate all the widgets
        self.create_widgets()

        # put them in a box
        main_box = toga.Box(
            children=[
                self.board_canvas,
                self.switch_scroll,
            ],
            style=Pack(
                direction="column",
                padding_top=5,
                padding_right=5,
                padding_bottom=5,
                padding_left=5,
            ),
        )

        # put box in window
        self.main_window.content = main_box


        # show the window
        self.main_window.show()

    def get_tiles(self):
        if not self.options["More_players"]:
            self.tile_centers = [
                (i, j)
                for j in range(-2, 3)
                for i in range(max(-2 - j, -2), min(3 - j, 3))
            ]
        else:
            self.tile_centers = [
                (i, j)
                for j in range(-3, 4)
                for i in range(max(-3 - j, -3), min(3 - j, 3))
            ]

    def convert_coord_to_screen(self):

        # set size of tile based on window size
        self.tile_size = max(self.min_size - 15, 2) // (
            10 + 2 * self.options["More_players"]
        )

        # offset, to center the board
        offset = (
            0 * ~self.options["More_players"]
            + self.tile_size * math.cos(math.pi / 6) * self.options["More_players"]
        )

        # convert hex grid coordinates of tiles to screen coordinates
        self.tile_cart = [
            (
                offset
                + self.width // 2
                + 2 * self.tile_size * (i[0] + math.cos(math.pi / 3) * i[1]),
                self.height * self.canvas_ratio / 2
                + 2 * self.tile_size * math.sin(math.pi / 3) * i[1],
            )
            for i in self.tile_centers
        ]

    def draw(self):
        self.board_canvas.context.clear()
        self.width, self.height = self.main_window.size
        self.min_size = min(self.width, self.height * self.canvas_ratio)

        self.convert_coord_to_screen()
        for i in self.tile_cart:
            self.draw_hex(i[0], i[1], self.tile_size)

    def draw_hex(self, x, y, edge_size=30, filled=False, fill_color="BLANK"):
        e = edge_size
        a = math.pi / 6.0

        with self.board_canvas.Stroke(line_width=2.0) as stroker:
            with stroker.ClosedPath(x - e * math.cos(a), y - e * math.sin(a)) as path:
                path.line_to(x - e * math.cos(a), y + e * math.sin(a))
                path.line_to(x, y + e)
                path.line_to(x + e * math.cos(a), y + e * math.sin(a))
                path.line_to(x + e * math.cos(a), y - e * math.sin(a))
                path.line_to(x, y - e)

    def generate_pressed(self, widget):
        self.get_tiles()
        self.draw()

    def on_option_switch(self, widget):
        self.options[widget.id.replace("_switch", "")] = widget.value

    def show_description(self, widget, **kwargs):
        description_text = {
            "More_players_info_button": "Bigger board for games up to 6 players",
            "Ressource_clusters_info_button": "Prevent clusters of similar ressources. For brick and stones (and, for 5-6 players, also desert), prevents two similar tiles from touching. For wood, wheat and sheep, prevents three similar tiles from touching.",
            "Balanced_ports_info_button": "Prevent ressourses of touching their corresponding ports.",
            "Number_clusters_info_button": "Prevent similar numbers from being next to one another. Also prevents 6 and 8 to be next to another 6 or 8.",
            "Number_repeats_info_button": "Prevent numbers from being twice on the same ressource. Also prevent ressources to have more than one 6 or one 8 (or, for 5-6 players, two 6 or two 8).",
        }[widget.id]

        title_text = " ".join(widget.id.split("_")[:2])

        self.main_window.info_dialog(title_text, description_text)

    def create_widgets(self):

        # Canvas:

        # set proportions relative to the screen height
        self.canvas_prop_size = 1.8
        self.canvas_ratio = self.canvas_prop_size / (1 + self.canvas_prop_size)

        # create the canvas
        self.board_canvas = toga.Canvas(
            style=Pack(flex=self.canvas_prop_size),
        )

        # Buttons to get a description of what the options do
        self.description_buttons = [
            toga.Button(
                text="(?)",
                on_press=self.show_description,
                id=f"{t}_info_button",
            )
            for t in self.options.keys()
        ]

        # Text to display on the switches
        switches_text = [
            "5/6 players",
            "No ressource clusters",
            "Balanced ports",
            "No number clusters",
            "No repeating numbers",
        ]

        # All the switches
        self.switches = [
            toga.Switch(
                style=Pack(flex=1),
                text=t,
                on_change=self.on_option_switch,
                value=v,
                id = f"{i}_switch"
            ) for t, i, v in zip(switches_text, self.options.keys(), self.options.values())
        ]

        # Pair the switches and buttons
        self.switch_boxes = [
            toga.Box(
                children=[b, s],
                style=Pack(direction="row"),
            )
            for (b, s) in zip(self.description_buttons, self.switches)
        ]

        # The button to generate a board
        self.generate_button = toga.Button(
            style=Pack(flex=1),
            text="Generate board",
            on_press=self.generate_pressed,
        )

        # Put all switches and button in the same box
        self.switch_box = toga.Box(
            children= self.switch_boxes
            + [self.generate_button],
            style=Pack(
                direction="column",
            ),
        )

        # Make it scrollable
        self.switch_scroll = toga.ScrollContainer(
            content=self.switch_box,
            style=Pack(
                padding_top=5,
                padding_right=5,
                padding_bottom=5,
                padding_left=5,
                flex=1,
            ),
            horizontal=False,
        )


def main():
    return BalancedCatanBoardGenerator()
