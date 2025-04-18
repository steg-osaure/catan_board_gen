"""Method containing the class to store the different option settings"""

# import json

default_options = {
    "More_players": {"default": False, "box_text": "5/6 players", "description": "Bigger board for games up to 6 players"},
    "Ressource_clusters": {
        "default": True,
        "box_text": "No ressource clusters",
        "description": "Prevent clusters of similar ressources.\nFor brick and stones (and, for 5-6 players, also desert), prevents two similar tiles from touching.\nFor wood, wheat and sheep, prevents three similar tiles from touching.",
    },
    "Balanced_ports": {"default": True, "box_text": "Balanced ports", "description": "Prevent ressourses of touching their\ncorresponding ports."},
    "Number_clusters": {
        "default": True,
        "box_text": "No number clusters",
        "description": "Prevent similar numbers from being next to one another.\nAlso prevents 6 and 8 to be next to another 6 or 8.",
    },
    "Number_repeats": {
        "default": True,
        "box_text": "No repeating numbers",
        "description": "Prevent numbers from being twice on the same ressource.\nAlso prevent ressources to have more than one 6 or one 8\n(or, for 5-6 players, two 6 or two 8).",
    },
}


class OptionHandler:
    """Class to handle the options for the script"""

    def __init__(self):
        """Initialize the option handler with default values"""

        # with open("default_options.json") as option_json:
        #    self.options = option_json.load()
        self.options = default_options

        for key in self.options.keys():
            self.options[key].update({"value": self.options[key]["default"]})

    def get_option(self, key: str) -> None:
        """Get the value of a specific option"""
        return self.options[key]["value"]

    def set_option(self, key: str, value: bool) -> None:
        """Set an option to a specific value"""
        self.options[key]["value"] = value

    def toggle_option(self, key: str) -> None:
        """Toggle the value of a specific option"""
        self.options[key]["value"] = not self.options[key]["value"]

    def get_all(self) -> dict[str, bool]:
        # return {key: self.options[key]["value"] for key in self.options.keys()}
        return self.options.keys()

    def get_box_text(self, key: str) -> str:
        """Get the text for the box"""
        return self.options[key]["box_text"]

    def get_description(self, key: str) -> str:
        """Get the description for the box"""
        return self.options[key]["description"]
