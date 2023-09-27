#cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True, embedsignature=True
# distutils: language = c++
from libc.stdlib cimport malloc, calloc, free
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr, make_shared
cimport numpy as np
ctypedef np.uint8_t uint8_t

cdef extern from "sparse_matrix_base.hpp" namespace "udlr::sparse_matrix_base":
    cdef cppclass CsrMatrix "udlr::sparse_matrix_base::CsrMatrix":
        int m
        int n
        vector[vector[int]] row_adjacency_list
        int entry_count

cdef extern from "gf2sparse.hpp" namespace "udlr::gf2sparse":

    cdef cppclass GF2Entry "udlr::gf2sparse::GF2Entry":
        GF2Entry() except +
        int row_index
        int col_index
        bool at_end()

    cdef cppclass GF2Sparse "udlr::gf2sparse::GF2Sparse<udlr::gf2sparse::GF2Entry>":
        int m
        int n
        GF2Sparse() except +
        GF2Sparse(int m, int n) except +
        GF2Entry& insert_entry(int j, int i)
        GF2Entry& get_entry(int i, int j)
        GF2Sparse transpose()
        vector[uint8_t]& mulvec(vector[uint8_t]& input_vector, vector[uint8_t]& output_vector)
        vector[vector[int]] nonzero_coordinates()
        int entry_count()
        vector[vector[int]] row_adjacency_list()
        CsrMatrix to_csr()


cdef extern from "gf2sparse_linalg.hpp" namespace "udlr::gf2sparse_linalg":

    cdef cppclass RowReduce "udlr::gf2sparse_linalg::RowReduce<udlr::gf2sparse::GF2Entry>":
        RowReduce() except +
        RowReduce(GF2Sparse& A) except +
        vector[int] rows
        vector[int] cols
        GF2Sparse L
        GF2Sparse U
        GF2Sparse P
        int rank
        int rref(bool full_reduce, bool lower_triangular)
        vector[uint8_t]& lu_solve(vector[uint8_t]& y)
        void build_p_matrix()
        vector[int] pivots

    CsrMatrix cy_kernel(GF2Sparse* mat)
    CsrMatrix cy_row_complement_basis(GF2Sparse* mat)

cdef class PluDecomposition():
    cdef bool MEM_ALLOCATED
    cdef bool full_reduce
    cdef bool lower_triangular
    cdef bool L_cached
    cdef bool U_cached
    cdef bool P_cached
    cdef int m
    cdef int n
    cdef GF2Sparse* cpcm
    cdef RowReduce* rr
    cdef object Lmat
    cdef object Umat
    cdef object Pmat





    

