"""
Generate random, balanced boards for the board game Catan
"""

import math
import random as r

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
        offset = 0 + 1 * self.options["More_players"]

        # generate the list of used tiles coordinates
        self.tile_centers = [
            (i, j)
            for j in range(-2 - offset, 3 + offset)
            for i in range(max(-2 - j - offset, -2 - offset), min(3 - j, 3))
        ]

        # list of ressources
        self.ressource_list = ['brick', 'wood', 'sheep', 'wheat', 'stone', 'desert']

        # the deck of ressources to use
        self.deck = (3 + 2 * offset) * ['brick'] \
                  + (4 + 2 * offset) * ['wood'] \
                  + (4 + 2 * offset) * ['sheep'] \
                  + (4 + 2 * offset) * ['wheat'] \
                  + (3 + 2 * offset) * ['stone'] \
                  + (1 + 1 * offset) * ['desert']
                  

        # the deck of numbers to use
        self.numbers_deck = [2, 12] * (1 + offset) + [3, 4, 5, 6, 8, 9, 10, 11] * (2  + offset)

        #self.numbers_deck = [n for n in self.numbers_deck if n != 7]
        # Assing the desert tiles with number 7
        desert_idx = where(self.deck, 'desert')
        for i in desert_idx[::-1]:
            self.numbers_deck.insert(i, 7)

        # Generate the tiles
        self.tiles = [Tile(c[0], c[1], t, n) for (t, c, n) in zip(self.deck, self.tile_centers, self.numbers_deck)]



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
        for i, t in enumerate(self.tile_cart):
            color = {
                'brick': 'coral',
                'wood': 'forestgreen',
                'sheep': 'palegreen',
                'wheat': 'gold',
                'stone': 'slategrey',
                'desert': 'peachpuff',
            }[self.deck[i]]
            self.draw_hex(t[0], t[1], self.tile_size, fill_color = color)

    def draw_hex(self, x, y, edge_size=30, fill_color="BLANK"):
        with self.board_canvas.Stroke(line_width=0.5) as stroker:
            with stroker.Fill(x, y + edge_size, fill_color) as path:
                for n in range(6):
                    path.line_to(x + edge_size * math.sin(n * math.pi / 3), y + edge_size * math.cos(n * math.pi / 3))

    def generate_pressed(self, widget):
        self.get_tiles()
        self.shuffle_and_check()
        self.draw()

    def shuffle_and_check(self):
        # shuffle ressources
        # shuffle numbers
        # check againts rules
        # re-generate if necessary

        # debug: seed to 0
        #r.seed(0)

        while ~all(self.check_valid_ressources()):
            r.shuffle(self.deck)
            for t, res in zip(self.tiles, self.deck):
                t.ressource = res
            break

        while ~all(self.check_valid_number()):
            self.numbers_deck = [n for n in self.numbers_deck if n != 7]
            r.shuffle(self.numbers_deck)
            desert_idx = where(self.deck, 'desert')
            for i in desert_idx:
                self.numbers_deck.insert(i, 7)
            for t, n in zip(self.tiles, self.numbers_deck):
                t.number = n
            break

    def ressource_neighbours(self):
        nb_neighbours = [0] * len(self.deck)
        for i, t in enumerate(self.tiles):
            same_ressources_idx = where(self.deck, t.ressource)
            same_ressources_centers = [self.tiles[i].coords for i in same_ressources_idx]
            neighbours = t.neighbours()
            # TODO: fix
            #print(neighbours)
            #same_type_neighbours = neighbours[[any(all(same_ressources_centers == n)) for n in neighbours]]
            #nb_neighbours[i] = len(same_type_neighbours)

        return(nb_neighbours)

    def check_valid_ressources(self):
        nb_neighbours = self.ressource_neighbours()
        valid = [((r in ['wheat', 'wood', 'sheep']) & (n < 2)) | ((r in ['brick', 'stone', 'desert']) & (n < 1)) for (r, n) in zip(self.deck, nb_neighbours)]
        return(valid)

    def check_valid_number(self):
        nb_neighbours = [0] * len(self.deck)
        valid = [True] * len(self.deck)
        for i, t in enumerate(self.tiles):

            # check that no same numbers are touching
            same_num_idx = where(self.numbers_deck, t.number)[0]
            # same_num_centers = [self.tiles[i].coords for i in same_num_idx]


            # neighbours = t.neighbours()
            # TODO: fix
            # same_num_neighbours = neighbours[[any(all(same_num_centers == n)) for n in neighbours]]
            # valid[i] = valid[i] & (len(same_num_neighbours) == 0)

            # check that no same number share the same ressource

            # same_num_idx = same_num_idx[same_num_idx != i]
            # valid[i] = valid[i] & ~(t.ressource in [r for r in self.deck[same_num_idx]])
            #print(i, t.ressource, same_num_idx, valid[i])

        # for 6 and 8:

        #idx_68 = np.where((self.numbers_deck == 6) | (self.numbers_deck == 8))[0]
        # TODO: fix
        idx_68 = where(self.numbers_deck, 6) + where(self.numbers_deck, 8)

        # check that ressources have 0/1 (up to 4 players) or 1/2 (5-6 players) 6 or 8
        ress_68 = [self.deck[i] for i in idx_68]
        #u, c = np.unique(ress_68, return_counts=True)
        u = list(set(ress_68))
        #c = [len(where(ress_68, e)) for e in u]
        c = [ress_68.count(e) for e in u]
        # TODO: fix
        #duplicate_68_ress = u[c > 1]
        #duplicate_68_idx = idx_68[np.array([r in duplicate_68_ress for r in ress_68])]
        #valid[duplicate_68_idx] = False

        # check that no 6 and 8 are adjacent
        for i, idx in enumerate(idx_68):
            t = self.tiles[idx]

            neighbours = t.neighbours()

            #others_idx = np.delete(idx_68, i)
            others_idx = idx_68.copy()
            others_idx.pop(i)

            others = [self.tiles[o] for o in others_idx]
            others_coords = [o.coords for o in others]

