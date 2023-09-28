#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low-Level Tests CTRIA3 card parser

    ref: NX Nastran 12 Quick Reference Guide 12-147 (p.1631)
"""

from pprint import pprint

import numpy as np
import pytest

from nastranio.cards import CTRIA3


@pytest.fixture
def parsed_bulk():
    cards = CTRIA3()
    # fmt: off
    cards_bulk = [
        """\
     $▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
     CTRIA3       111     203      31      74      75            0.98        +
     +                           1.77    20.4    2.09""",
    "CTRIA3         1       1       5      12      15     1.2",
    "CTRIA3         2       1       5      12      15       2",
    ]
    # fmt: on
    cards.parse(cards_bulk.pop(0))
    for card in cards_bulk:
        _ = CTRIA3()
        _.parse(card)
        cards.merge(_)
    return cards


def test_card_main(parsed_bulk):
    cards = parsed_bulk
    exp = {
        "EID": [111, 1, 2],
        "G1": [31, 5, 5],
        "G2": [74, 12, 12],
        "G3": [75, 15, 15],
        "MCID": [None, None, 2],
        "PID": [203, 1, 1],
        "T1": [1.77, None, None],
        "T2": [20.4, None, None],
        "T3": [2.09, None, None],
        "TFLAG": [None, None, None],
        "THETA": [0.0, 1.2, None],
        "THETA/MCID": [0.0, 1.2, 2],
        "ZOFFS": [0.98, None, None],
    }
    actual = cards.carddata["main"]
    pprint(actual)
    assert len(cards) == 3
    assert actual == exp


def test_export_data(parsed_bulk):
    cards = parsed_bulk
    # ========================================================================
    # test export_data() used for serialization
    # ========================================================================
    res = cards.export_data()
    exp = {
        "main": {
            "EID": [111, 1, 2],
            "G1": [31, 5, 5],
            "G2": [74, 12, 12],
            "G3": [75, 15, 15],
            "MCID": [None, None, 2],
            "PID": [203, 1, 1],
            "T1": [1.77, None, None],
            "T2": [20.4, None, None],
            "T3": [2.09, None, None],
            "TFLAG": [None, None, None],
            "THETA": [0.0, 1.2, None],
            "THETA/MCID": [0.0, 1.2, 2],
            "ZOFFS": [0.98, None, None],
        },
        "card": "CTRIA3",
    }

    assert res == exp


def test_to_nastran(parsed_bulk):
    """test to_nastran() method"""
    cards = parsed_bulk
    # # ========================================================================
    # # to_nastran
    # # ========================================================================
    nas = "\n".join(cards.to_nastran(ruler=True))
    print(nas)
    exp = """\
$CTRIA3▕    EID▕    PID▕     G1▕     G2▕     G3▕THETA..▕  ZOFFS▕       ▕+      ▕
$+     ▕       ▕  TFLAG▕     T1▕     T2▕     T3▕       ▕       ▕       ▕       ▕
CTRIA3       111     203      31      74      75      0.     .98        +
+                           1.77    20.4    2.09
CTRIA3         1       1       5      12      15     1.2
CTRIA3         2       1       5      12      15       2"""
    assert nas == exp


def test_to_nastran_nodefault(parsed_bulk):
    """test to_nastran() method without expliciting default values"""
    cards = parsed_bulk
    # # ========================================================================
    # # to_nastran
    # # ========================================================================
    nas = "\n".join(cards.to_nastran(ruler=True, with_default=False))
    print(nas)
    exp = """\
$CTRIA3▕    EID▕    PID▕     G1▕     G2▕     G3▕THETA..▕  ZOFFS▕       ▕+      ▕
$+     ▕       ▕  TFLAG▕     T1▕     T2▕     T3▕       ▕       ▕       ▕       ▕
CTRIA3       111     203      31      74      75             .98        +
+                           1.77    20.4    2.09
CTRIA3         1       1       5      12      15     1.2
CTRIA3         2       1       5      12      15       2"""
    assert nas == exp


def test_to_eid2gids(parsed_bulk):
    """test eid2gids() dictionnary"""
    cards = parsed_bulk
    eid2gids = cards.eid2gids()
    exp = {1: {12, 5, 15}, 2: {12, 5, 15}, 111: {74, 75, 31}}
    assert eid2gids == exp
    eid2gids = cards.eid2gids(keep_order=True)
    pprint(eid2gids)
    exp = {1: [5, 12, 15], 2: [5, 12, 15], 111: [31, 74, 75]}
    assert eid2gids == exp


def test_grinames(parsed_bulk):
    cards = parsed_bulk
    """ test gids_header() list
    """
    gridnames = cards.gids_header
    assert gridnames == ["G1", "G2", "G3"]


def test_thk(parsed_bulk):
    cards = parsed_bulk
    thks = cards.thk
    import pprint

    pprint.pprint(thks)  # TODO: remove me!
    np.testing.assert_allclose(thks["data"], np.array([8.08666667, np.nan, np.nan]))
    np.testing.assert_array_equal(thks["index"], np.array([111, 1, 2]))
    assert thks["name"] == "thk"
