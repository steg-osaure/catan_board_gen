"""Module containing the CatanBoardGenerator class."""

import random as r

from typing import Any


from logic.ressource_tile import RessourceTile
from logic.port_tile import PortTile
from logic.utils import where

from core.option_handler import OptionHandler


class BoardGenerator:
    """Class responsible for generating randomized Catan game boards with constraints.

    This class uses a Wave Function Collapse (WFC)-inspired algorithm to generate
    Catan boards by assigning resources and numbers to tiles
    while enforcing various balance constraints.

    Features include:
    - Preventing large clusters of the same resource type.
    - Ensuring ports are not adjacent to matching resource tiles.
    - Preventing most frequent numbers to repeat on one type of ressource.
    - Adapting the board layout for 3-4 player and 5-6 player games.

    Attributes:
        ressource_list (list[str]): List of all possible resource types.
        relative_neighbours (list[tuple[int, int]]): Relative coordinates for neighboring tiles.
        max_neighbours (dict[str, int]): Maximum allowed same-resource neighbors per tile.
        numbers_deck (list[int]): Numbers available for assignment to tiles.
        centers_deck (list[tuple[int, int]]): Coordinates for tile centers.
        ressource_deck (list[str]): Resource types available for assignment.
        tiles (list[RessourceTile]): List of resource tiles on the board.
        init_ports (list[tuple[int, int, str, int]]): Initial configuration for port tiles.
        ports (list[PortTile]): List of ports on the board.
        remaining_ressources (list[str]): Resources still available during collapse.
        board_num_options (list[int]): Numbers still available during collapse.
        stack (list[dict[str, Any]]): Stack for internal state management.
        options (OptionHandler): Options controlling board generation behavior.
        more_players (bool): Whether the game is configured for 5-6 players.
        offset (int): Adjustment for larger boards (5-6 player variant).
    """

    ressource_list: list[str] = ["brick", "wood", "sheep", "wheat", "stone", "desert"]
    relative_neighbours: list[tuple[int, int]] = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    max_neighbours = {"wheat": 1, "wood": 1, "sheep": 1, "brick": 0, "stone": 0, "desert": 0}

    def __init__(self, options: OptionHandler) -> None:
        """Initialize the BoardGenerator, setting up decks, tiles, ports, and options."""
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
        """Set generation options based on user-selected parameters."""

        self.options = options
        self.more_players = self.options.get_option("More_players")
        self.offset = 0 + 1 * self.more_players

    def get_numbers(self) -> None:
        """Prepare the deck of tile numbers, taking into account desert tiles and player count."""
        n_commun = 2 + self.offset
        n_rare = 1 + self.offset
        self.numbers_deck = [2, 12] * n_rare + [i for i in range(3, 12) if i != 7] * n_commun

        self.assign_desert()

    def assign_desert(self) -> None:
        """Insert the number 7 for desert tiles into the number deck at appropriate positions."""
        desert_idx = where(self.ressource_deck, "desert")
        # loop backwards to avoid index issues
        for i in desert_idx[::-1]:
            self.numbers_deck.insert(i, 7)

    def get_centers(self) -> None:
        """Compute the coordinates for all resource tiles based on board size."""
        column_range = range(-2 - self.offset, 3 + self.offset)
        row_ranges = {j: range(max(-2 - j - self.offset, -2 - self.offset), min(3 - j, 3)) for j in column_range}
        self.centers_deck = [(i, j) for j in column_range for i in row_ranges[j]]

    def get_ressources(self) -> None:
        """Prepare the deck of available resource types based on player count."""
        n_desert = 1 + self.offset
        n_inorganic = 3 + 2 * self.offset
        n_organic = 4 + 2 * self.offset

        self.ressource_deck = n_inorganic * ["brick", "stone"] + n_organic * ["wood", "sheep", "wheat"] + n_desert * ["desert"]

    def get_ressource_tiles(self) -> None:
        """Initialize all resource tiles with their coordinates and assign available resources."""
        self.get_centers()
        self.get_ressources()
        self.get_numbers()

        # Generate the tiles
        self.tiles = [RessourceTile(x, y) for (x, y) in self.centers_deck]

    def get_port_tiles(self) -> None:
        """Generate the port tiles and assign randomized or balanced port resources based on options."""
        # Initialize the position of the 3-wide edge tiles
        edge_positions = {
            False: [
                ((0, -3), (1, 0), [0, 0, -1]),
                ((-3, 3), (0, -1), [2, 2, 1]),
                ((3, 0), (-1, 1), [4, 4, 3]),
                ((-3, 0), (1, -1), [1, 1, 0]),
                ((0, 3), (-1, 0), [3, 3, 2]),
                ((3, -3), (0, 1), [5, 5, 4]),
            ],
            True: [
                ((0, -4), (1, 0), [0, 0, -1]),
                ((-4, 4), (0, -1), [2, 2, 1]),
                ((3, 0), (-1, 1), [4, 4, 3]),
                ((-4, 0), (1, -1), [1, 1, 0]),
                ((-1, 4), (-1, 0), [3, 3, 2]),
                ((3, -4), (0, 1), [5, 5, 4]),
            ],
        }[self.more_players]

        # Additional 1-wide edge tiles for 5/6 player boards
        more_positions = {False: [], True: [((3, -1), (0, 0), [-1]), ((-1, -3), (0, 0), [1]), ((-4, 1), (0, 0), [2]), ((0, 3), (0, 0), [-2])]}[
            self.more_players
        ]
        edge_positions += more_positions

        # Initialize the port ressources present on the 3-wide edge tiles
        edge_ressources = [
            ["None", None, "sheep"],
            ["None", None, "wheat"],
            ["None", None, "brick"],
            [None, "stone", None],
            [None, "wood", None],
            [None, "None", None],
        ]

        # Additional 1-wide edge tiles for 5/6 player boards
        more_ressources = {False: [], True: [[None], [None], ["None"], ["sheep"]]}[self.more_players]

        # Randomize edge tile placement
        # Random generation behaves differently when using Balanced Port options
        if self.options.get_option("Random_ports"):
            if self.options.get_option("Balanced_ports"):
                # we want the 3-wide tiles to alternate between having 2 and 1 ports
                shuffle_type_a = [0, 1, 2]
                shuffle_type_b = [3, 4, 5]
                r.shuffle(shuffle_type_a)
                r.shuffle(shuffle_type_b)
                randomize_a_b_order = [shuffle_type_a, shuffle_type_b]
                r.shuffle(randomize_a_b_order)
                idx = randomize_a_b_order[0] + randomize_a_b_order[1]
                edge_ressources = [edge_ressources[i] for i in idx]

                # for 1-wide tiles in the case of 5/6 player games, we just want to randomize the two ones with the ports
                # and we want them to not be directly next to a port from a 3-wide tile
                if self.more_players:

                    shuffle_other_a = [0, 1]
                    shuffle_other_b = [2, 3]
                    r.shuffle(shuffle_other_a)
                    r.shuffle(shuffle_other_b)
                    other_a_b_order = [shuffle_other_a, shuffle_other_b] if (idx[0] < 3) else [shuffle_other_b, shuffle_other_a]
                    more_idx = other_a_b_order[0] + other_a_b_order[1]

                    more_ressources = [more_ressources[i] for i in more_idx]

            else:
                r.shuffle(edge_ressources)
                r.shuffle(more_ressources)

        # Initialize port placement following the edge tiles placement
        edge_ressources += more_ressources  # type: ignore

        self.ports = [
            PortTile(
                x=position[0][0] + i * position[1][0],
                y=position[0][1] + i * position[1][1],
                ressource=ressource,
                orientation=position[2][i],
            )
            for position, ressource_list in zip(edge_positions, edge_ressources)
            for i, ressource in enumerate(ressource_list)
            if ressource is not None
        ]

    def call(self) -> dict[str, Any]:
        """Trigger the full board generation process, returning a dictionary of tiles and ports."""
        self.stack = []
        self.get_port_tiles()

        # Generate ressource tile placement until a valid configuration is found
        is_valid = False
        while not is_valid:
            is_valid = self.collapse_ressource()

        # Generate number placement until a valid configuration is found
        is_valid = False
        while not is_valid:
            is_valid = self.collapse_number()

        return {"ressources": self.tiles, "ports": self.ports}

    def update_ressources_near_ports(self) -> None:
        """Adjust resource options near ports to ensure balanced port distribution if required."""
        if self.options.get_option("Balanced_ports"):
            for p in self.ports:
                # remove resource option from the neighboring tiles
                neighbouring_tiles = [t for t in self.tiles if t.get_coords() in p.neighbours()]
                tiles_to_clean = [t for t in neighbouring_tiles if p.ressource in t.ressource_options]

                for t in tiles_to_clean:
                    t.ressource_options.remove(p.ressource)

    def pick_tile_to_collapse(self, to_check: str) -> RessourceTile:
        """Select the next tile to collapse based on the smallest number of available options.

        Args:
            to_check (str): Specify 'ressource' or 'number' collapse mode.

        Returns:
            RessourceTile: The selected tile to collapse next.
        """

        def check(t: RessourceTile) -> bool:
            return t.res_collapsed if to_check == "ressource" else t.num_collapsed

        def options(t: RessourceTile) -> int:
            return len(t.ressource_options) if to_check == "ressource" else len(t.num_options)

        # pick the tile with the least options (from non-collapsed tiles)
        idx_list = [i for (i, t) in enumerate(self.tiles) if not check(t)]
        opt_list = [options(t) for t in self.tiles if not check(t)]
        argmin = where(opt_list, min(opt_list))
        r.shuffle(argmin)
        idx_to_collapse = idx_list[argmin[0]]
        return self.tiles[idx_to_collapse]

    def propagate_ressource_collapse(self, t_col: RessourceTile) -> None:
        """Update the resource options of neighboring tiles after a resource is collapsed."""
        # remove resource that was chosen from deck,
        if t_col.ressource in self.remaining_ressources:
            self.remaining_ressources.pop(self.remaining_ressources.index(t_col.ressource))
        # remove option for all tiles if this resource is not in the deck anymore
        if t_col.ressource not in self.remaining_ressources:
            for t in self.tiles:
                if not t.res_collapsed:
                    t.ressource_options = [res for res in t.ressource_options if res != t_col.ressource]

        # Remove ressource options for (potentially indirect) neighbours
        if self.options.get_option("Ressource_clusters"):

            # Fetch the neighbours of the collapsed tile that share the same ressource.
            # Their neighbours might also need to have their options removed
            same_res_neighbours = [t for t in self.tiles if ((t.get_coords() in t_col.neighbours()) and t.res_collapsed and (t.ressource == t_col.ressource))]

            # Propagate on direct neighbours
            to_propagate = [t for t in self.tiles if (t.get_coords() in t_col.neighbours() and not t.res_collapsed)]
            self.propagate_ressource_cluster_collapse(t_col.ressource, to_propagate, same_res_neighbours)

            # Propagate on indirect neighbours
            for same_n in same_res_neighbours:
                # Fetch indirect that share the same ressource (include the collapsed tile)
                indirect_neighbours = [
                    t for t in self.tiles if ((t.get_coords() in same_n.neighbours()) and t.res_collapsed and (t.ressource == t_col.ressource))
                ]

                # Get indirect neighbours (no need to check tiles that where already propagated)
                additional_check_tiles = [t for t in self.tiles if (t.get_coords() in same_n.neighbours() and not t.res_collapsed and t not in to_propagate)]

                self.propagate_ressource_cluster_collapse(t_col.ressource, additional_check_tiles, indirect_neighbours)

    def propagate_ressource_cluster_collapse(self, ressource: str, tiles_to_check: list[RessourceTile], additional_neighbours: list[RessourceTile]) -> None:
        """Restrict resource options for neighboring tiles to prevent oversized clusters of the same resource."""
        for n in tiles_to_check:
            # Get collapsed neighbours of the ressource to check
            collapsed_neighbours = [t for t in self.tiles if ((t.get_coords() in n.neighbours()) and t.res_collapsed and (t.ressource == ressource))]

            # We have to consider the direct neighbours of the tile,
            # but also additional tiles of the same ressource that might for a cluster but not be directly
            # next to the tile to check
            set_to_check = set(collapsed_neighbours + additional_neighbours)
            if len(set_to_check) > self.max_neighbours[ressource]:
                n.ressource_options = [res for res in n.ressource_options if res != ressource]

    def step_ressource_collapse(self) -> bool:
        """Perform one step of resource collapse and propagate the consequences.

        Returns:
            bool: True if no dead end occurred, False otherwise.
        """
        t_col = self.pick_tile_to_collapse(to_check="ressource")
        t_col.res_collapse()
        self.propagate_ressource_collapse(t_col)

        # Did we run into a dead end?
        if any(((len(t.ressource_options) == 0) & (not t.res_collapsed)) for t in self.tiles):
            return False
        return True

    def collapse_ressource(self) -> bool:
        """Collapse all resource tiles using Wave Function Collapse until a valid assignment is achieved.

        Returns:
            bool: True if successful, False if a dead end is encountered.
        """
        # reset the tiles and available ressources
        self.get_ressource_tiles()
        self.remaining_ressources = self.ressource_deck.copy()

        # Remove options next to ports
        self.update_ressources_near_ports()

        # Collapse tiles one by one until successful, or abort when we run into a dead end
        while not all(t.res_collapsed for t in self.tiles):
            still_valid = self.step_ressource_collapse()
            if not still_valid:
                return False

        # If all tiles are collapsed and no dead end where found, ressource placement is succesfull
        return True

    def propagate_number_collapse(self, t_col: RessourceTile) -> None:
        """Update number options of neighboring tiles after a number is collapsed, handling adjacency and clusters."""
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
                other_n = {6: 8, 8: 6}[n_col]
                for n in non_collapsed_neighbours:
                    n.num_options = [num for num in n.num_options if num != other_n]

        if self.options.get_option("Number_repeats"):
            self.propagate_number_repeate_collapse(t_col)

    def propagate_number_repeate_collapse(self, t_col: RessourceTile) -> None:
        """Restrict number repetition on tiles sharing the same resource type, handling 6/8 placement rules."""
        n_col = t_col.number
        # remove number from same ressource tiles' options
        non_collapsed_same_res = [t for t in self.tiles if (t.ressource == t_col.ressource and not t.num_collapsed)]
        for n in non_collapsed_same_res:
            n.num_options = [num for num in n.num_options if num != n_col]

        # handling 6 and 8
        if n_col in [6, 8]:
            other_n = {6: 8, 8: 6}[n_col]

            # for 3-4 player games, each ressource can have at most one 6 or one 8
            if not self.more_players:  # or (self.options["More_players"] and ress_has_two68):
                for n in non_collapsed_same_res:
                    n.num_options = [num for num in n.num_options if num != other_n]

            # for 5-6 player games, each ressource has at most one 6 and one 8
            # as soon as one ressource gets both picked,
            # then the others can have at most one
            # effectivelly, exactly one
            elif any(
                len([t.ressource for t in self.tiles if ((t.ressource == ressource) and t.num_collapsed and (t.number in [6, 8]))]) == 2
                for ressource in self.ressource_list
            ):
                # Loop over all ressource
                for ressource in self.ressource_list:
                    ressource_tiles = [t for t in self.tiles if t.ressource == ressource]

                    # If ressource already has exactly one 6 or one 8, remove the other 6 and 8 options
                    if len([t for t in ressource_tiles if t.num_collapsed and (t.number in [6, 8])]) == 1:
                        for n in [t for t in ressource_tiles if not t.num_collapsed]:
                            n.num_options = [num for num in n.num_options if num not in [6, 8]]

    def step_number_collapse(self) -> bool:
        """Perform one step of number collapse and propagate the consequences.

        Returns:
            bool: True if no dead end occurred, False otherwise.
        """
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
        """Collapse number for all tiles using Wave Function Collapse until a valid assignment is achieved.

        Returns:
            bool: True if successful, False if a dead end is encountered.
        """
        # reset the tiles' number options and available numbers
        self.get_numbers()
        for t in self.tiles:
            t.reset_number_options()
        self.board_num_options = self.numbers_deck.copy()
        self.board_num_options = [n for n in self.board_num_options if n != 7]

        # Collapse tiles one by one until successful, or abort when we run into a dead end
        while not all(t.num_collapsed for t in self.tiles):
            still_valid = self.step_number_collapse()
            if not still_valid:
                return False

        # If all tiles are collapsed and no dead end where found, number placement is succesfull
        return True
