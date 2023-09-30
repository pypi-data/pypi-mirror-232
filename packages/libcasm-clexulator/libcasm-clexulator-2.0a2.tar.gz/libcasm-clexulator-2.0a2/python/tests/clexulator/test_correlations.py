import json

import numpy as np
import pytest

import libcasm.clexulator as clex
import libcasm.xtal as xtal

from .functions import make_source


@pytest.mark.slow
@pytest.mark.very_slow
def test_calc_intensive_correlations(session_shared_datadir):
    source = make_source(session_shared_datadir, "OccClexulatorZrOTest", "default")

    with open(session_shared_datadir / "ZrO_prim.json", "r") as f:
        xtal_prim = xtal.Prim.from_dict(json.load(f))
    prim_neighbor_list = clex.PrimNeighborList()
    clexulator = clex.make_clexulator(source, prim_neighbor_list)

    T = np.array([[2, 0, 0], [0, 2, 0], [0, 0, 1]], dtype=int)
    supercell_neighbor_list = clex.SuperNeighborList(T, prim_neighbor_list)
    n_unitcells = round(np.linalg.det(T))

    dof_values = clex.make_default_config_dof_values(xtal_prim, n_unitcells)
    assert len(dof_values.occupation()) == 4 * n_unitcells
    correlations = clex.calc_intensive_correlations(
        clexulator, dof_values, supercell_neighbor_list
    )
    assert isinstance(correlations, np.ndarray)
    assert len(correlations) == 74


@pytest.mark.slow
@pytest.mark.very_slow
def test_calc_local_correlations(session_shared_datadir):
    source = make_source(session_shared_datadir, "LocalOccClexulatorZrOTest", "hop0")

    with open(session_shared_datadir / "ZrO_prim.json", "r") as f:
        xtal_prim = xtal.Prim.from_dict(json.load(f))
    prim_neighbor_list = clex.PrimNeighborList()
    local_clexulator = clex.make_local_clexulator(source, prim_neighbor_list)
    assert local_clexulator.n_equivalents() == 2

    T = np.array([[2, 0, 0], [0, 2, 0], [0, 0, 1]], dtype=int)
    supercell_neighbor_list = clex.SuperNeighborList(T, prim_neighbor_list)
    n_unitcells = round(np.linalg.det(T))

    dof_values = clex.make_default_config_dof_values(xtal_prim, n_unitcells)
    assert len(dof_values.occupation()) == 4 * n_unitcells
    dof_values.set_occ(n_unitcells * 2, 1)

    for unitcell_index in range(n_unitcells):
        for equivalent_index in range(local_clexulator.n_equivalents()):
            correlations = clex.calc_local_correlations(
                local_clexulator,
                dof_values,
                supercell_neighbor_list,
                unitcell_index,
                equivalent_index,
            )
            assert isinstance(correlations, np.ndarray)
            assert len(correlations) == 33
            print(unitcell_index, equivalent_index, correlations.tolist())
