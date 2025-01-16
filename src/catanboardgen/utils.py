"""Module containing miscellaneous utilities."""


def where(l, element):
    """Find the indices of all occurrences of an element in a list.

    Args:
        l (list): The list to search.
        element (any): The element to look for in the list.

    Returns:
        list: A list of indices where the element is found in the input list.
    """

    return [i for i in range(len(l)) if l[i] == element]
