#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low-Level Tests CBUSH card parser

    ref: NX Nastran 12 Quick Reference Guide 11-39 (p.1399)
"""

from pprint import pprint

import pytest

from nastranio.cards import CBUSH


@pytest.fixture
def parsed_bulk():
    cards = CBUSH()
    # fmt: off
    cards_bulk = [
        """\
     $▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
     CBUSH         39       6       1     100      75""",
        """\
     $ GB not specified
     CBUSH         40       6       1                                       0""",
        """\
     $ Coincident Grid Points (usually used in VIP FEM)
     CBUSH         41       6       1     100                               6""",
        """\
     $ NONCOINCIDENT GRID POINTS WITH FIELDS 6 THROUGH 9 BLANK AND
     $ A SPRING-DAMPER OFFSET.
     CBUSH         42       6       1     600                                +
     +           0.25      10      0.     10.     10.""",
    ]
    # fmt: on
    cards.parse(cards_bulk.pop(0))
    for card in cards_bulk:
        _ = CBUSH()
        _.parse(card)
        cards.merge(_)
    return cards


def test_to_nastran(parsed_bulk):
    """test to_nastran() method"""
    cards = parsed_bulk
    # # ========================================================================
    # # to_nastran
    # # ========================================================================
    nas = "\n".join(cards.to_nastran(ruler=True))
    print(nas)
    exp = """\
$CBUSH ▕    EID▕    PID▕     GA▕     GB▕  GO/X1▕     X2▕     X3▕    CID▕+      ▕
$+     ▕      S▕   OCID▕     S1▕     S2▕     S3▕       ▕       ▕       ▕       ▕
CBUSH         39       6       1     100      75
CBUSH         40       6       1                                       0
CBUSH         41       6       1     100                               6
CBUSH         42       6       1     600                                +
+            .25      10      0.     10.     10."""

    assert nas == exp


def test_export_data(parsed_bulk):
    cards = parsed_bulk
    # ========================================================================
    # test export_data() used for serialization
    # ========================================================================
    res = cards.export_data()
    pprint(res)

    exp = {
        "card": "CBUSH",
        "main": {
            "CID": [None, 0, 6, None],
            "EID": [39, 40, 41, 42],
            "GA": [1, 1, 1, 1],
            "GB": [100, None, 100, 600],
            "GO": [75, None, None, None],
            "GO/X1": [75, None, None, None],
            "OCID": [None, None, None, 10],
            "PID": [6, 6, 6, 6],
            "S": [None, None, None, 0.25],
            "S1": [None, None, None, 0.0],
            "S2": [None, None, None, 10.0],
            "S3": [None, None, None, 10.0],
            "X1": [None, None, None, None],
            "X2": [None, None, None, None],
            "X3": [None, None, None, None],
        },
    }

    assert res == exp


def test_to_eid2gids(parsed_bulk):
    """test eid2gids() dictionnary"""
    cards = parsed_bulk
    eid2gids = cards.eid2gids()
    pprint(eid2gids)
    exp = {39: {1, 100}, 40: {1, None}, 41: {1, 100}, 42: {600, 1}}
    assert eid2gids == exp
    eid2gids = cards.eid2gids(keep_order=True)
    pprint(eid2gids)
    exp = {39: [1, 100], 40: [1, None], 41: [1, 100], 42: [1, 600]}
    assert eid2gids == exp


def test_grinames(parsed_bulk):
    cards = parsed_bulk
    """ test gids_header() list
    """
    gridnames = cards.gids_header
    assert gridnames == ["GA", "GB"]
