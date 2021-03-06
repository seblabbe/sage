include "../ext/cdefs.pxi"

cimport matrix_dense
cimport sage.rings.integer
from sage.rings.integer cimport Integer

cdef extern from "../ext/multi_modular.h":
    ctypedef unsigned long mod_int

ctypedef long* GEN

cdef class Matrix_integer_dense(matrix_dense.Matrix_dense):
    cdef char _initialized
    cdef mpz_t *_entries
    cdef mpz_t **_matrix
    cdef object _pivots
    cdef int mpz_height(self, mpz_t height) except -1
    cpdef double _log_avg_sq1(self) except -1.0
    cdef _mod_int_c(self, mod_int modulus)
    cdef _mod_two(self)

    cdef _zero_out_matrix(self)
    cdef _new_unitialized_matrix(self, Py_ssize_t nrows, Py_ssize_t ncols)
    cdef _pickle_version0(self)
    cdef _unpickle_version0(self, data)
    cpdef _export_as_string(self, int base=?)

    cdef _init_linbox(self)
    cdef void reduce_entry_unsafe(self, Py_ssize_t i, Py_ssize_t j, Integer modulus)

    # HNF Modn
    cdef int _hnf_modn(Matrix_integer_dense self, Matrix_integer_dense res,
            mod_int det) except -1
    cdef long long* _hnf_modn_impl(Matrix_integer_dense self, mod_int det,
                                   Py_ssize_t nrows, Py_ssize_t ncols) except NULL
    cdef _new_uninitialized_matrix(self, Py_ssize_t nrows, Py_ssize_t ncols)

    cdef extract_hnf_from_pari_matrix(self, GEN H, int flag, bint include_zero_rows)

cdef int four_dim_det(mpz_t, mpz_t *) except -1
cpdef _lift_crt(Matrix_integer_dense M, residues, moduli=*)

################################################################
# fast conversion to PARI on the stack
################################################################
cdef inline GEN pari_GEN(Matrix_integer_dense B)
