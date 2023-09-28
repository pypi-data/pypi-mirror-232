import numpy as np
import scipy.sparse
from typing import Tuple, Union

def rank(pcm: Union[scipy.sparse.spmatrix, np.ndarray]) -> int:
    """
    Calculate the rank of a given parity check matrix.
    
    Parameters:
        pcm (Union[scipy.sparse.spmatrix, np.ndarray]): The parity check matrix to be ranked.
        
    Returns:
        int: The rank of the parity check matrix.
    """
    ...

def kernel(pcm: Union[scipy.sparse.spmatrix, np.ndarray]) -> scipy.sparse.spmatrix:
    """
    Calculate the kernel of a given parity check matrix.
    
    Parameters:
        pcm (Union[scipy.sparse.spmatrix, np.ndarray]): The parity check matrix for kernel calculation.
        
    Returns:
        scipy.sparse.spmatrix: The kernel of the parity check matrix.
    """
    ...

def row_complement_basis(pcm: Union[scipy.sparse.spmatrix, np.ndarray]) -> scipy.sparse.spmatrix:
    """
    Calculate the row complement basis of a given parity check matrix.
    
    Parameters:
        pcm (Union[scipy.sparse.spmatrix, np.ndarray]): The parity check matrix for row complement basis calculation.
        
    Returns:
        scipy.sparse.spmatrix: The row complement basis of the parity check matrix.
    """
    ...


class PluDecomposition():

    def __init__(self, pcm: Union[scipy.sparse.spmatrix, np.ndarray], full_reduce: bool = False, lower_triangular: bool = True) -> None:
        """
        Initialise the PLU Decomposition with a given parity check matrix.
        
        Parameters:
            pcm (Union[scipy.sparse.spmatrix, np.ndarray]): The parity check matrix for PLU Decomposition.
            full_reduce (bool, optional): Flag to indicate if full row reduction is required. Default is False.
            lower_triangular (bool, optional): Flag to indicate if the result should be in lower triangular form. Default is True.
        """

        ...

    def lu_solve(self, y: np.ndarray) -> np.ndarray:
        """
        Solve the LU decomposition problem for a given array 'y'.
        
        Parameters:
            y (np.ndarray): Array to be solved.
            
        Returns:
            np.ndarray: Solution array.
        """

        ...

    @property
    def L(self) -> scipy.sparse.spmatrix:
        """
        Get the lower triangular matrix from the LU decomposition.
        
        Returns:
            scipy.sparse.spmatrix: Lower triangular matrix.
        """
        ...

    @property
    def U(self) -> scipy.sparse.spmatrix:
        """
        Get the upper triangular matrix from the LU decomposition.
        
        Returns:
            scipy.sparse.spmatrix: Upper triangular matrix.
        """
        ...

    @property
    def P(self) -> scipy.sparse.spmatrix:
        """
        Get the permutation matrix from the LU decomposition.
        
        Returns:
            scipy.sparse.spmatrix: Permutation matrix.
        """
        ...

    @property
    def rank(self) -> int:
        """
        Get the rank of the matrix used for the LU decomposition.
        
        Returns:
            int: Rank of the matrix.
        """
        ...

    @property
    def pivots(self) -> np.ndarray:
        """
        Get the pivot positions used during the LU decomposition.
        
        Returns:
            np.ndarray: Array of pivot positions.
        """
        ...