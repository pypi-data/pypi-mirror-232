#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests nastranio.Registry"""

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
    bulkpath = os.path.join(datadir, "nightstand.dat")
    _reg = Registry()
    _reg.from_bulkfile(bulkpath, nbprocs=8, progress=False)
    return _reg


def test_coords_as_defined_by_gids(filled_reg):
    reg = filled_reg
    # mesh = Mesh()
    # mesh.set_registry(reg)
    # ------------------------------------------------------------------------
    # as numpy data
    #     ID    Def CS      X1           X2           X3
    # _______________________________________________________
    #       1       11   19.00522    -47.01603     15.80569
    #      13        0    375.331     -47.3115      14.6654
    gids, coords, csys = reg.mesh.coords(gids=(1, 13))
    expected_gids = np.array([1, 13])
    expected_coords = np.array(
        [[374.79303586, -47.79179422, 14.66539227], [375.331, -47.3115, 14.6654]]
    )
    expected_csys = np.array([0, 0])
    assert np.alltrue(gids == expected_gids)
    assert np.allclose(coords, expected_coords)
    assert np.alltrue(csys == expected_csys)
    # ------------------------------------------------------------------------
    # as pandas DataFrame
    coords = reg.mesh.coords(gids=(1, 13), asdf=True)
    expected_csv = """\
gid,csys,X,Y,Z
1,0,374.79303585921286,-47.79179421589026,14.665392265440204
13,0,375.331,-47.3115,14.6654
"""
    expected = df_from_csvstr(expected_csv)
    print(coords)
    print(expected)
    assert np.allclose(coords, expected)


def test_coords_by_gids(filled_reg):
    reg = filled_reg
    # mesh = Mesh()
    # mesh.set_registry(reg)
    # ------------------------------------------------------------------------
    # as numpy data
    #     ID    Def CS          X1           X2           X3
    # ___________________   Listing in Coordinate System    0   --------
    #       1       11        374.793     -47.7918      14.6654
    #      13        0        375.331     -47.3115      14.6654
    gids, coords, csys = reg.mesh.coords(gids=(1, 13), incsys=0)
    expected_gids = np.array([1, 13])
    expected_coords = np.array(
        [[374.793, -47.7918, 14.6654], [375.331, -47.3115, 14.6654]]
    )
    expected_csys = np.array([0, 0])
    print(gids)
    assert np.allclose(gids, expected_gids)
    print(csys)
    assert np.allclose(csys, expected_csys)
    print(coords)
    assert np.allclose(coords, expected_coords)
    # ------------------------------------------------------------------------
    # as pandas DataFrame
    coords = reg.mesh.coords(gids=(1, 13), asdf=True)
    expected_csv = """\
gid,csys,X,Y,Z
1,0,374.79303585921286,-47.79179421589026,14.665392265440204
13,0,375.331,-47.3115,14.6654"""
    expected = df_from_csvstr(expected_csv)
    print(coords)
    print(expected)
    assert np.allclose(coords, expected)
    # ------------------------------------------------------------------------
    # as pandas DataFrame in ginven CSYS
    coords = reg.mesh.coords(gids=(1, 13), asdf=True, incsys=0)
    expected_csv = """\
gid,csys,X,Y,Z
1,0,374.793,-47.7918,14.6654
13,0,375.331,-47.3115,14.6654"""
    expected = df_from_csvstr(expected_csv)
    print("GOT:")
    print("----")
    print(coords)
    print("EXPECTING:")
    print("----------")
    print(expected)
    assert np.allclose(coords, expected)


def test_coords_as_defined_by_eids(filled_reg):
    reg = filled_reg
    # ------------------------------------------------------------------------
    # searching by eids
    gids, coords, csys = reg.mesh.coords(eids=(1, 8))
    print("coords:", coords)
    print("gids:", gids)
    print("csys:", csys)
    expected_coords = np.array(
        [
            [374.79303586, -47.79179422, 14.66539227],
            [375.856, -47.402, 14.6654],
            [374.793, -47.3784, 14.6654],
            [375.686, -47.6245, 14.6654],
            [375.331, -47.3115, 14.6654],
            [375.216, -47.5571, 14.6654],
        ]
    )
    expected_gids = np.array([1, 5, 8, 12, 13, 15])
    expected_csys = np.array([0, 0, 0, 0, 0, 0])
    assert np.allclose(coords, expected_coords)
    assert np.alltrue(gids == expected_gids)
    assert np.alltrue(csys == expected_csys)
    # ------------------------------------------------------------------------
    # as pandas DataFrame
    coords = reg.mesh.coords(eids=(1, 8), asdf=True)
    expected_csv = """\
gid,csys,X,Y,Z
1,0,374.79303585921286,-47.79179421589026,14.665392265440204
5,0,375.856,-47.402,14.6654
8,0,374.793,-47.3784,14.6654
12,0,375.686,-47.6245,14.6654
13,0,375.331,-47.3115,14.6654
15,0,375.216,-47.5571,14.6654"""
    expected = df_from_csvstr(expected_csv)
    print(coords)
    print(coords.to_csv())
    print(expected)
    assert np.allclose(coords, expected)


def test_boundaries(filled_reg):
    boundaries = filled_reg.mesh.boundaries
    assert boundaries.T.to_dict() == {
        12508: {"dof": 123, "sid": 290, "source": "SPC1"},
        12509: {"dof": 123, "sid": 290, "source": "SPC1"},
        12510: {"dof": 123, "sid": 290, "source": "SPC1"},
        12511: {"dof": 123, "sid": 290, "source": "SPC1"},
        12516: {"dof": 123456, "sid": -1, "source": "GRID"},
        12517: {"dof": 123456, "sid": -1, "source": "GRID"},
    }


def test_loading(filled_reg):
    loads = filled_reg.mesh.load_combination
    assert loads is None


def test_to_gmsh(filled_reg):
    txt = filled_reg.mesh.to_gmsh()


def test_to_nastran(filled_reg):
    txt = filled_reg.to_nastran()
