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

    if not isinstance(input_matrix, np.ndarray):
        raise TypeError("input_matrix must be a numpy ndarray.")
    if not isinstance(kernel, np.ndarray):
        raise TypeError("kernel must be a numpy ndarray.")
    if not isinstance(stride, int) or stride <= 0:
        raise ValueError("stride must be a positive integer.")
    if input_matrix.ndim != 2:
        raise ValueError("input_matrix must be a 2D array.")
    if kernel.ndim != 2:
        raise ValueError("kernel must be a 2D array.")
    if kernel.shape[0] > input_matrix.shape[0] or kernel.shape[1] > input_matrix.shape[1]:
        raise ValueError("kernel dimensions must be less than or equal to those of the input_matrix.")
    
    height, width = kernel.shape
    output_matrix = np.zeros((input_matrix.shape[0] - height + 1, input_matrix.shape[1] - width + 1))
    for i in range(output_matrix.shape[0]):
        for j in range(output_matrix.shape[1]):
            output_matrix[i, j] = (input_matrix[i : i + height, j : j + width] * kernel).sum()
    return output_matrix
