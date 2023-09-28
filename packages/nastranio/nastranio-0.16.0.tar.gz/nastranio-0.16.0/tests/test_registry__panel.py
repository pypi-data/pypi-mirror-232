#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests nastranio.Registry"""

import os
from distutils import dir_util
from pprint import pprint as pp

import numpy as np
import pandas as pd
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
    bulkpath = os.path.join(datadir, "test_panels.dat")
    _reg = Registry()
    _reg.from_bulkfile(bulkpath, nbprocs="auto", progress=False)
    return _reg


def test_00(filled_reg):
    reg = filled_reg
    pp(list(reg.container.keys()))
    exp = set(["exec", "params", "comments", "bulk", "cases", "meta", "summary"])
    assert set(reg.container.keys()) == exp


# def test_json_import_export(filled_reg):
#     reg = filled_reg
#     txt = reg.to_json()
#     reg2 = Registry()
#     reg2.from_json(txt)
#     assert reg == reg2


def test_msgpack_import_export(filled_reg):
    reg = filled_reg
    data = reg.to_msgpack()
    reg2 = Registry()
    reg2.from_msgpack(data)
    assert reg == reg2


def test_msgpack_serialize_unserialize(filled_reg):
    reg = filled_reg
    fname = reg.to_file(fmt="pack")
    reg2 = Registry()
    reg2.from_file(fname)
    assert reg == reg2


def test_json_serialize_unserialize(filled_reg):
    reg = filled_reg
    fname = reg.to_file(fmt="json")
    reg2 = Registry()
    reg2.from_file(fname)
    assert reg == reg2


def test_subset(filled_reg):
    reg = filled_reg
    # all_cq4_eids = set(reg.CQUAD4.array['EID'])
    # exp = {1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25}
    # assert exp == all_cq4_eids
    cq4_sub = reg.CQUAD4.subset(eids=(1, 4, 25))
    assert isinstance(cq4_sub, CQUAD4)
    assert set(cq4_sub.array["EID"]) == {1, 4, 25}


@pytest.mark.xfail(reason="test is not up-to-date")
def test_meetic(filled_reg):
    reg = filled_reg
    # standard panel specs
    panels_specs = {
        "samepid": True,
        "pcard1": "PCOMP",
        "pcard2": "PCOMP",
        "anglemax": 30,
        "min_paths": 2,
    }
    m = reg.mesh.meetic(**panels_specs)
    print(m.to_csv())
    exp = """\
gid,pathid,eid1,eid2,card1,dim1,pid1,card2,dim2,pid2,same_card,same_pid,same_dim,pcard1,pcard2,same_pcard,angle
2,0,1,2,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
3,0,2,3,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
4,0,3,4,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
6,1,1,23,CQUAD4,2d,6,CTRIA3,2d,6,False,True,True,PCOMP,PCOMP,True,0.0
6,2,5,23,CTRIA3,2d,6,CTRIA3,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
7,0,1,2,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
7,3,1,23,CQUAD4,2d,6,CTRIA3,2d,6,False,True,True,PCOMP,PCOMP,True,0.0
7,4,2,6,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
7,7,6,22,CQUAD4,2d,6,CTRIA3,2d,6,False,True,True,PCOMP,PCOMP,True,0.0
7,9,22,23,CTRIA3,2d,6,CTRIA3,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
8,0,2,3,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
8,1,2,6,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
8,5,3,7,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
8,7,6,7,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
9,0,3,4,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
9,1,3,7,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
9,5,4,8,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
9,7,7,8,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
10,0,4,8,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
11,1,5,21,CTRIA3,2d,6,CTRIA3,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
12,3,6,22,CQUAD4,2d,6,CTRIA3,2d,6,False,True,True,PCOMP,PCOMP,True,0.0
12,5,9,10,CQUAD4,2d,7,CQUAD4,2d,7,True,True,True,PCOMP,PCOMP,True,0.0
12,12,21,22,CTRIA3,2d,6,CTRIA3,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
13,0,6,7,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
13,5,7,11,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
14,0,7,8,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
14,1,7,11,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
14,5,8,12,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
14,7,11,12,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
15,0,8,12,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
17,0,9,10,CQUAD4,2d,7,CQUAD4,2d,7,True,True,True,PCOMP,PCOMP,True,0.0
17,5,13,14,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
18,5,14,15,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
21,0,13,17,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
22,0,13,14,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
22,1,13,17,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
22,4,14,18,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
22,5,17,18,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
23,0,14,15,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
23,1,14,18,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
23,4,15,19,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
23,5,18,19,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
24,0,15,16,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
24,1,15,19,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
24,4,16,20,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
24,5,19,20,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
25,0,16,20,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
27,0,17,18,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
28,0,18,19,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
29,0,19,20,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
31,0,5,21,CTRIA3,2d,6,CTRIA3,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
31,2,5,23,CTRIA3,2d,6,CTRIA3,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
31,3,21,22,CTRIA3,2d,6,CTRIA3,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
31,5,22,23,CTRIA3,2d,6,CTRIA3,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
32,0,11,12,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
32,5,15,16,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
34,0,24,25,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
35,0,24,25,CQUAD4,2d,6,CQUAD4,2d,6,True,True,True,PCOMP,PCOMP,True,0.0
"""
    expected = df_from_csvstr(exp, index_col=[0, 1])
    m = m[[c for c in expected.columns]]
    expected.columns = m.columns
    assert len(m) == len(expected)
    errors = []
    # check by row...
    for i, row_m in m.iterrows():
        try:
            row_exp = expected.loc[i]
        except TypeError as exc:
            errors.append(i)
            continue
        try:
            assert row_exp.to_dict() == row_m.to_dict()
        except AssertionError:
            print(f"row #{i}")
            print(row_m)
            print("----")
            print(row_exp)
            raise
    if errors:
        print("errors: %s" % errors)
        assert 1 == 0


