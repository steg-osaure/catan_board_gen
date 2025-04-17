"""Module in charge of handleing the main application."""

import toga
from toga.style import Pack

from typing import Any


class CBGenApp(toga.App):
    """Core application class."""

    def startup(self) -> None:
        """Initialize the application, creating the main window and UI components."""
        #####  Initiate the window and its content  #####

        self.main_window = toga.MainWindow(
            title=self.formal_name,
        )

        self.initialize_options()
        self.prompted_warning = False

        # initiate all the widgets
        self.create_widgets()

        self.initialize_window()

        # show the window
        self.main_window.show()

    def initialize_options(self) -> None:
        # options, for the logic:
        self.options = {
            "More_players": False,
            "Ressource_clusters": True,
            "Balanced_ports": True,
            "Number_clusters": True,
            "Number_repeats": True,
        }

    def initialize_window(self) -> None:
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

    def generate_pressed(self, widget: toga.Widget) -> None:
        """Handler for the generate board button press event."""
        # self.get_tiles()
        # self.get_nums()
        # self.shuffle_and_check()
        # self.draw()
        pass

    def on_option_switch(self, widget: toga.Widget) -> None:
        """Handle changes to toggle switches in the UI.

        Updates the application's options based on the state of the switch widget.

        Args:
            widget (toga.Widget): The widget that triggered the event.
        """

        self.options[widget.id.replace("_switch", "")] = widget.value

    def show_description(self, widget: toga.Widget, **kwargs: Any) -> None:
        """Display a description dialog for the selected option.

        The dialog shows information about what the option does.

        Args:
            widget (toga.Widget): The widget that triggered the event.
            **kwargs: Additional arguments passed by the Toga framework.
        """

        description_text = {
            "More_players_info_button": "Bigger board for games up to 6 players",
            "Ressource_clusters_info_button": "Prevent clusters of similar ressources.\
                For brick and stones (and, for 5-6 players, also desert), prevents two similar tiles from touching.\
                For wood, wheat and sheep, prevents three similar tiles from touching.",
            "Balanced_ports_info_button": "Prevent ressourses of touching their\
                corresponding ports.",
            "Number_clusters_info_button": "Prevent similar numbers from being next to one another.\
                Also prevents 6 and 8 to be next to another 6 or 8.",
            "Number_repeats_info_button": "Prevent numbers from being twice on the same ressource.\
                Also prevent ressources to have more than one 6 or one 8\
                (or, for 5-6 players, two 6 or two 8).",
        }[widget.id]

        title_text = " ".join(widget.id.split("_")[:2])

        self.main_window.info_dialog(title_text, description_text)

    def create_widgets(self) -> None:
        """Create and initialize the application's UI components.

        This includes the canvas for the board, switches for options, and buttons
        for generating boards and showing option descriptions.
        """

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
            for t in self.options
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
                id=f"{i}_switch",
            )
            for t, i, v in zip(switches_text, self.options.keys(), self.options.values())
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
            on_press=self.generate_pressed,  # type: ignore
        )

        # Put all switches and button in the same box
        self.switch_box = toga.Box(
            children=self.switch_boxes + [self.generate_button],
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
