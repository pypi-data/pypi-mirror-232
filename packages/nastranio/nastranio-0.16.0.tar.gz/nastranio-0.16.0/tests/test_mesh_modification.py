"""
test nastranio.mesh_api.mod.py

Read a gmsh mesh file

(Pdb++) act_coords
     csys     X     Y     Z
gid
1       0   0.0   0.0   0.0
2       0 -50.0   0.0   0.0
3       0 -50.0  30.0   0.0
4       0   0.0  30.0   0.0
5       0   0.0   0.0  10.0
6       0 -50.0   0.0  10.0
7       0 -50.0  30.0  10.0
8       0   0.0  30.0  10.0
"""
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from nastranio.registry import Registry


@pytest.fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = Path(request.module.__file__)
    return filename.parent / "test_mod"


@pytest.fixture
def filled_reg(datadir):
    bulkpath = datadir / "frame_1d.nas"
    _reg = Registry()
    _reg.from_bulkfile(bulkpath, nbprocs=8, progress=False)
    _reg.bind_mod_api(index_elems=("1d",))
    return _reg


def test_initial_state(filled_reg):
    reg = filled_reg
    grids = reg.container["bulk"]["GRID"]
    act_coords = grids.coords(asdf=True)
    expected_coords = {
        "csys": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0},
        "X": {1: 0.0, 2: -50.0, 3: -50.0, 4: 0.0, 5: 0.0, 6: -50.0, 7: -50.0, 8: 0.0},
        "Y": {1: 0.0, 2: 0.0, 3: 30.0, 4: 30.0, 5: 0.0, 6: 0.0, 7: 30.0, 8: 30.0},
        "Z": {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 10.0, 6: 10.0, 7: 10.0, 8: 10.0},
    }

    expected_coords = pd.DataFrame(expected_coords)
    expected_coords.index.names = ["gid"]
    diff = act_coords - expected_coords
    assert np.alltrue(diff == 0)


def test_move_node_by(filled_reg):
    """move Node2 to [-49.6, 0.5, -0.5], using vector"""
    reg = filled_reg
    reg.mesh.mod.node_move_by(2, [0.4, 0.5, -0.5])
    grids = reg.container["bulk"]["GRID"]
    act_coords = grids.coords(asdf=True)
    expected_coords = {
        "csys": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0},
        "X": {1: 0.0, 2: -49.6, 3: -50.0, 4: 0.0, 5: 0.0, 6: -50.0, 7: -50.0, 8: 0.0},
        "Y": {1: 0.0, 2: 0.5, 3: 30.0, 4: 30.0, 5: 0.0, 6: 0.0, 7: 30.0, 8: 30.0},
        "Z": {1: 0.0, 2: -0.5, 3: 0.0, 4: 0.0, 5: 10.0, 6: 10.0, 7: 10.0, 8: 10.0},
    }

    expected_coords = pd.DataFrame(expected_coords)
    expected_coords.index.names = ["gid"]
    diff = act_coords - expected_coords
    assert np.alltrue(diff == 0)
    modified_bulk = reg.to_nastran()
    fh = StringIO()
    fh.write(modified_bulk)
    fh.seek(0)
    reg2 = Registry()
    reg2.from_bulkfile(fh)
    checked_coords = reg2.container["bulk"]["GRID"].coords(asdf=True).to_dict()
    assert checked_coords == expected_coords.to_dict()


def test_node_move_to(filled_reg):
    """move Node2 to [-49.6, 0.5, -0.5], using vector"""
    reg = filled_reg
    reg.mesh.mod.node_move_to(2, [-49.6, 0.5, -0.5])
    grids = reg.container["bulk"]["GRID"]
    act_coords = grids.coords(asdf=True)
    expected_coords = {
        "csys": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0},
        "X": {1: 0.0, 2: -49.6, 3: -50.0, 4: 0.0, 5: 0.0, 6: -50.0, 7: -50.0, 8: 0.0},
        "Y": {1: 0.0, 2: 0.5, 3: 30.0, 4: 30.0, 5: 0.0, 6: 0.0, 7: 30.0, 8: 30.0},
        "Z": {1: 0.0, 2: -0.5, 3: 0.0, 4: 0.0, 5: 10.0, 6: 10.0, 7: 10.0, 8: 10.0},
    }

    expected_coords = pd.DataFrame(expected_coords)
    expected_coords.index.names = ["gid"]
    diff = act_coords - expected_coords
    assert np.alltrue(diff == 0)
    modified_bulk = reg.to_nastran()
    fh = StringIO()
    fh.write(modified_bulk)
    fh.seek(0)
    reg2 = Registry()
    reg2.from_bulkfile(fh)
    checked_coords = reg2.container["bulk"]["GRID"].coords(asdf=True).to_dict()
    assert checked_coords == expected_coords.to_dict()


