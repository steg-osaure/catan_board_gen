"""Module containing the CatanBoardGenerator class."""

import random as r

from typing import Any


from logic.ressource_tile import RessourceTile
from logic.port_tile import PortTile
from logic.utils import where

from core.option_handler import OptionHandler


class BoardGenerator:
    """Class to handle the generation of Catan boards."""

    ressource_list: list[str] = ["brick", "wood", "sheep", "wheat", "stone", "desert"]
    relative_neighbours: list[tuple[int, int]] = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]

    def __init__(self, options: OptionHandler) -> None:
        """Initialize the application, creating the main window and UI components."""
        self.numbers_deck: list[int] = []
        self.centers_deck: list[tuple[int, int]] = []
        self.ressource_deck: list[str] = []
        self.tiles: list[RessourceTile] = []
        self.init_ports: list[tuple[int, int, str, int]] = []
        self.ports: list[PortTile] = []
        self.remaining_ressources: list[str] = []
        self.board_num_options: list[int] = []
        self.stack: list[dict[str, Any]] = []

        # options, for the logic:
        self.set_options(options)

    def set_options(self, options: OptionHandler) -> None:
        self.options = options
        self.more_players = self.options.get_option("More_players")
        self.offset = 0 + 1 * self.more_players

    def get_numbers(self) -> None:
        """Generate the deck of numbers for the tiles, including handling desert tiles."""
        # the deck of numbers to use
        n_commun = 2 + self.offset
        n_rare = 1 + self.offset
        self.numbers_deck = [2, 12] * n_rare + [i for i in range(3, 12) if i != 7] * n_commun

        self.assign_desert()

    def assign_desert(self) -> None:
        # Assign the desert tiles with number 7
        desert_idx = where(self.ressource_deck, "desert")
        # loop backwards to avoid index issues
        for i in desert_idx[::-1]:
            self.numbers_deck.insert(i, 7)

    def get_centers(self) -> None:
        """Generate tile data, including resources and coordinates."""

        # generate the list of used tiles coordinates
        column_range = range(-2 - self.offset, 3 + self.offset)
        row_ranges = {j: range(max(-2 - j - self.offset, -2 - self.offset), min(3 - j, 3)) for j in column_range}
        self.centers_deck = [(i, j) for j in column_range for i in row_ranges[j]]

    def get_ressources(self) -> None:
        # the deck of resources to use
        n_desert = 1 + self.offset
        n_inorganic = 3 + 2 * self.offset
        n_organic = 4 + 2 * self.offset

        self.ressource_deck = n_inorganic * ["brick", "stone"] + n_organic * ["wood", "sheep", "wheat"] + n_desert * ["desert"]

    def get_ressource_tiles(self) -> None:

        self.get_centers()
        self.get_ressources()
        self.get_numbers()

        # Generate the tiles
        self.tiles = [RessourceTile(x, y) for (x, y) in self.centers_deck]

    def get_port_tiles(self) -> None:

        # Initialize the position of the 3-wide edge tiles
        edge_positions = {
            False: [
                ((0, -3), (1, 0)),
                ((-3, 0), (1, -1)),
                ((-3, 3), (0, -1)),
                ((0, 3), (-1, 0)),
                ((3, 0), (-1, 1)),
                ((3, -3), (0, 1)),
            ],
            True: [
                ((0, -4), (1, 0)),
                ((-4, 0), (1, -1)),
                ((-4, 4), (0, -1)),
                ((-1, 4), (-1, 0)),
                ((3, 0), (-1, 1)),
                ((3, -4), (0, 1)),
            ],
        }[self.more_players]

        # Initialize the port ressources present on the 3-wide edge tiles
        edge_ressources = [
            ["None", None, "sheep"],
            [None, "stone", None],
            ["None", None, "wheat"],
            [None, "wood", None],
            ["None", None, "brick"],
            [None, "None", None],
        ]

        # Additional 1-wide edge tiles for 5/6 player boards
        more_positions = {False: [], True: [((3, -1), (0, 0)), ((-1, -3), (0, 0)), ((-4, 1), (0, 0)), ((0, 3), (0, 0))]}[self.more_players]
        more_ressources = {False: [], True: [[None], [None], ["None"], ["sheep"]]}[self.more_players]

        # Randomize edge tile placement
        if self.options.get_option("Random_ports"):
            r.shuffle(edge_positions)
            r.shuffle(edge_ressources)
            r.shuffle(more_positions)
            r.shuffle(more_ressources)

        # Initialize port placement following the edge tiles placement
        edge_positions += more_positions
        more_ressources += more_ressources

        self.ports = [
            PortTile(
                x=position[0][0] + i * position[1][0],
                y=position[0][1] + i * position[1][1],
                ressource=ressource,
                orientation=-1,
            )
            for position, ressource_list in zip(edge_positions, edge_ressources)
            for i, ressource in enumerate(ressource_list)
            if ressource is not None
        ]

    def call(self) -> dict[str, Any]:
        """Handler for the generate board button press event."""
        self.stack = []
        self.get_port_tiles()

        self.shuffle_and_check()

        board = {"ressources": self.tiles, "ports": self.ports}

        return board

    def shuffle_and_check(self) -> None:
        """Shuffle the tiles and numbers until a valid board configuration is found."""

        # Shuffling the tiles until a valid permutation is found
        is_valid = False
        while not is_valid:
            print("Collapsing ressources")
            is_valid = self.collapse_ressource()

        # Shuffling the numbers until a valid permutation is found
        is_valid = False
        while not is_valid:
            print("Collapsing numbers")
            is_valid = self.collapse_number()

    def update_ressources_near_ports(self) -> None:
        if self.options.get_option("Balanced_ports"):
            for p in self.ports:
                # remove resource option from the neighboring tiles
                neighbouring_tiles = [t for t in self.tiles if t.get_coords() in p.neighbours()]
                tiles_to_clean = [t for t in neighbouring_tiles if p.ressource in t.ressource_options]

                for t in tiles_to_clean:
                    t.ressource_options.remove(p.ressource)

    def pick_tile_to_collapse(self, to_check: str) -> RessourceTile:
        # pick the tile with the least options (from non-collapsed tiles)
        def check(t: RessourceTile) -> bool:
            return t.res_collapsed if to_check == "ressource" else t.num_collapsed

        def options(t: RessourceTile) -> int:
            return len(t.ressource_options) if to_check == "ressource" else len(t.num_options)

        idx_list = [i for (i, t) in enumerate(self.tiles) if not check(t)]
        opt_list = [options(t) for t in self.tiles if not check(t)]
        argmin = where(opt_list, min(opt_list))
        r.shuffle(argmin)
        idx_to_collapse = idx_list[argmin[0]]
        return self.tiles[idx_to_collapse]

    def propagate_ressource_collapse(self, t_col: RessourceTile) -> None:

        # propagate the option decrease

        # remove resource that was chosen from deck,
        if t_col.ressource in self.remaining_ressources:
            self.remaining_ressources.pop(self.remaining_ressources.index(t_col.ressource))
        # remove option for all tiles if this resource is not in the deck anymore
        if t_col.ressource not in self.remaining_ressources:
            for t in self.tiles:
                if not t.res_collapsed:
                    t.ressource_options = [res for res in t.ressource_options if res != t_col.ressource]

        if self.options.get_option("Ressource_clusters"):
            # remove resource from neighboring tiles' options
            non_collapsed_neighbours = [t for t in self.tiles if (t.get_coords() in t_col.neighbours() and not t.res_collapsed)]
            for n in non_collapsed_neighbours:

                # check number of collapsed neighbors:
                nb_res_neighbours = len(
                    [t for t in self.tiles if ((t.get_coords() in n.neighbours()) and (t.res_collapsed) and (t.ressource == t_col.ressource))]
                )

                # TODO: rework: tiles can still generate in "strings":
                # at the end of a string, there is only one neighbor of the same type,
                # but the string can be more than 2 tiles long
                if ((t_col.ressource in ["wheat", "wood", "sheep"]) & (nb_res_neighbours >= 2)) | (
                    (t_col.ressource in ["brick", "stone", "desert"]) & (nb_res_neighbours >= 1)
                ):
                    n.ressource_options = [res for res in n.ressource_options if res != t_col.ressource]

    def step_ressource_collapse(self) -> bool:

        t_col = self.pick_tile_to_collapse(to_check="ressource")
        t_col.res_collapse()

        self.propagate_ressource_collapse(t_col)

        # Did we run into a dead end?
        if any(((len(t.ressource_options) == 0) & (not t.res_collapsed)) for t in self.tiles):
            return False
        return True

    def collapse_ressource(self) -> bool:
        """Apply the Wave Function Collapse algorithm for resources."""

        # reset the tiles
        self.get_ressource_tiles()

        # TODO: create a list, used as a stack, storing the changes applied,
        # to backtrack in case there is no valid options left
        # self.res_stack = []

        self.remaining_ressources = self.ressource_deck.copy()

        self.update_ressources_near_ports()

        step = 0
        while not all(t.res_collapsed for t in self.tiles):
            print(step)
            still_valid = self.step_ressource_collapse()

            if not still_valid:
                print("reset")
                return False
            step += 1

        self.ressource_deck = [t.ressource for t in self.tiles]

        # Temporary solutions for resource clusters
        # only if option is set
        if self.options.get_option("Ressource_clusters"):
            nb_neighbours = self.ressource_neighbours()
            valid = [
                ((r in ["wheat", "wood", "sheep"]) & (n < 2)) | ((r in ["brick", "stone", "desert"]) & (n < 1))
                for (r, n) in zip(self.ressource_deck, nb_neighbours)
            ]
            if not all(valid):
                return False

        return True

    def propagate_number_collapse(self, t_col: RessourceTile) -> None:
        n_col = t_col.number

        # remove number that was chosen from number deck,
        self.board_num_options.pop(self.board_num_options.index(n_col))
        # remove option for all tiles if this number is not in the deck anymore
        if n_col not in self.board_num_options:
            for t in self.tiles:
                if not t.num_collapsed:
                    t.num_options = [num for num in t.num_options if num != n_col]

        if self.options.get_option("Number_clusters"):
            # remove number from neighbouring tiles' options
            non_collapsed_neighbours = [t for t in self.tiles if (t.get_coords() in t_col.neighbours() and not t.num_collapsed)]
            for n in non_collapsed_neighbours:
                n.num_options = [num for num in n.num_options if num != n_col]

            # 6 and 8
            if n_col in [6, 8]:
                other_n = 6 * (n_col == 8) + 8 * (n_col == 6)
                for n in non_collapsed_neighbours:
                    n.num_options = [num for num in n.num_options if num != other_n]

        if self.options.get_option("Number_repeats"):
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
                if not self.more_players:  # or (self.options["More_players"] and ress_has_two68):
                    for n in non_collapsed_same_res:
                        n.num_options = [num for num in n.num_options if num != other_n]

                # edge case for 5-6 players:
                # if a ressource gets both 6 and 8, but another ressource already has either one,
                # the other needs to get remove from its options
                # if ress_has_two68:
                #     for ress_to_fix in [res for res in self.ressource_list
                #           if len([t for t in self.tiles if ((t.ressource == res) and t.num_collapsed and (t.number in [6, 8]))]) == 1]:
                #         t_res = [t for t in self.tiles if (t.ressource == ress_to_fix)]
                #         n_res = [t.number for t in t_res if ((t.num_collapsed) and (t.number in [6, 8]))][0]
                #         other_n_res = 6 * (n_col == 8) + 8 * (n_col == 6)
                #         for n in [t for t in t_res if not t.num_collapsed]:
                #             n.num_options = [num for num in n.num_options if num != other_n_res]

    def step_number_collapse(self) -> bool:
        # pick the tile with the least options (from non-collapsed tiles)
        t_col = self.pick_tile_to_collapse(to_check="number")

        # collapse it
        t_col.num_collapse()

        # propagate the option decrease
        self.propagate_number_collapse(t_col)

        if any(((len(t.num_options) == 0) & (not t.num_collapsed)) for t in self.tiles):
            return False
        return True

    def collapse_number(self) -> bool:
        """Apply the Wave Function Collapse algorithm to assign numbers to tiles.

        This method ensures that numbers are distributed across the board
        in a valid configuration without violating constraints such as:
        - Adjacent tiles cannot have the same number.
        - Numbers 6 and 8 cannot be adjacent to each other or another 6/8.

        Returns:
            bool: True if a valid configuration is found, False otherwise.
        """

        self.get_numbers()

        for t in self.tiles:
            t.reset_number_options()

        # TODO: create a list, used as a stack, storing the changes applied,
        # to backtrack in case there is no valid options left
        # self.num_stack = []

        self.board_num_options = self.numbers_deck.copy()
        self.board_num_options = [n for n in self.board_num_options if n != 7]

        while not all(t.num_collapsed for t in self.tiles):
            still_valid = self.step_number_collapse()
            if not still_valid:
                print("reset")
                return False

        # TEMPORARY: if, in 5-6 player games, more than one ressource type has both 6 and 8
        # (meaning one has neither), board is invalid
        if self.more_players and any(
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

        nb_neighbours = [0] * len(self.ressource_deck)
        for i, t in enumerate(self.tiles):
            same_ressources_idx = where(self.ressource_deck, t.ressource)
            same_ressources_centers = [self.tiles[i].get_coords() for i in same_ressources_idx]
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
        valid = [
            ((r in ["wheat", "wood", "sheep"]) & (n < 2)) | ((r in ["brick", "stone", "desert"]) & (n < 1))
            for (r, n) in zip(self.ressource_deck, nb_neighbours)
        ]
        return valid

    def check_ports(self) -> list[bool]:
        """Validate that resource tiles do not touch their corresponding ports.

        Ports of specific resource types should not have adjacent tiles of the same type.

        Returns:
            list: A list of boolean values indicating whether each port passes the check.
        """

        valid = [True] * len(self.ports)
        for i, p in enumerate(self.ports):
            same_type_neighbours = [t.get_coords() for t in self.tiles if t.get_coords() in p.neighbours() and t.ressource == p.ressource]
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

        valid = [True] * len(self.ressource_deck)
        for i, t in enumerate(self.tiles):

            # check that no same numbers are touching
            same_num_idx = where(self.numbers_deck, t.number)
            same_num_centers = [self.tiles[j].get_coords() for j in same_num_idx if i != j]

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
            others_coords = [o.get_coords() for o in others]

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
        for i, ressource in enumerate(self.ressource_list[:-1]):
            ress_idx = where(self.ressource_deck, ressource)
            ress_nums = [self.numbers_deck[j] for j in ress_idx]
            unique_nums = list(set(ress_nums))
            count_nums = [ress_nums.count(e) for e in unique_nums]

            valid[i] = valid[i] & (sum(count_nums) <= len(unique_nums) + 1 * self.more_players)

            # Conditions for 6 and 8

            ress_6_count = sum(ress_nums.count(e) for e in unique_nums if e == 6)
            ress_8_count = sum(ress_nums.count(e) for e in unique_nums if e == 8)

            # there can only be at most one of either for 3-4 player boards,
            if not self.more_players:
                valid[i] = valid[i] & (ress_6_count + ress_8_count <= 1)

            # and at least one, or both (but not twice the same) for 5-6 player boards
            else:
                valid[i] = valid[i] & (ress_6_count + ress_8_count >= 1) & (ress_6_count <= 1) & (ress_8_count <= 1)

        return valid
