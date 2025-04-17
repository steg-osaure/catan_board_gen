"""Module containing the CatanBoardGenerator class."""

import math
import random as r

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.fonts import SANS_SERIF
from toga.constants import Baseline
from toga.colors import WHITE, rgb  # type: ignore

from .tile import Tile
from .utils import where

from typing import Any


class CatanBoardGenerator(toga.App):
    """A Toga application to generate random, balanced Catan boards."""

    relative_neighbours = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]

    def startup(self) -> None:
        """Initialize the application, creating the main window and UI components."""
        #####  Initiate the window and its content  #####

        self.main_window = toga.MainWindow(
            title=self.formal_name,
        )

        # options, for the logic:
        self.options = {
            "More_players": False,
            "Ressource_clusters": True,
            "Balanced_ports": True,
            "Number_clusters": True,
            "Number_repeats": True,
        }

        self.prompted_warning = False

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

    def get_nums(self) -> None:
        """Generate the deck of numbers for the tiles, including handling desert tiles."""
        offset = 0 + 1 * self.options["More_players"]
        # the deck of numbers to use
        self.numbers_deck = [2, 12] * (1 + offset) + [3, 4, 5, 6, 8, 9, 10, 11] * (2 + offset)

        # Assign the desert tiles with number 7
        desert_idx = where(self.deck, "desert")
        for i in desert_idx[::-1]:
            self.numbers_deck.insert(i, 7)

    def get_tiles(self) -> None:
        """Generate tile data, including resources and coordinates."""
        offset = 0 + 1 * self.options["More_players"]

        # generate the list of used tiles coordinates
        self.tile_centers = [(i, j) for j in range(-2 - offset, 3 + offset) for i in range(max(-2 - j - offset, -2 - offset), min(3 - j, 3))]

        # list of resources
        self.ressource_list = ["brick", "wood", "sheep", "wheat", "stone", "desert"]

        # the deck of resources to use
        self.deck = (
            (3 + 2 * offset) * ["brick"]
            + (4 + 2 * offset) * ["wood"]
            + (4 + 2 * offset) * ["sheep"]
            + (4 + 2 * offset) * ["wheat"]
            + (3 + 2 * offset) * ["stone"]
            + (1 + 1 * offset) * ["desert"]
        )

        self.get_nums()

        # Generate the tiles
        self.tiles = [Tile(c[0], c[1], t, n) for (t, c, n) in zip(self.deck, self.tile_centers, self.numbers_deck)]

        # generate the ports
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
        ] * (not self.options["More_players"]) + [
            (2, -4, "sheep", -1),
            (0, -4, "None", 0),
            (-3, -1, "stone", 1),
            (-4, 1, "None", 2),
            (-4, 2, "wheat", 1),
            (-4, 4, "None", 2),
            (-2, 4, "wood", -3),
            (0, 3, "sheep", -2),
            (1, 2, "brick", -3),
            (3, 0, "None", -2),
            (3, -2, "None", -1),
        ] * self.options[
            "More_players"
        ]

    def get_neighbours(self, x: int, y: int) -> list[tuple[int, int]]:
        """Return the coordinates of neighboring tiles for a given tile.

        Args:
            x (int): The x-coordinate of the tile.
            y (int): The y-coordinate of the tile.

        Returns:
            list: A list of tuples representing the coordinates of neighbors.
        """
        return [(i[0] + x, i[1] + y) for i in self.relative_neighbours]

    def convert_coord_to_screen(self) -> None:
        """Convert hex grid coordinates to screen coordinates for rendering."""
        # set size of tile based on window size
        self.tile_size: int = max(self.min_size - 15, 2) // (12 + 4 * self.options["More_players"])

        # offset, to center the board
        offset = 0 * ~self.options["More_players"] + self.tile_size * math.cos(math.pi / 6) * self.options["More_players"]

        # convert hex grid coordinates of tiles to screen coordinates
        self.tile_cart = [
            (
                offset + self.width // 2 + 2 * self.tile_size * (i[0] + math.cos(math.pi / 3) * i[1]),
                self.height * self.canvas_ratio / 2 - 15 + 2 * self.tile_size * math.sin(math.pi / 3) * i[1],
            )
            for i in self.tile_centers
        ]

        self.screen_ports = [
            (
                offset + self.width // 2 + 2 * self.tile_size * (i[0] + math.cos(math.pi / 3) * i[1]),
                self.height * self.canvas_ratio / 2 - 15 + 2 * self.tile_size * math.sin(math.pi / 3) * i[1],
                i[2],
                i[3],
            )
            for i in self.ports
        ]

    def draw(self) -> None:
        """Render the board tiles and ports on the canvas."""
        self.board_canvas.context.clear()
        self.width, self.height = self.main_window.size  # type: tuple[int, int]
        self.min_size: int = min(self.width, int(self.height * self.canvas_ratio))

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

    def generate_pressed(self, widget: toga.Widget) -> None:
        """Handler for the generate board button press event."""
        self.get_tiles()
        # self.get_nums()
        self.shuffle_and_check()
        self.draw()

    def shuffle_and_check(self) -> None:
        """Shuffle the tiles and numbers until a valid board configuration is found."""

        # Shuffling the tiles until a valid permutation is found
        is_valid = False
        while not is_valid:
            is_valid = self.res_wfc()

        # Shuffling the numbers until a valid permutation is found
        is_valid = False
        while not is_valid:
            is_valid = self.num_wfc()

    def res_wfc(self) -> bool:
        """Apply the Wave Function Collapse algorithm for resources."""
        self.get_tiles()

        # setup
        for t in self.tiles:

            # All tiles get options set to all
            t.res_collapsed = False
            t.res_options = self.ressource_list.copy()

        # create a list, used as a stack, storing the changes applied,
        # to backtrack in case there is no valid options left
        # self.res_stack = []

        self.board_res_options = self.deck.copy()

        if self.options["Balanced_ports"]:
            for i, p in enumerate(self.ports):
                x, y, res, _o = p
                neighbours = self.get_neighbours(x, y)
                # remove resource option from the neighboring tiles
                for t in [t for t in self.tiles if t.coords in neighbours]:
                    t.res_options = [tres for tres in t.res_options if tres != res]

        while not all(t.res_collapsed for t in self.tiles):

            # pick the tile with the least options (from non-collapsed tiles)
            res_idx_list = [i for (i, t) in enumerate(self.tiles) if not t.res_collapsed]
            res_opt_list = [len(t.res_options) for (i, t) in enumerate(self.tiles) if not t.res_collapsed]

            for i in res_idx_list:
                t = self.tiles[i]

            argmin = where(res_opt_list, min(res_opt_list))
            r.shuffle(argmin)
            idx_to_collapse = res_idx_list[argmin[0]]

            t_col = self.tiles[idx_to_collapse]

            # collapse it
            t_col.res_collapse()
            res_col = t_col.ressource

            # propagate the option decrease

            # remove resource that was chosen from deck,
            self.board_res_options.pop(self.board_res_options.index(res_col))
            # remove option for all tiles if this resource is not in the deck anymore
            if not res_col in self.board_res_options:
                for t in self.tiles:
                    if not t.res_collapsed:
                        t.res_options = [res for res in t.res_options if res != res_col]

            if self.options["Ressource_clusters"]:
                # remove resource from neighboring tiles' options
                non_collapsed_neighbours = [t for t in self.tiles if (t.coords in t_col.neighbours() and not t.res_collapsed)]
                for n in non_collapsed_neighbours:

                    # check number of collapsed neighbors:
                    nb_res_neighbours = len([t for t in self.tiles if ((t.coords in n.neighbours()) and (t.res_collapsed) and (t.ressource == res_col))])

                    # TODO: rework: tiles can still generate in "strings":
                    # at the end of a string, there is only one neighbor of the same type,
                    # but the string can be more than 2 tiles long
                    if ((res_col in ["wheat", "wood", "sheep"]) & (nb_res_neighbours >= 2)) | (
                        (res_col in ["brick", "stone", "desert"]) & (nb_res_neighbours >= 1)
                    ):
                        n.res_options = [res for res in n.res_options if res != res_col]

            # balanced ports

            if any(((len(t.res_options) == 0) & (not t.res_collapsed)) for t in self.tiles):
                return False

        self.deck = [t.ressource for t in self.tiles]

        # Temporary solutions for resource clusters
        # only if option is set
        if self.options["Ressource_clusters"]:
            nb_neighbours = self.ressource_neighbours()
            valid = [
                ((r in ["wheat", "wood", "sheep"]) & (n < 2)) | ((r in ["brick", "stone", "desert"]) & (n < 1)) for (r, n) in zip(self.deck, nb_neighbours)
            ]
            if not all(valid):
                return False

        return True

    def num_wfc(self) -> bool:
        """Apply the Wave Function Collapse algorithm to assign numbers to tiles.

        This method ensures that numbers are distributed across the board
        in a valid configuration without violating constraints such as:
        - Adjacent tiles cannot have the same number.
        - Numbers 6 and 8 cannot be adjacent to each other or another 6/8.

        Returns:
            bool: True if a valid configuration is found, False otherwise.
        """

        self.get_nums()

        # setup
        for t in self.tiles:

            # All tiles get options set to all
            t.num_collapsed = False
            t.num_options = list(range(2, 7)) + list(range(8, 13))

            # desert is collapsed into 7
            if t.ressource == "desert":
                t.num_collapse(7)

        # create a list, used as a stack, storing the changes applied,
        # to backtrack in case there is no valid options left
        # self.num_stack = []

        self.board_num_options = self.numbers_deck.copy()
        self.board_num_options = [n for n in self.board_num_options if n != 7]

        while not all(t.num_collapsed for t in self.tiles):

            # pick the tile with the least options (from non-collapsed tiles)
            num_idx_list = [i for (i, t) in enumerate(self.tiles) if not t.num_collapsed]
            num_opt_list = [len(t.num_options) for (i, t) in enumerate(self.tiles) if not t.num_collapsed]

            for i in num_idx_list:
                t = self.tiles[i]

            argmin = where(num_opt_list, min(num_opt_list))
            r.shuffle(argmin)
            idx_to_collapse = num_idx_list[argmin[0]]

            t_col = self.tiles[idx_to_collapse]

            # collapse it
            t_col.num_collapse()
            n_col = t_col.number

            # propagate the option decrease

            # remove number that was chosen from number deck,
            self.board_num_options.pop(self.board_num_options.index(n_col))
            # remove option for all tiles if this number is not in the deck anymore
            if not n_col in self.board_num_options:
                for t in self.tiles:
                    if not t.num_collapsed:
                        t.num_options = [num for num in t.num_options if num != n_col]

            if self.options["Number_clusters"]:
                # remove number from neighbouring tiles' options
                non_collapsed_neighbours = [t for t in self.tiles if (t.coords in t_col.neighbours() and not t.num_collapsed)]
                for n in non_collapsed_neighbours:
                    n.num_options = [num for num in n.num_options if num != n_col]

                # 6 and 8
                if n_col in [6, 8]:
                    other_n = 6 * (n_col == 8) + 8 * (n_col == 6)
                    for n in non_collapsed_neighbours:
                        n.num_options = [num for num in n.num_options if num != other_n]

            if self.options["Number_repeats"]:
                # remove number from same ressource tiles' options
                non_collapsed_same_res = [t for t in self.tiles if (t.ressource == t_col.ressource and not t.num_collapsed)]
                for n in non_collapsed_same_res:
                    n.num_options = [num for num in n.num_options if num != n_col]

                # handling 6 and 8
                if n_col in [6, 8]:
                    other_n = 6 * (n_col == 8) + 8 * (n_col == 6)

                    # for 3-4 player games, each ressource can have at most one 6 or one 8
                    # TODO: conditions for 5-6 players
                    # for 5-6 player games, each ressource has at most one 6 and one 8
                    # as soon as one ressource gets both picked,
                    # then the others can have at most one
                    # effectivelly, exactly one
                    if not self.options["More_players"]:  # or (self.options["More_players"] and ress_has_two68):
                        for n in non_collapsed_same_res:
                            n.num_options = [num for num in n.num_options if num != other_n]

                    # edge case for 5-6 players:
                    # if a ressource gets both 6 and 8, but another ressource already has either one,
                    # the other needs to get remove from its options
                    # if ress_has_two68:
                    #     for ress_to_fix in [res for res in self.ressource_list if len([t for t in self.tiles if ((t.ressource == res) and t.num_collapsed and (t.number in [6, 8]))]) == 1]:
                    #         t_res = [t for t in self.tiles if (t.ressource == ress_to_fix)]
                    #         n_res = [t.number for t in t_res if ((t.num_collapsed) and (t.number in [6, 8]))][0]
                    #         other_n_res = 6 * (n_col == 8) + 8 * (n_col == 6)
                    #         for n in [t for t in t_res if not t.num_collapsed]:
                    #             n.num_options = [num for num in n.num_options if num != other_n_res]

            if any(((len(t.num_options) == 0) & (not t.num_collapsed)) for t in self.tiles):
                return False

        # TEMPORARY: if, in 5-6 player games, more than one ressource type has both 6 and 8
        # (meaning one has neither), board is invalid
        if self.options["More_players"] and any(
            len([t.ressource for t in self.tiles if ((t.ressource == res) and t.num_collapsed and (t.number in [6, 8]))]) == 0
            for res in self.ressource_list[:-1]
        ):
            return False

        self.numbers_deck = [t.number for t in self.tiles]
        return True

    def ressource_neighbours(self) -> list[int]:
        """Calculate the number of neighboring tiles with the same resource type.

        This method checks for clusters of tiles with the same resource.

        Returns:
            list: A list where each element corresponds to the count of neighboring
                tiles with the same resource for each tile.
        """

        nb_neighbours = [0] * len(self.deck)
        for i, t in enumerate(self.tiles):
            same_ressources_idx = where(self.deck, t.ressource)
            same_ressources_centers = [self.tiles[i].coords for i in same_ressources_idx]
            neighbours = t.neighbours()
            same_type_neighbours = [s for s in same_ressources_centers if s in neighbours]
            nb_neighbours[i] = len(same_type_neighbours)
        return nb_neighbours

    def check_ressource_clusters(self) -> list[bool]:
        """Validate the resource distribution to prevent excessive clustering.

        Clusters of the same resource type are limited based on constraints:
        - Wheat, wood, and sheep tiles can have at most two neighbors of the same type.
        - Brick, stone, and desert tiles can have at most one neighbor of the same type.

        Returns:
            list: A list of boolean values indicating if each tile passes the check.
        """

        nb_neighbours = self.ressource_neighbours()
        valid = [((r in ["wheat", "wood", "sheep"]) & (n < 2)) | ((r in ["brick", "stone", "desert"]) & (n < 1)) for (r, n) in zip(self.deck, nb_neighbours)]
        return valid

    def check_ports(self) -> list[bool]:
        """Validate that resource tiles do not touch their corresponding ports.

        Ports of specific resource types should not have adjacent tiles of the same type.

        Returns:
            list: A list of boolean values indicating whether each port passes the check.
        """

        valid = [True] * len(self.ports)
        for i, p in enumerate(self.ports):
            x, y, r, _o = p
            neighbours = self.get_neighbours(x, y)
            same_type_neighbours = [t.coords for t in self.tiles if t.coords in neighbours and t.ressource == r]
            valid[i] = valid[i] & (len(same_type_neighbours) == 0)
        return valid

    def check_number_clusters(self) -> list[bool]:
        """Ensure that number tokens are distributed according to constraints.

        Constraints include:
        - No two tiles with the same number should be adjacent.
        - Numbers 6 and 8 cannot be adjacent to each other or to another 6/8.

        Returns:
            list: A list of boolean values indicating if each tile's number passes the check.
        """

        valid = [True] * len(self.deck)
        for i, t in enumerate(self.tiles):

            # check that no same numbers are touching
            same_num_idx = where(self.numbers_deck, t.number)
            same_num_centers = [self.tiles[j].coords for j in same_num_idx if i != j]

            neighbours = t.neighbours()
            same_num_neighbours = [s for s in same_num_centers if s in neighbours]
            valid[i] = valid[i] & (len(same_num_neighbours) == 0)

        idx_68 = where(self.numbers_deck, 6) + where(self.numbers_deck, 8)

        # check that no 6 and 8 are adjacent
        for i, idx in enumerate(idx_68):
            t = self.tiles[idx]

            neighbours = t.neighbours()

            others_idx = [j for j in idx_68 if i != j]

            others = [self.tiles[o] for o in others_idx]
            others_coords = [o.coords for o in others]

            neighbours_68 = [s for s in others_coords if s in neighbours]

            valid[idx] = valid[idx] & (len(neighbours_68) == 0)

        return valid

    def check_number_repeats(self) -> list[bool]:
        """Ensure that resource types do not have repeated number tokens.

        Additional constraints include:
        - For 3-4 player boards, a resource type can have at most one 6 or one 8.
        - For 5-6 player boards, a resource type can have at most one 6 and one 8.

        Returns:
            list: A list of boolean values indicating if each resource type passes the check.
        """

        valid = [True] * len(self.ressource_list[:-1])

        # For all ressources (except desert), check that there is no repeat
        # For 5/6 players, at most one repeat
        for i, r in enumerate(self.ressource_list[:-1]):
            ress_idx = where(self.deck, r)
            ress_nums = [self.numbers_deck[j] for j in ress_idx]
            unique_nums = list(set(ress_nums))
            count_nums = [ress_nums.count(e) for e in unique_nums]

            valid[i] = valid[i] & (sum(count_nums) <= len(unique_nums) + 1 * self.options["More_players"])

            # Conditions for 6 and 8

            ress_6_count = sum(ress_nums.count(e) for e in unique_nums if e == 6)
            ress_8_count = sum(ress_nums.count(e) for e in unique_nums if e == 8)

            # there can only be at most one of either for 3-4 player boards,
            if not self.options["More_players"]:
                valid[i] = valid[i] & (ress_6_count + ress_8_count <= 1)

            # and at least one, or both (but not twice the same) for 5-6 player boards
            else:
                valid[i] = valid[i] & (ress_6_count + ress_8_count >= 1) & (ress_6_count <= 1) & (ress_8_count <= 1)

        return valid

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
