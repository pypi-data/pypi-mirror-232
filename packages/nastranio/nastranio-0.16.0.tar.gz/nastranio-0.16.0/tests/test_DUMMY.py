#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low-Level Tests CBAR card parser

    ref: NX Nastran 12 Quick Reference Guide 11-20 (p.1380)
"""

from io import StringIO
from pprint import pprint

import pytest

from nastranio.registry import Registry


@pytest.fixture
def parsed_bulk():
    txt = """
BEGIN BULK
$▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
DUMMY          2      39       7       3     0.6     18.     26.        +
+                    513
DUMMY          3      42     7.5              10                        +
+                    513                       9
"""
    fh = StringIO()
    fh.write(txt)
    fh.seek(0)
    reg = Registry()
    reg.from_bulkfile(fh, nbprocs=1, progress=False)
    bulk = reg.container["bulk"]["DUMMY"]
    return bulk


def test_export_data(parsed_bulk):
    bulk = parsed_bulk
    # ========================================================================
    # test export_data() used for serialization
    # ========================================================================
    res = bulk.export_data()
    exp = {
        "card": "DUMMY",
        "main": {
            "field#0": ["", ""],
            "field#1": ["", ""],
            "field#10": ["+", "+"],
            "field#11": ["+", "+"],
            "field#12": [None, None],
            "field#13": [513, 513],
            "field#14": [None, None],
            "field#15": [None, None],
            "field#16": [None, 9],
            "field#2": [2, 3],
            "field#3": [39, 42],
            "field#4": [7, 7.5],
            "field#5": [3, None],
            "field#6": [0.6, 10],
            "field#7": [18.0, None],
            "field#8": [26.0, None],
            "field#9": [None, None],
        },
    }

    assert res == exp
    assert bulk.fields == {
        2: "field#2",
        3: "field#3",
        4: "field#4",
        5: "field#5",
        6: "field#6",
        7: "field#7",
        8: "field#8",
        9: "field#9",
        12: "field#12",
        13: "field#13",
        14: "field#14",
        15: "field#15",
        16: "field#16",
    }


def test_to_nastran(parsed_bulk):
    """test to_nastran() method"""
    bulk = parsed_bulk
    # ========================================================================
    # to_nastran
    # ========================================================================
    nas = "\n".join(bulk.to_nastran(ruler=False))
    print(nas)
    exp = """\
DUMMY          2      39       7       3      .6     18.     26.        +
+                    513
DUMMY          3      42     7.5              10                        +
+                    513                       9"""

    assert nas == exp