def test_nearest_grid(filled_reg):
    reg = filled_reg
    closest_gids = reg.mesh.mod.rtrees.nearest_grids(
        coords=(-50, 30, 0), num_results=3, astype=list
    )
    assert closest_gids == [3, 7, 2]
    # grids = reg.container["bulk"]["GRID"]
    # act_coords = grids.coords(asdf=True)
    closest_gids = reg.mesh.mod.rtrees.nearest_grids(
        coords=(-49.9, 30.2, 0.1), num_results=3, astype=list
    )
    assert closest_gids == [3, 7, 2]
    # -------------------------------------------------------------------------
    # nearest elements
    closest_eids = reg.mesh.mod.rtrees.nearest_elements(
        coords=(-49.9, 30.2, 0.1), num_results=2, astype=list, cardname=None
    )
    assert closest_eids == {"CBAR": [11, 20]}

    closest_eids = reg.mesh.mod.rtrees.nearest_elements(
        coords=(-49.9, 30.2, 0.1), num_results=2, astype=list, cardname="CBAR"
    )
    assert closest_eids == [11, 20]


def test_node_add(filled_reg):
    reg = filled_reg
    coords = reg.container["bulk"]["GRID"].coords(asdf=True)
    assert len(coords) == 8  # not modified mesh
    # -------------------------------------------------------------------------
    # check that creating a node with an exiting gid raise a ValueError
    with pytest.raises(ValueError) as e_info:
        reg.mesh.mod.node_add(gid=1, coords=(10, 11, 12))
    # -------------------------------------------------------------------------
    # creating a node
    created_gid = reg.mesh.mod.node_add(coords=(10.1, 11, 12), clear_caches=True)
    assert created_gid == 9
    coords = reg.container["bulk"]["GRID"].coords(asdf=True)
    assert len(coords) == 9
    assert coords.loc[9].to_dict() == {"csys": 0.0, "X": 10.1, "Y": 11.0, "Z": 12.0}
    # -------------------------------------------------------------------------
    # creating a node
    created_gid = reg.mesh.mod.node_add(
        gid=100, coords=(10.1, 11, -12), clear_caches=True
    )
    assert created_gid == 100
    coords = reg.container["bulk"]["GRID"].coords(asdf=True)
    assert len(coords) == 10
    assert coords.loc[100].to_dict() == {"csys": 0.0, "X": 10.1, "Y": 11.0, "Z": -12.0}
    # -------------------------------------------------------------------------
    # check that RTREES are updated
    closest_gids = reg.mesh.mod.rtrees.nearest_grids(
        coords=(10.1, 11, -12), num_results=1, astype=list
    )
    assert closest_gids == [100]


def test_split1d_knowing_eid(filled_reg):
    reg = filled_reg
    card, new_eid, new_gid = reg.mesh.mod.elem1d_split(
        eid=12, where=0.25, clear_caches=True
    )
    assert reg.mesh.eid2gids()[new_eid] == {9, 1}
    assert reg.mesh.eid2gids(keep_order=True)[new_eid] == [9, 1]
    assert reg.mesh.eid2gids()[12] == {4, 9}
    assert reg.mesh.eid2gids(keep_order=True)[12] == [4, 9]

    assert card.eid2gids()[new_eid] == {9, 1}
    assert card.eid2gids(keep_order=True)[new_eid] == [9, 1]
    assert card.eid2gids()[12] == {4, 9}
    assert card.eid2gids(keep_order=True)[12] == [4, 9]
    assert reg.mesh.coords(asdf=True).loc[new_gid][["X", "Y", "Z"]].to_dict() == {
        "X": 0.0,
        "Y": 22.5,
        "Z": 0.0,
    }
    directions = reg.mesh.normals().loc[[12, new_eid]].to_dict()
    assert directions == {
        "X": {12: 0.0, 21: 0.0},
        "Y": {12: -1.0, 21: -1.0},
        "Z": {12: 0.0, 21: 0.0},
    }


