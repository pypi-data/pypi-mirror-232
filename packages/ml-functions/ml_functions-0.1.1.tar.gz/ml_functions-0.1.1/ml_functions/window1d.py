import numpy as np
from typing import List


def window1d(
    input_array: List | np.ndarray, size: int, shift: int = 1, stride: int = 1
) -> List[List[float]]:
    
    """
    Generate a list of windows from a 1D array or list.

    Parameters:
    - input_array (list | np.ndarray): The array or list from which to create windows.
    - size (int): The size of each window.
    - shift (int, optional): The number of positions to shift the window for each iteration. Defaults to 1.
    - stride (int, optional): The stride (or step size) for elements within each window. Defaults to 1.

    Returns:
    - list[list] | np.ndarray: A list of windows (if input_array is a list) or a numpy array of windows
      (if input_array is a numpy array), each of which is a list.

    Examples:
    >>> window1d([1, 2, 3, 4, 5, 6], 2)
    [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]

    >>> window1d(np.array([1, 2, 3, 4, 5, 6]), 2, 2)
    array([[1, 2], [3, 4], [5, 6]])

    >>> window1d([1, 2, 3, 4, 5, 6], 2, 1, 2)
    [[1, 3], [2, 4], [3, 5], [4, 6]]
    """

    if not isinstance(input_array, (list, np.ndarray)) or input_array is None:
        raise TypeError("input_array must be a non-empty list or numpy array.")
    if not isinstance(size, int) or size <= 0 or size > len(input_array):
        raise ValueError("size must be a positive integer not exceeding the length of input_array.")
    if not isinstance(shift, int) or shift <= 0:
        raise ValueError("shift must be a positive integer.")
    if not isinstance(stride, int) or stride <= 0:
        raise ValueError("stride must be a positive integer.")
    
    windows = []
    i = 0
    while i + (size * stride) - stride < len(input_array):
        window = [input_array[i + (j * stride)] for j in range(size)]
        windows.append(window)
        i += shift
    if isinstance(input_array, list):
        return windows
    else:
        return np.array(windows)