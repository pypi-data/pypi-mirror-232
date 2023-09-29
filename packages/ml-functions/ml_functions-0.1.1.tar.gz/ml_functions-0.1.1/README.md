# ml_functions: A Machine Learning Functions Package

## Overview

The `ml_functions` package provides a collection of Python functions designed for various machine learning tasks. The package currently includes:

- `convolution2d`: Perform 2D cross-correlation between an input matrix and a kernel.
- `transpose`: Transpose a 2D matrix.
- `window1d`: Generate a list of windows from a 1D array or list.

## Installation

This package uses Poetry for dependency management. To install the package, first, ensure you have [Poetry installed](https://python-poetry.org/docs/#installation).

Then, run:

```bash
poetry install
```

This package is also available on pypi: https://pypi.org/project/ml-functions/

## Usage

### convolution2d

Perform 2D cross-correlation.

The convolution2d function slides a kernel over the input matrix, computes the element-wise product of the kernel and the corresponding sub-matrix at each position, and sums up these products. It utilizes nested loops to iterate over the rows and columns of the output matrix, extracting sub-matrices from the input matrix and performing element-wise multiplication with the kernel.


Image Feature Extraction:

Convolution operations are fundamental to Convolutional Neural Networks (CNNs). Before feeding an image into a CNN, it might be preprocessed using various kernels to extract features like edges, textures, and corners. For instance, you might use a Sobel filter (used in edge detection to detect brightness changes) to detect edges in an image.


```python
from ml_functions import convolution2d
result = convolution2d(
    input_matrix: np.ndarray, kernel: np.ndarray, stride: int = 1)
```


### transpose2d

Transposes a 2D matrix.

Matrix Operations in Neural Networks:

While designing neural networks, especially fully connected layers or when visualizing certain types of data, you may need to transpose weight matrices or the input matrix itself to match the required shape for matrix multiplication.

For example, if you have an input vector x of shape (m, 1) and weight matrix W of shape (n, m), then before you perform the dot product (an operation performed by each artificial neuron in the network), you might need to transpose W to make it of shape (m, n).

```python
from ml_functions import transpose2d
result = transpose2d(input_matrix: list[list[int]])
```


### window1d

Generate a list of windows from a 1D array or list.

Time Series Analysis:

When working with time series data, it's often necessary to break the series down into smaller overlapping or non-overlapping windows for analysis. This is particularly useful for tasks like anomaly detection, where you'd want to compute statistics like mean and standard deviation for local windows to identify anomalies. With this function you can change the size of the window, how it changes with each iteration (shift), and how many steps to take before generating the next window (stride).

```python
from ml_functions import window1d
result = window1d(
    input_array: list | np.ndarray, size: int, shift: int = 1, stride: int = 1)
```

### Tests

Basic tests for the functions in the package are included in the tests directory. Each function has corresponding test cases that are designed to verify the accuracy and efficiency of the functions under different circumstances. Error testing has yet to be added.