def test_multiple_split1d_all_CBAR(filled_reg):
    reg = filled_reg
    points = [
        [-12.5, 1, 11],  # on eid13
        [-25, -2, -16],  # on eid9
        [5, 3, -2],  # on eid12
        [-49.99, -1, -11],  # should be merged with node gid2
        [-37.5, -2, 16],  # on eid13
    ]
    details = reg.mesh.mod.multiple_elem1d_split(points, "CBAR")
    # reg.to_nastran("/home/nic/toto2.nas")
    exp = [
        {"XA": -12.5, "XB": 0.0, "XC": 10.0, "eid": 21, "gid": 9, "prev_eid": 13},
        {"XA": -25.0, "XB": 0.0, "XC": 0.0, "eid": 22, "gid": 10, "prev_eid": 9},
        {"XA": 0.0, "XB": 3.0, "XC": 0.0, "eid": 23, "gid": 11, "prev_eid": 12},
        {"XA": -50.0, "XB": 0.0, "XC": 0.0, "eid": None, "gid": 2, "prev_eid": None},
        {"XA": -37.5, "XB": 0.0, "XC": 10.0, "eid": 24, "gid": 12, "prev_eid": 13},
    ]
    assert details == exp
    assert reg.mesh.eid2card()[22] == "CBAR"
    assert reg.mesh.eid2gids()[22] == {2, 10}
    assert reg.mesh.eid2gids(keep_order=True)[22] == [10, 2]
    eids_bbox = reg.mesh.eid2bbox()
    eid22_bbox = eids_bbox.loc[22].to_dict()
    assert eid22_bbox == {
        "X1_min": -50.0,
        "X2_min": 0.0,
        "X3_min": 0.0,
        "X1_max": -25.0,
        "X2_max": 0.0,
        "X3_max": 0.0,
    }


def test_multiple_split1d_on_specific_rtree(filled_reg):
    reg = filled_reg
    # reg.to_nastran("/home/nic/toto.nas")
    points = [
        [-12.5, 1, 11],  # on eid13
        [-25, -2, -16],  # on eid13
        [5, 3, -2],  # on eid16
        [-49.99, -1, -11],  # should be merged with node gid6
        [-37.5, -2, 16],  # on eid13
    ]
    rtree = reg.mesh.mod.rtrees.create_rtree(eids=(13, 14, 15, 16))
    details = reg.mesh.mod.multiple_elem1d_split(points, "CBAR", rtree=rtree)
    # reg.to_nastran("/home/nic/toto3.nas")
    exp = [
        {"XA": -12.5, "XB": 0.0, "XC": 10.0, "eid": 21, "gid": 9, "prev_eid": 13},
        {"XA": -25.0, "XB": 0.0, "XC": 10.0, "eid": 22, "gid": 10, "prev_eid": 13},
        {"XA": 0.0, "XB": 3.0, "XC": 10.0, "eid": 23, "gid": 11, "prev_eid": 16},
        {"XA": -50.0, "XB": 0.0, "XC": 10.0, "eid": None, "gid": 6, "prev_eid": None},
        {"XA": -37.5, "XB": 0.0, "XC": 10.0, "eid": 24, "gid": 12, "prev_eid": 13},
    ]
    assert details == exp
    assert reg.mesh.eid2card()[22] == "CBAR"
    assert reg.mesh.eid2gids()[22] == {10, 12}
    assert reg.mesh.eid2gids(keep_order=True)[22] == [10, 12]
    eids_bbox = reg.mesh.eid2bbox()
    eid22_bbox = eids_bbox.loc[22].to_dict()
    assert eid22_bbox == {
        "X1_min": -37.5,
        "X2_min": 0.0,
        "X3_min": 10.0,
        "X1_max": -25.0,
        "X2_max": 0.0,
        "X3_max": 10.0,
    }


def test_multiple_split1d_on_specific_eids(filled_reg):
    reg = filled_reg
    # reg.to_nastran("/home/nic/toto.nas")
    points = [
        [-12.5, 1, 11],  # on eid13
        [-25, -2, -16],  # on eid13
        [5, 3, -2],  # on eid16
        [-49.99, -1, -11],  # should be merged with node gid6
        [-37.5, -2, 16],  # on eid13
    ]
    details = reg.mesh.mod.multiple_elem1d_split(points, "CBAR", eids=(13, 14, 15, 16))
    # reg.to_nastran("/home/nic/toto3.nas")
    exp = [
        {"XA": -12.5, "XB": 0.0, "XC": 10.0, "eid": 21, "gid": 9, "prev_eid": 13},
        {"XA": -25.0, "XB": 0.0, "XC": 10.0, "eid": 22, "gid": 10, "prev_eid": 13},
        {"XA": 0.0, "XB": 3.0, "XC": 10.0, "eid": 23, "gid": 11, "prev_eid": 16},
        {"XA": -50.0, "XB": 0.0, "XC": 10.0, "eid": None, "gid": 6, "prev_eid": None},
        {"XA": -37.5, "XB": 0.0, "XC": 10.0, "eid": 24, "gid": 12, "prev_eid": 13},
    ]
    assert details == exp
    assert reg.mesh.eid2card()[22] == "CBAR"
    assert reg.mesh.eid2gids()[22] == {10, 12}
    assert reg.mesh.eid2gids(keep_order=True)[22] == [10, 12]
    eids_bbox = reg.mesh.eid2bbox()
    eid22_bbox = eids_bbox.loc[22].to_dict()
    assert eid22_bbox == {
        "X1_min": -37.5,
        "X2_min": 0.0,
        "X3_min": 10.0,
        "X1_max": -25.0,
        "X2_max": 0.0,
        "X3_max": 10.0,
    }
