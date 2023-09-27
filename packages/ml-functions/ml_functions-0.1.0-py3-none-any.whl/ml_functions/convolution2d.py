import numpy as np


def convolution2d(
    input_matrix: np.ndarray, kernel: np.ndarray, stride: int = 1
) -> np.ndarray:
    """
    Compute 2D cross-correlation between an input matrix and a kernel.

    Parameters:
    - input_matrix (np.ndarray): 2D array representing the input matrix.
    - kernel (np.ndarray): 2D array representing the kernel.
    - stride (int, optional): Stride for the convolution. The parameter is included for
      future implementations, but not currently used. Defaults to 1.

    Returns:
    - np.ndarray: 2D array representing the result of the convolution.

    Examples:
    >>> input_matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> kernel = np.array([[1, 0], [0, -1]])
    >>> convolution2d(input_matrix, kernel)
    array([[  1.,   2.],
           [-3.,  -4.]])
    """

    h, w = kernel.shape
    Y = np.zeros((input_matrix.shape[0] - h + 1, input_matrix.shape[1] - w + 1))
    for i in range(Y.shape[0]):
        for j in range(Y.shape[1]):
            Y[i, j] = (input_matrix[i : i + h, j : j + w] * kernel).sum()
    return Y
