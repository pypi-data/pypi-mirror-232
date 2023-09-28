"""Modificatin Module testing"""

import os
from distutils import dir_util
from pprint import pprint as pp

import numpy as np
import pytest

from nastranio.cards import *
from nastranio.mesh_api import Mesh
from nastranio.registry import Registry

from .test_utils import df_from_csvstr


@pytest.fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    basename, _ = os.path.splitext(filename)
    test_dir, model = basename.split("__")

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


@pytest.fixture
def filled_reg(datadir):
    bulkpath = os.path.join(datadir, "stiffpanel.nas")
    _reg = Registry()
    _reg.from_bulkfile(bulkpath, nbprocs=8, progress=False)
    _reg.bind_mod_api(index_elems=("1d", "2d"))
    return _reg


def test_closest(filled_reg):
    reg = filled_reg
    closest_gids = reg.mesh.mod.rtrees.nearest_grids(
        coords=(-2, -1, 0), num_results=1, astype=list
    )
    assert closest_gids == [1]
    closest_eids = reg.mesh.mod.rtrees.nearest_elements(
        coords=(-2, -1, 0), num_results=1, astype=set
    )
    assert closest_eids == {"CBAR": {1, 28}, "CTRIA3": {106, 100}}


def test_move_node(filled_reg):
    reg = filled_reg
    # breakpoint()
    # move node#1 twice.
    reg.mesh.mod.node_move_by(1, vector=[-0.2, 0, 0.1])
    reg.mesh.mod.node_move_by(1, vector=[-0.2, 0, 0.1])
    # check new grid position
    xyz_fast = reg.container["bulk"]["GRID"].query_id_fast(
        1, columns=["X1", "X2", "X3"], asview=True
    )
    assert np.allclose(xyz_fast, [-2.4, -1, 0.2])
    xyz_slow = reg.container["bulk"]["GRID"].query_id(1, asview=float)[2:5]
    assert np.allclose(xyz_slow, [-2.4, -1, 0.2])
    xyz12 = reg.container["bulk"]["GRID"].query_id_fast(
        (1, 2), columns=["X1", "X2", "X3"], asview=True
    )
    assert np.allclose(xyz12, [[-2.4, -1.0, 0.2], [2.0, -1.0, 0.0]])

    xyz21 = reg.container["bulk"]["GRID"].query_id_fast(
        (2, 1), columns=["X2", "X1", "X3"], asview=True
    )
    assert np.allclose(xyz21, [[-1.0, 2.0, 0.0], [-1.0, -2.4, 0.2]])
    # check bboxes
    closest_gids = reg.mesh.mod.rtrees.nearest_grids(
        coords=(-2, -1, 0), num_results=1, astype=list
    )
    assert closest_gids == [28]
    closest_eids = reg.mesh.mod.rtrees.nearest_elements(
        coords=(-2, -1, 0), num_results=1, astype=set
    )
    assert closest_eids == {"CBAR": {1, 28}, "CTRIA3": {106, 100}}