def test_ordered_eid2gids(filled_reg):

    reg = filled_reg
    e2g = reg.mesh.eid2gids(keep_order=True, eids=(1, 2, 23, 28))
    pp(e2g)
    exp = {1: [1, 6, 7, 2], 2: [2, 7, 8, 3], 23: [7, 6, 31], 28: [39, 10]}

    assert e2g == exp


def test_eid2gids(filled_reg):
    reg = filled_reg
    e2g = reg.mesh.eid2gids(eids=(1, 2, 23, 28))
    pp(e2g)
    exp = {1: {1, 6, 7, 2}, 2: {2, 7, 8, 3}, 23: {7, 6, 31}, 28: {39, 10}}
    assert e2g == exp


def test_to_vtk(filled_reg):
    reg = filled_reg
    _c = reg.mesh.eid2gids(keep_order=True)
    grid, gids_vtk2nas, eids_vtk2nas = reg.mesh.to_vtk(eids=(1, 2, 23, 28))
    # check if eid2gids still work
    _c2 = reg.mesh.eid2gids(keep_order=True)
    assert _c == _c2
    grid.save("panels.vtu")
    # try to load it
    import pyvista as pv

    g = pv.UnstructuredGrid("panels.vtu")
    os.remove("panels.vtu")
    pp(gids_vtk2nas)
    expected = {0: 1, 1: 2, 2: 3, 3: 6, 4: 7, 5: 8, 6: 10, 7: 31, 8: 39}
    assert gids_vtk2nas == expected


def test_normals(filled_reg):
    reg = filled_reg
    # mesh = Mesh()
    # mesh.set_registry(reg)
    normals = reg.mesh.normals(digits=3, eids=(1, 13, 28, 29))
    print(normals.to_csv())
    expected = """\
,X,Y,Z
1,-0.0,0.0,1.0
13,-0.5,0.0,0.866
28,0.0,0.0,-1.0
29,0.0,0.0,1.0"""

    expected = df_from_csvstr(expected)
    assert np.alltrue(normals == expected)


def test_area(filled_reg):
    reg = filled_reg
    areas = reg.mesh.area(eids=(1, 28, 13, 29))
    print(areas)
    assert np.allclose(
        areas["data"], np.array([0.75, np.nan, 1.0, np.nan]), equal_nan=True
    )


def test_thk(filled_reg):
    # Element 24 - LAMINATE PLATE    ( Quad, 4-noded )
    #  Property 6         Color 124    Layer 1         AttachTo 0
    # Element 27 - PLATE    ( Quad, 4-noded )
    #  Property 4         Color 124    Layer 1         AttachTo 0
    #  Plate Thickness     0.5           0.5           0.4           0.3
    # Element 35 - PLATE    ( Tri,  3-noded )
    #  Property 4         Color 124    Layer 1         AttachTo 0
    #  Plate Thickness     0.4           0.4           0.3
    # Element 36 - PLATE    ( Quad, 4-noded )
    #  Property 2         Color 124    Layer 1         AttachTo 0
    # Element 37 - PLATE    ( Tri,  3-noded )
    #  Property 2         Color 124    Layer 1         AttachTo 0
    # Element 33 - SPRING/DAMPER    ( Line, 2-noded )
    reg = filled_reg
    thks = reg.mesh.thk(eids=(24, 27, 4, 35, 36, 37, 33), asdict=False)
    exp = pd.Series(
        {
            24: 0.5,
            27: 0.425,
            4: 0.5,
            35: 0.3666666666666667,
            36: 0.5,
            37: 0.5,
            33: np.nan,
        }
    )
    np.testing.assert_allclose(exp.values, thks.values)
    np.testing.assert_array_equal(exp.index, thks.index)


def test_lengths(filled_reg):
    reg = filled_reg
    all_lengths = reg.mesh.length()
    # {
    #     'index': array([28, 29, 30, 31, 100, 200]),
    #     'data': array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5]),
    #     'name': 'length',
    # }
    np.alltrue(all_lengths["index"] == np.array([28, 29, 30, 31, 100, 200]))
    np.allclose(all_lengths["data"], np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5]))
    assert all_lengths["name"] == "length"
    # ------------------------------------------------------------------------
    # lengths by EIDS
    all_lengths = reg.mesh.length(eids=(100, 28))
    # {
    #     'index': array([28, 29, 30, 31, 100, 200]),
    #     'data': array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5]),
    #     'name': 'length',
    # }
    np.alltrue(all_lengths["index"] == np.array([100, 28]))
    np.allclose(all_lengths["data"], np.array([0.5, 0.5]))
    assert all_lengths["name"] == "length"
