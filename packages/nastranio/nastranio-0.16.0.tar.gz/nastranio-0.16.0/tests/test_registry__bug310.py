import os
from distutils import dir_util

import pytest

from nastranio.registry import Registry


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
    bulkpath = os.path.join(datadir, "bug310.nas")
    _reg = Registry()
    _reg.from_bulkfile(bulkpath, nbprocs=8, progress=False)
    return _reg


def test_coords_as_defined_by_gids(datadir):
    bulkpath = os.path.join(datadir, "bug310.nas")
    reg1 = Registry()
    reg1.from_bulkfile(bulkpath, nbprocs=1, progress=False)
    elapsed = {1: reg1.container["meta"]["elapsed"]}
    for nbprocs in (2, 3, 4, 5):
        regi = Registry()
        regi.from_bulkfile(bulkpath, nbprocs=nbprocs, progress=False)
        diff = reg1.diff(regi)["values_changed"]
        assert "root['meta']['nbprocs']" in set(diff.keys())
        assert reg1 == regi
        elapsed[nbprocs] = regi.container["meta"]["elapsed"]
