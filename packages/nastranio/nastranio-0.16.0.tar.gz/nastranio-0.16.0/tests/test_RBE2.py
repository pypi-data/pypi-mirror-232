#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Low-Level Tests RBE2 card parser

    ref: NX Nastran 12 Quick Reference Guide 17-45 (p.2519)
"""

from io import StringIO
from pprint import pprint

import pytest

from nastranio.cards import RBE2
from nastranio.registry import Registry


@pytest.fixture
def parsed_bulk():
    txt = """
BEGIN BULK
$▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
RBE2           9       8      12      10      12      14      15      16+
+             20
RBE2       12154    5124  123456    6170      2.
 """
    fh = StringIO()
    fh.write(txt)
    fh.seek(0)
    reg = Registry()
    reg.from_bulkfile(fh, nbprocs=1, progress=False)
    bulk = reg.container["bulk"]["RBE2"]
    return bulk


def test_card_main(parsed_bulk):
    cards = parsed_bulk
    exp = {
        "ALPHA": [0.0, 2.0],
        "CM": [12, 123456],
        "EID": [9, 12154],
        "GN": [8, 5124],
        "rbe2_gidsetID": [0, 1],
    }
    actual = cards.carddata["main"]
    assert actual == exp


def test_export_data(parsed_bulk):
    cards = parsed_bulk
    res = cards.export_data()
    exp = {
        "main": {
            "ALPHA": [0.0, 2.0],
            "CM": [12, 123456],
            "EID": [9, 12154],
            "GN": [8, 5124],
            "rbe2_gidsetID": [0, 1],
        },
        "card": "RBE2",
        "rbe2_gidset": [
            [{"GM": 10}, {"GM": 12}, {"GM": 14}, {"GM": 15}, {"GM": 16}, {"GM": 20}],
            [{"GM": 6170}],
        ],
    }

    assert res == exp


def test_to_nastran(parsed_bulk):
    """test to_nastran() method"""
    cards = parsed_bulk
    nas = "\n".join(cards.to_nastran(ruler=True))
    expected = """\
$RBE2  ▕    EID▕     GN▕     CM▕    GM1▕    GM2▕    GM3▕    GM4▕    GM5▕+      ▕
$+     ▕    GM6▕    GM7▕    GM8▕ -etc.-▕  ALPHA▕       ▕       ▕       ▕       ▕
RBE2           9       8      12      10      12      14      15      16+
+             20      0.
RBE2       12154    5124  123456    6170      2."""

    print(nas)
    assert nas == expected


def test_to_nastran_nodefault(parsed_bulk):
    """test to_nastran() method without expliciting default values"""
    cards = parsed_bulk
    nas = "\n".join(cards.to_nastran(ruler=True, with_default=False))
    expected = """\
$RBE2  ▕    EID▕     GN▕     CM▕    GM1▕    GM2▕    GM3▕    GM4▕    GM5▕+      ▕
$+     ▕    GM6▕    GM7▕    GM8▕ -etc.-▕  ALPHA▕       ▕       ▕       ▕       ▕
RBE2           9       8      12      10      12      14      15      16+
+             20
RBE2       12154    5124  123456    6170      2."""

    print(nas)
    assert nas == expected


def test_eid2gids(parsed_bulk):
    """test eid2gids() dictionnary"""
    cards = parsed_bulk
    eid2gids = cards.eid2gids()
    exp = {9: {16, 20, 8, 10, 12, 14, 15}, 12154: {6170, 5124}}
    assert eid2gids == exp
    eid2gids = cards.eid2gids(keep_order=True)
    pprint(eid2gids)
    exp = {9: [8, 10, 12, 14, 15, 16, 20], 12154: [5124, 6170]}
    assert eid2gids == exp


def test_grinames(parsed_bulk):
    cards = parsed_bulk
    """ test gids_header() list
    """
    gridnames = cards.gids_header
    assert gridnames == ["GN"]
