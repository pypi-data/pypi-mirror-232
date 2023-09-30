import numpy as np
import pytest

import libcasm.xtal as xtal
import libcasm.xtal.prims as xtal_prims
from libcasm.clexulator import ConfigDoFValues, make_default_config_dof_values


def test_constructor():
    dof_values = ConfigDoFValues()
    assert isinstance(dof_values, ConfigDoFValues)


def test_constructor_2():
    xtal_prim = xtal_prims.FCC(r=1.0, occ_dof=["A", "B", "Va"])
    n_unitcells = 2
    dof_values = make_default_config_dof_values(xtal_prim, n_unitcells)
    assert isinstance(dof_values, ConfigDoFValues)
    assert dof_values.occupation().shape == (2,)


def test_constructor_3():
    xtal_prim = xtal_prims.HCP(r=1.0, occ_dof=["A", "B", "Va"])
    n_unitcells = 2
    dof_values = make_default_config_dof_values(xtal_prim, n_unitcells)
    assert isinstance(dof_values, ConfigDoFValues)
    assert dof_values.occupation().shape == (4,)
    assert dof_values.occupation().shape == (4,)


def test_constructor_4():
    xtal_prim = xtal_prims.HCP(
        r=1.0,
        occ_dof=["A", "B", "Va"],
        local_dof=[xtal.DoFSetBasis("disp")],
        global_dof=[xtal.DoFSetBasis("Hstrain")],
    )
    n_unitcells = 2
    dof_values = make_default_config_dof_values(xtal_prim, n_unitcells)
    assert isinstance(dof_values, ConfigDoFValues)
    assert dof_values.occupation().shape == (4,)


def test_occupation():
    dof_values = ConfigDoFValues()

    occupation_in = np.array([1, 0, 0, 0], dtype=int)
    # this sets using a copy
    dof_values.set_occupation(occupation_in)

    occupation_out = dof_values.occupation()
    assert np.allclose(occupation_in, occupation_out)

    # so this has no effect
    occupation_in[0] = 2
    assert dof_values.occ(0) == 1

    # but this does
    dof_values.set_occ(0, 2)
    assert dof_values.occ(0) == 2


def test_occupation_2():
    dof_values = ConfigDoFValues()

    occupation_in = np.array([1, 0, 0, 0], dtype=int)
    dof_values.set_occupation(occupation_in)

    # this returns a const reference np.ndarray (writeable==False,owndata==False)
    # so occupation_out should be ready-only
    occupation_out = dof_values.occupation()
    assert np.allclose(occupation_in, occupation_out)
    with pytest.raises(ValueError):
        occupation_out[0] = 2
    assert dof_values.occ(0) == 1
    assert occupation_out.flags.writeable is False
    assert occupation_out.flags.owndata is False


def test_copy_config_dof_values():
    import copy

    dof_values_1 = ConfigDoFValues()

    occupation_in = np.array([1, 0, 0, 0], dtype=int)
    dof_values_1.set_occupation(occupation_in)

    dof_values_2 = copy.copy(dof_values_1)
    assert isinstance(dof_values_1, ConfigDoFValues)
    assert isinstance(dof_values_2, ConfigDoFValues)
    assert dof_values_1 is not dof_values_2
