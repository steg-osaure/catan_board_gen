"""Module in charge of handleing the main application."""

from typing import Any

import toga
from toga.style import Pack

from logic.board_generator import BoardGenerator
from drawer.board_drawer import BoardDrawer
from .option_handler import OptionHandler


class CBGenApp(toga.App):
    """Core application class."""

    def __init__(self) -> None:
        super().__init__()

        self.options: OptionHandler
        self.board_gen: BoardGenerator
        self.board_draw: BoardDrawer
        self.board_canvas: toga.Canvas
        self.option_widget: toga.ScrollContainer

    def startup(self) -> None:
        """Initialize the application, creating the main window and UI components."""

        self.options = OptionHandler(self.paths.app / "default_options.json")
        self.board_gen = BoardGenerator(self.options)
        self.board_draw = BoardDrawer()
        # ===  Initiate the window and its content  === #

        self.main_window = toga.MainWindow(title=self.formal_name)

        # initiate all the widgets
        self.create_board_widget()
        self.create_options_widget()

        # create and show the window
        self.initialize_window()
        self.main_window.show()

    def create_board_widget(self) -> None:
        """Create and initialize the application's UI components.

        This includes the canvas for the board, switches for options, and buttons
        for generating boards and showing option descriptions.
        """

        # Define handlers for the canvas
        def resize_canvas(widget: toga.Widget, width: int, height: int, **kwargs: Any) -> None:  # pylint: disable=unused-argument
            self.board_draw.set_size((width, height))
            self.board_draw.draw()

        def print_tile_info(widget: toga.Widget, x: float, y: float, **kwargs: Any) -> None:  # pylint: disable=unused-argument
            tx, ty = self.board_draw.convert_coord_to_tile((x, y))
            tile = self.board_draw.get_tile(tx, ty)
            if tile:
                self.main_window.info_dialog(f"Tile at {tx}, {ty}", tile.get_info_text())

        # Create the widget
        self.board_canvas = toga.Canvas(
            style=Pack(flex=1.8),
            on_resize=resize_canvas,
            on_press=print_tile_info,
        )

        # Pass to the drawer
        self.board_draw.set_canvas(self.board_canvas)

    def initialize_window(self) -> None:
        # put them in a box
        main_box = toga.Box(
            children=[
                self.board_canvas,
                self.option_widget,
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

    def create_options_widget(self) -> None:

        # Buttons to get a description of what the options do
        def show_description(widget: toga.Widget, **kwargs: Any) -> None:  # pylint: disable=unused-argument
            # Fetch the description stored in the option JSON
            description_text = self.options.get_description(widget.id.replace("_info_button", ""))
            title_text = " ".join(widget.id.split("_")[:2])
            # Pop up with the info text
            self.main_window.info_dialog(title_text, description_text)

        # One info button per option in the JSON
        description_buttons = [
            toga.Button(
                text="(?)",
                on_press=show_description,
                id=f"{opt}_info_button",
            )
            for opt in self.options.get_all()
        ]

        # Switch to toggle the options
        def on_option_switch(widget: toga.Widget) -> None:  # pylint: disable=unused-argument
            self.options.set_option(widget.id.replace("_switch", ""), widget.value)

        # One switch per option in the JSON
        switches = [
            toga.Switch(
                style=Pack(flex=1),
                text=self.options.get_box_text(opt_name),
                on_change=on_option_switch,
                value=self.options.get_option(opt_name),
                id=f"{opt_name}_switch",
            )
            for opt_name in self.options.get_all()
        ]

        # Pair the switches and buttons
        switch_boxes = [
            toga.Box(
                children=[b, s],
                style=Pack(direction="row"),
            )
            for (b, s) in zip(description_buttons, switches)
        ]

        # The button to generate a board
        def generate_pressed(widget: toga.Widget) -> None:  # pylint: disable=unused-argument
            self.board_gen.set_options(self.options)
            self.board_gen.generate()
            self.board_draw.set_board(self.board_gen.get_board())
            self.board_draw.draw()

        generate_button = toga.Button(
            style=Pack(flex=1),
            text="Generate board",
            on_press=generate_pressed,  # type: ignore
        )

        # Put all switches and button in the same box
        switch_box = toga.Box(
            children=switch_boxes + [generate_button],
            style=Pack(
                direction="column",
            ),
        )

        # Make it scrollable
        self.option_widget = toga.ScrollContainer(
            content=switch_box,
            style=Pack(
                padding_top=5,
                padding_right=5,
                padding_bottom=5,
                padding_left=5,
                flex=1,
            ),
            horizontal=False,
        )
