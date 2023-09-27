import numpy as np


def window1d(
    input_array: list | np.ndarray, size: int, shift: int = 1, stride: int = 1
) -> list[float]:
    """
    Generate a list of windows from a 1D array or list.

    Parameters:
    - input_array (list | np.ndarray): The array or list from which to create windows.
    - size (int): The size of each window.
    - shift (int, optional): The number of positions to shift the window for each iteration. Defaults to 1.
    - stride (int, optional): The stride (or step size) for elements within each window. Defaults to 1.

    Returns:
    - list[list]: A list of windows, each of which is a list.

    Examples:
    >>> window1d([1, 2, 3, 4, 5, 6], 2)
    [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]

    >>> window1d([1, 2, 3, 4, 5, 6], 2, 2)
    [[1, 2], [3, 4], [5, 6]]

    >>> window1d([1, 2, 3, 4, 5, 6], 2, 1, 2)
    [[1, 3], [2, 4], [3, 5], [4, 6]]
    """

    windows = []
    i = 0
    while i + (size * stride) - stride < len(input_array):
        window = [input_array[i + (j * stride)] for j in range(size)]
        windows.append(window)
        i += shift
    return windows