#            l = ~any([any(all([n == o for n in neighbours])) for o in others_coords])
#            valid[idx] = valid[idx] & l

        return valid

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


class Tile:
    # the possible colors, matching the ressource type
    colors = {
            'brick': 'coral',
            'wood': 'forestgreen',
            'sheep': 'palegreen',
            'wheat': 'gold',
            'stone': 'slategrey',
            'desert': 'peachpuff',
            }

    # the transformation matrix
    # u1 = (1, 0)
    # u2 = (np.cos(np.pi/3), np.sin(np.pi/3))
#    grid_to_cart = np.array([
#        [1, np.cos(np.pi/3)],
#        [0, np.sin(np.pi/3)] ])

    # coordinates of the corners
    # in hex grid coordinates:
    corners = [
        ( 1/3, 1/3), 
        (-1/3, 2/3), 
        (-2/3, 1/3), 
        (-1/3,-1/3), 
        ( 1/3,-2/3), 
        ( 2/3,-1/3),
    ]
    


    relative_neighbours = [
            (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)
            ]

    def __init__(self, x: int = 0, y: int = 0, ressource: str = 'desert', number: int = None):

        # store x, y (hex coordinates)
        self.x, self.y = x, y
        self.coords = (self.x, self.y)

        # store ressource
        self.ressource = ressource

        # store number
        self.number = number

#    def draw(self, axis):
#        self.color = self.colors[self.ressource]
#        # pips (odds of getting the number out of the dice roll, out of 36)
#        self.pip = min(self.number - 1, 13 - self.number)

#        # get coordinates of corners, transform to cartesian
#        #corners_cart = np.matmul(self.grid_to_cart, (self.corners + self.coords).transpose())

#        # a hexagon for the tile
#        #tile_hex = axis.fill(corners_cart[0], corners_cart[1], edgecolor='k', facecolor=self.color)

#        # a circle with number in the middle
#        if self.number is not None and self.number != 7:
#            center_cart = np.matmul(self.grid_to_cart, self.coords.transpose())
#            tile_circ = plt.Circle((center_cart[0], center_cart[1]), 0.18, edgecolor='k', facecolor='white')
#            axis.add_patch(tile_circ)

#            tile_num = plt.text(center_cart[0], center_cart[1], str(self.number), verticalalignment='center', horizontalalignment='center')

    def neighbours(self):
        return([(i[0] + self.x, i[1] + self.y) for i in self.relative_neighbours])

