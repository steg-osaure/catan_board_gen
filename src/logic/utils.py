"""Module containing miscellaneous utilities."""

from typing import Any


def where(lst: list[Any], element: Any) -> list[int]:
    """Find the indices of all occurrences of an element in a list.

    Args:
        lst (list): The list to search.
        element (any): The element to look for in the list.

    Returns:
        list: A list of indices where the element is found in the input list.
    """

    return [i for i in range(len(lst)) if lst[i] == element]
