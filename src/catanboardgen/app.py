"""
Generate random, balanced boards for the board game Catan
"""

from catanboardgen.CatanBoardGenerator import CatanBoardGenerator


def main():
    """Create and return an instance of the CatanBoardGenerator application.

        This function serves as the entry point for running the application.

    Returns:
        CatanBoardGenerator: An instance of the CatanBoardGenerator app.
    """
    return CatanBoardGenerator()
