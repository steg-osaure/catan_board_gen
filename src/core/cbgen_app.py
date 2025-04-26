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
        self.current_board: dict[str, Any] = {"ressources": [], "ports": []}
        self.board_canvas: toga.Canvas
        self.description_buttons: list[toga.Button]
        self.switches: list[toga.Switch]
        self.switch_boxes: list[toga.Box]
        self.generate_button: toga.Button
        self.switch_box: toga.Box
        self.switch_scroll: toga.ScrollContainer
        self.board_canvas_size: tuple[int, int] = (0, 0)

    def startup(self) -> None:
        """Initialize the application, creating the main window and UI components."""

        self.options = OptionHandler(self.paths.app / "default_options.json")
        self.board_gen = BoardGenerator(self.options)
        self.board_draw = BoardDrawer()
        # ===  Initiate the window and its content  === #

        self.main_window = toga.MainWindow(title=self.formal_name)

        # initiate all the widgets
        # create and show the window
        self.create_widgets()
        self.initialize_window()

        self.main_window.show()

    def zoom(self, widget: toga.Widget) -> None:  # pylint: disable=unused-argument
        # self.imview.style.width = 500
        pass

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

    def generate_pressed(self, widget: toga.Widget) -> None:  # pylint: disable=unused-argument
        """Handler for the generate board button press event."""
        self.board_gen.set_options(self.options)
        self.current_board = self.board_gen.call()
        # self.current_board = self.board_gen.debug_call()
        # self.current_board = self.board_gen.debug_ressources()
        # self.current_board = self.board_gen.debug_cluster()
        self.board_draw.draw(self.current_board, self.board_canvas, self.board_canvas_size)

    def on_option_switch(self, widget: toga.Widget) -> None:  # pylint: disable=unused-argument
        """Handle changes to toggle switches in the UI.

        Updates the application's options based on the state of the switch widget.

        Args:
            widget (toga.Widget): The widget that triggered the event.
        """

        self.options.set_option(widget.id.replace("_switch", ""), widget.value)

    def show_description(self, widget: toga.Widget, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        """Display a description dialog for the selected option.

        The dialog shows information about what the option does.

        Args:
            widget (toga.Widget): The widget that triggered the event.
            **kwargs: Additional arguments passed by the Toga framework.
        """

        description_text = self.options.get_description(widget.id.replace("_info_button", ""))

        title_text = " ".join(widget.id.split("_")[:2])

        self.main_window.info_dialog(title_text, description_text)

    def create_widgets(self) -> None:
        """Create and initialize the application's UI components.

        This includes the canvas for the board, switches for options, and buttons
        for generating boards and showing option descriptions.
        """

        # Canvas:

        # create the canvas
        self.board_canvas = toga.Canvas(
            style=Pack(flex=1.8),
            on_resize=self.on_board_canvas_resize,
            on_press=self.on_board_canvas_press,
        )

        # Buttons to get a description of what the options do
        self.description_buttons = [
            toga.Button(
                text="(?)",
                on_press=self.show_description,
                id=f"{opt}_info_button",
            )
            for opt in self.options.get_all()
        ]

        # All the switches
        self.switches = [
            toga.Switch(
                style=Pack(flex=1),
                text=self.options.get_box_text(opt_name),
                on_change=self.on_option_switch,
                value=self.options.get_option(opt_name),
                id=f"{opt_name}_switch",
            )
            for opt_name in self.options.get_all()
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

    def on_board_canvas_resize(self, widget: toga.Widget, width: int, height: int, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        """Handle the resize event of the board canvas.

        Args:
            widget (toga.Widget): The widget that triggered the event.
            **kwargs: Additional arguments passed by the Toga framework.
        """
        self.board_canvas_size = width, height
        self.board_draw.draw(self.current_board, self.board_canvas, self.board_canvas_size)

    def on_board_canvas_press(self, widget: toga.Widget, x: float, y: float, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        # print(f"test {x}, {y}")
        tx, ty = self.board_draw.convert_coord_to_tile((x, y))
        for t in self.current_board["ressources"] + self.current_board["ports"]:
            if t.get_coords() == (tx, ty):
                t.print_info()
