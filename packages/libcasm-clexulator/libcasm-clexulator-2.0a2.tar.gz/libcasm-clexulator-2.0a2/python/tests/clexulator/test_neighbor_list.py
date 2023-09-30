import numpy as np

import libcasm.xtal.lattices as xtal_lattices
from libcasm.clexulator import PrimNeighborList


def test_make_weight_matrix():
    lattice = xtal_lattices.FCC(r=1.0)
    W = PrimNeighborList.make_weight_matrix(lattice.column_vector_matrix())
    W_expected = np.array(
        [
            [2, 1, 1],
            [1, 2, 1],
            [1, 1, 2],
        ],
        dtype=int,
    )
    assert np.allclose(W, W_expected)


def test_prim_neighbor_list_1():
    prim_neighbor_list = PrimNeighborList()
    assert isinstance(prim_neighbor_list, PrimNeighborList)


def test_prim_neighbor_list_2():
    lattice = xtal_lattices.FCC(r=1.0)
    W = PrimNeighborList.make_weight_matrix(lattice.column_vector_matrix())
    prim_neighbor_list = PrimNeighborList(W, [0], 1)
    assert isinstance(prim_neighbor_list, PrimNeighborList)
