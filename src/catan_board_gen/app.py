"""
Generate random, balanced boards for the board game Catan
"""

import math
# import numpy as np

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
                size=(450, 772),
                resizable = False,
                )

        # initiate all the widgets
        self.create_widgets()

        # put them in a box
        main_box = toga.Box(
            children=[
                self.board_canvas,
                self.switch_box,
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

        #self.tile_centers = np.array([(i, j) for j in np.arange(-2, 3)for i in np.arange(max(-2 - j, -2), min(3 - j, 3)) ], dtype=int)
        self.tile_centers = [(i, j) for j in range(-2, 3) for i in range(max(-2 - j, -2), min(3 - j, 3)) ]
        #print(self.tile_centers)
        self.tile_cart = [
                (
                    225 + 40 * (i[0] + math.cos(math.pi / 3) * i[1]),
                    225 + 40 * math.sin(math.pi / 3) * i[1]
                ) for i in self.tile_centers]
        print(self.tile_cart)

        # draw canvas
        self.draw()

        # show the window
        self.main_window.show()

#    def draw_text(self):
#        font = toga.Font(family=SANS_SERIF, size=20)
#        self.text_width, text_height = self.board_canvas.measure_text("Tiberius", font)

#        x = (150 - self.text_width) // 2
#        y = 175

#        with self.board_canvas.Stroke(
#            color="REBECCAPURPLE", line_width=4.0
#        ) as rect_stroker:
#            self.text_border = rect_stroker.rect(
#                x - 5,
#                y - 5,
#                self.text_width + 10,
#                text_height + 10,
#            )

#        with self.board_canvas.Fill(color=rgb(149, 119, 73)) as text_filler:
#            self.text = text_filler.write_text("Test", x, y, font, Baseline.TOP)

    def draw(self):
        self.draw_hex(10, 30)

        for i in self.tile_cart:
            self.draw_hex(i[0], i[1])

    def draw_hex(self, x, y, edge_size = 20, filled = False, fill_color = "BLANK"):
        e = edge_size
        a = math.pi / 6.
        with self.board_canvas.Stroke(line_width = 2.0) as stroker:
            with stroker.ClosedPath(x, y) as path:
                path.line_to(x, y + e)
                path.line_to(x + e * math.cos(a), y + e * (1 + math.sin(a)))
                path.line_to(x + 2 * e * math.cos(a), y + e)
                path.line_to(x + 2 * e * math.cos(a), y)
                path.line_to(x + e * math.cos(a), y - e * math.sin(a))



    def on_press(self, widget, x, y, **kwargs):
        # self.main_window.info_dialog("Hey!", f"Pressed at ({x}, {y})")
        pass

    def generate_pressed(self, widget):
        self.main_window.info_dialog("Hey!", f"New board generation requested")
        # self.main_window.info_dialog("Hey!", f"window dimensions: {self.main_window.size}")

    def more_players(self, widget):
        pass

    def prevent_clusters(self, widget):
        print(f"Prevent clusters? {widget.value}")
        pass

    def prevent_port_contact(self, widget):
        pass

    def prevent_number_clusters(self, widget):
        pass

    def prevent_number_repeats(self, widget):
        pass

    def show_description(self, widget, **kwargs):
        description_text = {
            "Ressource_clusters_info_button": "Prevent clusters of similar ressources. For brick and stones (and, for 5-6 players, also desert), prevents two similar tiles from touching. For wood, wheat and sheep, prevents three similar tiles from touching.",
            "Balanced_ports_info_button": "Prevent ressourses of touching their corresponding ports.",
            "Number_clusters_info_button": "Prevent similar numbers from being next to one another. Also prevents 6 and 8 to be next to another 6 or 8.",
            "Number_repeats_info_button": "Prevent numbers from being twice on the same ressource. Also prevent ressources to have more than one 6 or one 8 (or, for 5-6 players, two 6 or two 8).",
        }[widget.id]

        title_text = " ".join(widget.id.split("_")[:2])

        self.main_window.info_dialog(title_text, description_text)

    def create_widgets(self):

        # Canvas to draw the board in
        self.board_canvas = toga.Canvas(
            style=Pack(flex=1),
            on_press=self.on_press,
        )

        self.more_players_switch = toga.Switch(
            text="5/6 players",
            on_change=self.more_players,
            value=False,
        )

        self.description_buttons = [
            toga.Button(
                text="(?)",
                on_press=self.show_description,
                id=f"{t}_info_button",
            )
            for t in [
                "Ressource_clusters",
                "Balanced_ports",
                "Number_clusters",
                "Number_repeats",
            ]
        ]

        # No two bricks or two stone tiles next to one another
        # No three wood, three sheep or three wheat tiles next to one another
        self.ressource_cluster_switch = toga.Switch(
            style=Pack(flex=1),
            text="No ressource clusters",
            on_change=self.prevent_clusters,
            value=True,
        )

        # No ressource tile touching the corresponding ressource port
        self.ressource_port_switch = toga.Switch(
            style=Pack(flex=1),
            text="Balanced ports",
            on_change=self.prevent_port_contact,
            value=True,
        )

        # No same number on adjacent tiles
        # No six and eight on adjacent tiles
        self.number_cluster_switch = toga.Switch(
            style=Pack(flex=1),
            text="No number clusters",
            on_change=self.prevent_number_clusters,
            value=True,
        )

        # No number twice on the same ressource type
        # No six and eight both on the same ressource type
        self.number_repeat_switch = toga.Switch(
            style=Pack(flex=1),
            text="No repeating numbers",
            on_change=self.prevent_number_repeats,
            value=True,
        )

        self.switches = [
            self.ressource_cluster_switch,
            self.ressource_port_switch,
            self.number_cluster_switch,
            self.number_repeat_switch,
        ]

        self.switch_boxes = [
            toga.Box(
                children=[b, s],
                style=Pack(direction="row"),
            )
            for (b, s) in zip(self.description_buttons, self.switches)
        ]

        self.generate_button = toga.Button(
            style=Pack(flex=1),
            text="Generate board",
            on_press=self.generate_pressed,
        )

        self.switch_box = toga.Box(
            children=[self.more_players_switch]
            + self.switch_boxes
            + [self.generate_button],
            style=Pack(
                direction="column",
                padding_top=5,
                padding_right=5,
                padding_bottom=5,
                padding_left=5,
            ),
        )


def main():
    return BalancedCatanBoardGenerator()
