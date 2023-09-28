"""
test nastranio.writers.gmsh.Study

Read a gmsh mesh file
"""
from pathlib import Path

import pytest

from nastranio.readers.gmsh.study import Study
from nastranio.registry import Registry


@pytest.fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = Path(request.module.__file__)
    return filename.parent / "test_study"


def test_study(datadir, tmpdir):
    """if <meshfilename>.params.json exists next to <meshfilename>, parameters
    are retrived from it.
    This test check that "tapered.params.json" is correctly retrieved.
    """
    study = Study(datadir / "tapered.msh")
    study.build()
    bulk = study.to_nastran(Path(tmpdir) / "tapered.nas")
    assert bulk.exists()


def test_study_providing_params(datadir, tmpdir):
    """
    check Study import with explicit parameters file provided.
    """
    study = Study(datadir / "tapered.msh")
    study.load_user_params_from_file(datadir / "tapered.params.json")
    study.build()
    bulk = study.to_nastran(Path(tmpdir) / "tapered.nas")
    assert bulk.exists()
    # read newly created nastran bulk file
    _reg = Registry()
    _reg.from_bulkfile(bulk, nbprocs=8, progress=False)
    bulk = _reg.to_nastran(Path(tmpdir) / "tapered2.nas")
