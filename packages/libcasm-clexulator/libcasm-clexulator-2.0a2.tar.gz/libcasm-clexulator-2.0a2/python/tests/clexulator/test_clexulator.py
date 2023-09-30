import pytest

from libcasm.clexulator import (
    Clexulator,
    LocalClexulator,
    PrimNeighborList,
    make_clexulator,
    make_local_clexulator,
)

from .functions import make_source


def test_constructor():
    clexulator = Clexulator()
    assert isinstance(clexulator, Clexulator)


@pytest.mark.slow
@pytest.mark.very_slow
def test_make_clexulator_1(session_shared_datadir):
    source = make_source(session_shared_datadir, "OccClexulatorZrOTest", "default")

    prim_neighbor_list = PrimNeighborList()
    clexulator = make_clexulator(source, prim_neighbor_list)
    assert isinstance(clexulator, Clexulator)
    assert clexulator.n_functions() == 74


@pytest.mark.slow
@pytest.mark.very_slow
def test_make_local_clexulator(session_shared_datadir):
    source = make_source(session_shared_datadir, "LocalOccClexulatorZrOTest", "hop0")

    prim_neighbor_list = PrimNeighborList()
    hop0_clexulator = make_local_clexulator(source, prim_neighbor_list)
    assert isinstance(hop0_clexulator, LocalClexulator)
    assert hop0_clexulator.n_equivalents() == 2
    assert hop0_clexulator.n_functions() == 33


@pytest.mark.slow
@pytest.mark.very_slow
def test_make_periodic_and_local_clexulator(session_shared_datadir):
    prim_neighbor_list = PrimNeighborList()

    source = make_source(session_shared_datadir, "OccClexulatorZrOTest", "default")
    clexulator = make_clexulator(source, prim_neighbor_list)
    assert isinstance(clexulator, Clexulator)
    assert clexulator.n_functions() == 74

    source = make_source(session_shared_datadir, "LocalOccClexulatorZrOTest", "hop0")
    hop0_clexulator = make_local_clexulator(source, prim_neighbor_list)
    assert isinstance(hop0_clexulator, LocalClexulator)
    assert hop0_clexulator.n_equivalents() == 2
    assert hop0_clexulator.n_functions() == 33

    source = make_source(session_shared_datadir, "LocalOccClexulatorZrOTest", "hop1")
    hop1_clexulator = make_local_clexulator(source, prim_neighbor_list)
    assert isinstance(hop1_clexulator, LocalClexulator)
    assert hop1_clexulator.n_equivalents() == 2
    assert hop0_clexulator.n_functions() == 33
