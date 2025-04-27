from typing import Any
from logic.utils import where


class BoardDebugger:
    def __init__(self):
        self.restart_debug: bool = True
        self.is_ressource_valid: bool = False
        self.is_number_valid: bool = False
        return

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

    def debug_call(self) -> dict[str, Any]:
        if self.restart_debug:
            self.stack = []
            self.get_port_tiles()
            self.get_ressource_tiles()
            self.get_numbers()
            self.board_num_options = self.numbers_deck.copy()
            self.board_num_options = [n for n in self.board_num_options if n != 7]
            self.remaining_ressources = self.ressource_deck.copy()
            self.update_ressources_near_ports()
            self.restart_debug = False
            self.is_ressource_valid = False
            self.is_number_valid = False

        if not self.is_ressource_valid:
            # self.restart_debug = not self.step_ressource_collapse()
            self.restart_debug = not self.collapse_ressource()
            self.is_ressource_valid = all(t.res_collapsed for t in self.tiles)
            if self.is_ressource_valid:
                for t in self.tiles:
                    t.reset_number_options()
            return {"ressources": self.tiles, "ports": self.ports}

        if not self.check_ressource_clusters():
            self.restart_debug = True
            return {"ressources": self.tiles, "ports": self.ports}

        if not self.is_number_valid:
            self.restart_debug = not self.step_number_collapse()
            self.is_number_valid = all(t.num_collapsed for t in self.tiles)
            return {"ressources": self.tiles, "ports": self.ports}

        if self.more_players and any(
            len([t.ressource for t in self.tiles if ((t.ressource == res) and t.num_collapsed and (t.number in [6, 8]))]) == 0
            for res in self.ressource_list[:-1]
        ):
            self.restart_debug = True
            return {"ressources": self.tiles, "ports": self.ports}

        return {"ressources": self.tiles, "ports": self.ports}

    def debug_cluster(self) -> dict[str, Any]:
        """Handler for the generate board button press event."""
        self.stack = []
        self.get_port_tiles()
        is_valid = True
        while is_valid:
            no_dead_end = self.collapse_ressource()
            if no_dead_end:
                is_valid = self.check_ressource_clusters()
        board = {"ressources": self.tiles, "ports": self.ports}

        return board

    def debug_ressources(self) -> dict[str, Any]:
        self.stack = []
        n_fail_cluster = 0
        n_fail_dead_end = 0
        n_test = 500
        for _ in range(n_test):
            self.get_port_tiles()
            is_valid = self.collapse_ressource()
            if not is_valid:
                n_fail_dead_end += 1
                continue
            if not self.check_ressource_clusters():
                n_fail_cluster += 1
        print(f"Ran {n_test} generations, {n_fail_dead_end} dead ends, failed cluster {n_fail_cluster} times")

        board = {"ressources": self.tiles, "ports": self.ports}
        return board

    def debug_numbers(self) -> dict[str, Any]:
        self.stack = []
        n_fail_repeats = 0
        n_fail_dead_end = 0
        n_test = 500
        for _ in range(n_test):
            self.get_port_tiles()
            valid_ressource = False
            while not valid_ressource:
                valid_ressource = self.collapse_ressource()

            is_valid = self.collapse_number()
            if not is_valid:
                n_fail_dead_end += 1
                continue

            if self.more_players and any(
                len([t.ressource for t in self.tiles if ((t.ressource == res) and t.num_collapsed and (t.number in [6, 8]))]) == 0
                for res in self.ressource_list[:-1]
            ):
                n_fail_repeats += 1
                # return {"ressources": self.tiles, "ports": self.ports}

        print(f"Ran {n_test} generations, {n_fail_dead_end} dead ends, failed nuber repeats {n_fail_repeats} times")

        board = {"ressources": self.tiles, "ports": self.ports}
        return board

    def debug_repeats(self) -> dict[str, Any]:
        """Handler for the generate board button press event."""
        self.stack = []
        self.get_port_tiles()
        is_valid = False
        while not is_valid:
            is_valid = self.collapse_ressource()

        while is_valid:
            no_dead_end = self.collapse_number()
            if no_dead_end and any(
                len([t.ressource for t in self.tiles if ((t.ressource == res) and t.num_collapsed and (t.number in [6, 8]))]) == 0
                for res in self.ressource_list[:-1]
            ):
                break
        board = {"ressources": self.tiles, "ports": self.ports}

        return board

    def check_ressource_clusters(self) -> bool:
        """Validate the resource distribution to prevent excessive clustering.

        Clusters of the same resource type are limited based on constraints:
        - Wheat, wood, and sheep tiles can have at most two neighbors of the same type.
        - Brick, stone, and desert tiles can have at most one neighbor of the same type.

        Returns:
            list: A list of boolean values indicating if each tile passes the check.
        """

        if self.options.get_option("Ressource_clusters"):
            valid = []
            for t in self.tiles:
                same_res_neighbours = len([neigh for neigh in self.tiles if neigh.get_coords() in t.neighbours() and neigh.ressource == t.ressource])
                valid.append(same_res_neighbours <= self.max_neighbours[t.ressource])
            if not all(valid):
                return False
        return True

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
