# Up-Down-Left-Right: A C++ Sparse Matrix Library

Up-down-left-right (UDLR) is a templated sparse matrix library designed the facilitate the development of algorithms that run on sparse graphs. The core datastructure is a quadrupally linked list representing the non-zero entries of the matrix. Every entry in this structure is connected with its immediate neighbours in the _up, down, left, and right_ directions. The quad-directional linked layout enables rapid matrix traversal both horizontally and vertically, making it highly efficient for algorithms such as Gaussian elimination. UDLR is fully templated, allowing for arbitrary meta data to be appended to each list entry. This is particularly useful for graph algorithms such as belief propagation in which messages are passed between nodes.

## CPP Installation

UDLR is a header only libary. Simply include the file and `udlr.hpp` and enjoy the library!

## Python Installation

Install using pip. Navigate to the repository root and run:

`pip install -Ue .`

## CPP Features

UDLR has initially been developed to provide sparse matrix operations over a GF2 field for applications in classical and quantum coding theory. As such, the sparse GF2 matrix is currently the most developed feature of this package. However, more functiionality will be added soon. The current fuctionality is listed below:

- A sparse GF2 matrix class. This class can be initialised with a custom node type that can contain user defined meta data.
- Function for performing linear algebra on GF2 matrices. Current funcitons include rank calculation, nullspace computation, LU decomposition and matrix inversion.
- Python bindings (via cython) for linear algebra operations on sparse GF2 matrices.









