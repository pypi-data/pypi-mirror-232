def transpose2d(input_matrix: list[list[float]]) -> list:
    """
    Transposes a 2D matrix.

    Parameters:
    - input_matrix (list[list[float]]): The 2D matrix to be transposed.
    Each inner list represents a row.

    Returns:
    - list: A new 2D matrix where the rows are the columns of the input matrix,
    and the columns are the rows of the input matrix.

    Examples:
    >>> transpose2d([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    [[1.0, 4.0, 7.0], [2.0, 5.0, 8.0], [3.0, 6.0, 9.0]]

    >>> transpose2d([[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]])
    [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]

    >>> transpose2d([[1.0]])
    [[1.0]]
    """

    num_rows = len(input_matrix)
    num_cols = len(input_matrix[0])

    transposed = [[None] * num_rows for _ in range(num_cols)]

    for i in range(num_rows):
        for j in range(num_cols):
            transposed[j][i] = input_matrix[i][j]

    return transposed