class Board:
    tile_centers = [
            (i, j) for j in range(-2, 3)for i in range(max(-2 - j, -2), min(3 - j, 3)) 
            ]

    tile_deck = 3 * ['brick'] \
                    + 4 * ['wood'] \
                    + 4 * ['sheep'] \
                    + 4 * ['wheat'] \
                    + 3 * ['stone'] \
                    + ['desert']

    ressource_list = ['brick', 'wood', 'sheep', 'wheat', 'stone', 'desert']

    numbers_deck = [2] + [3, 4, 5, 6, 8, 9, 10, 11] * 2 + [12]

    def __init__(self, seed: int = None, ruleset: int = 0):

        # 
        self.seed = seed
        self.ruleset = ruleset

        # initialize the seed
        r.seed(self.seed)

        # generate and shuffle the deck of tiles
        self.deck = self.tile_deck
        r.shuffle(self.deck)

        # generate and shuffle the deck of numbers
        self.nums = self.numbers_deck
        r.shuffle(self.nums)

        # give the desert the number 7
        desert_idx = where(self.deck, 'desert')
        self.nums = self.nums.insert(desert_idx, 7)


        # create Tile objects
        self.tiles = [Tile(c[0], c[1], t, n) for (t, c, n) in zip(self.tile_deck, self.tile_centers, self.nums)]

        while ~all(self.check_valid_ressources()):
            r.shuffle(self.deck)
            for t, res in zip(self.tiles, self.deck):
                t.ressource = res

        while ~all(self.check_valid_number()):
            self.nums = self.nums[self.nums != 7]
            r.shuffle(self.nums)
            desert_idx = where(self.deck, 'desert')
            self.nums = self.nums.insert(desert_idx, 7)
            for t, n in zip(self.tiles, self.nums):
                t.number = n

        # create figure
        self.fig, self.ax = plt.subplots()

    def ressource_neighbours(self):
        nb_neighbours = [0] * len(self.deck)
        for i, t in enumerate(self.tiles):
            same_ressources_idx = where(self.deck, t.ressource)
            same_ressources_centers = [self.tiles[i].coords for i in same_ressources_idx]
            neighbours = t.neighbours()
            # TODO: fix
            same_type_neighbours = neighbours[[any(all(same_ressources_centers == n)) for n in neighbours]]
            nb_neighbours[i] = len(same_type_neighbours)

        return(nb_neighbours)

    def check_valid_ressources(self):
        nb_neighbours = self.ressource_neighbours()
        valid = [((r in ['wheat', 'wood', 'sheep']) & (n < 2)) | ((r in ['brick', 'stone', 'desert']) & (n < 1)) for (r, n) in zip(self.deck, nb_neighbours)]
        return(valid)

    def check_valid_number(self):
        nb_neighbours = [0] * len(self.deck)
        valid = [True] * len(self.deck)
        for i, t in enumerate(self.tiles):

            # check that no same numbers are touching
            same_num_idx = where(self.nums, t.number)[0]
            same_num_centers = [self.tiles[i].coords for i in same_num_idx]

            neighbours = t.neighbours()
            # TODO: fix
            same_num_neighbours = neighbours[[any(all(same_num_centers == n)) for n in neighbours]]
            valid[i] = valid[i] & (len(same_num_neighbours) == 0)

            # check that no same number share the same ressource

            same_num_idx = same_num_idx[same_num_idx != i]
            valid[i] = valid[i] & ~(t.ressource in [r for r in self.deck[same_num_idx]])
            #print(i, t.ressource, same_num_idx, valid[i])

        # for 6 and 8:

        #idx_68 = np.where((self.nums == 6) | (self.nums == 8))[0]
        # TODO: fix
        idx_68 = where(self.nums, 6) + where(self.nums, 8)

        # check that ressources have 0/1 (up to 4 players) or 1/2 (5-6 players) 6 or 8
        ress_68 = self.deck[idx_68]
        #u, c = np.unique(ress_68, return_counts=True)
        u = list(set(ress_68))
        #c = [len(where(ress_68, e)) for e in u]
        c = [l.count(e) for e in u]
        # TODO: fix
        #duplicate_68_ress = u[c > 1]
        #duplicate_68_idx = idx_68[np.array([r in duplicate_68_ress for r in ress_68])]
        #valid[duplicate_68_idx] = False

        # check that no 6 and 8 are adjacent
        for i, idx in enumerate(idx_68):
            t = self.tiles[idx]

            neighbours = t.neighbours()

            #others_idx = np.delete(idx_68, i)
            others_idx = idx_68.copy()
            others_idx.pop(i)

            others = [self.tiles[o] for o in others_idx]
            others_coords = [o.coords for o in others]

            l = ~any([any(all([n == o for n in neighbours])) for o in others_coords])
            valid[idx] = valid[idx] & l

        return valid


def where(l, element):
    return( [i for i in range(len(l)) if l[i] == element])

def main():
    return BalancedCatanBoardGenerator()
