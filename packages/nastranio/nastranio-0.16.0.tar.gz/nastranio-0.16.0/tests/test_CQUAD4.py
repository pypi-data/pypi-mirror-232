#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low-Level Tests CQUAD4 card parser

    ref: NX Nastran 12 Quick Reference Guide 12-80 (p.1564)
"""

from pprint import pprint

import numpy as np
import pytest

from nastranio.cards import CQUAD4


@pytest.fixture
def parsed_bulk():
    cards = CQUAD4()
    # fmt: off
    cards_bulk = [
        """\
     $▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
     CQUAD4       111     203      31      74      75      32     2.6     0.3+
     +                      1    1.77    2.04    2.09    1.80""",
    "CQUAD4         1       1       5      12      15      13",
    "CQUAD4         2       1       5      12      15      13       2",
    ]
    # fmt: on
    cards.parse(cards_bulk.pop(0))
    for card in cards_bulk:
        _ = CQUAD4()
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
        "G4": [32, 13, 13],
        "MCID": [None, None, 2],
        "PID": [203, 1, 1],
        "T1": [1.77, None, None],
        "T2": [2.04, None, None],
        "T3": [2.09, None, None],
        "T4": [1.8, None, None],
        "TFLAG": [1, None, None],
        "THETA": [2.6, 0.0, None],
        "THETA/MCID": [2.6, 0.0, 2],
        "ZOFFS": [0.3, None, None],
    }
    actual = cards.carddata["main"]
    assert len(cards) == 3
    assert actual == exp


def test_export_data(parsed_bulk):
    cards = parsed_bulk
    # ========================================================================
    # test export_data() used for serialization
    # ========================================================================
    res = cards.export_data()
    pprint(res)
    exp = {
        "main": {
            "EID": [111, 1, 2],
            "G1": [31, 5, 5],
            "G2": [74, 12, 12],
            "G3": [75, 15, 15],
            "G4": [32, 13, 13],
            "MCID": [None, None, 2],
            "PID": [203, 1, 1],
            "T1": [1.77, None, None],
            "T2": [2.04, None, None],
            "T3": [2.09, None, None],
            "T4": [1.8, None, None],
            "TFLAG": [1, None, None],
            "THETA": [2.6, 0.0, None],
            "THETA/MCID": [2.6, 0.0, 2],
            "ZOFFS": [0.3, None, None],
        },
        "card": "CQUAD4",
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
$CQUAD4▕    EID▕    PID▕     G1▕     G2▕     G3▕     G4▕THETA..▕  ZOFFS▕+      ▕
$+     ▕       ▕  TFLAG▕     T1▕     T2▕     T3▕     T4▕       ▕       ▕       ▕
CQUAD4       111     203      31      74      75      32     2.6      .3+
+                      1    1.77    2.04    2.09     1.8
CQUAD4         1       1       5      12      15      13      0.
CQUAD4         2       1       5      12      15      13       2"""

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
$CQUAD4▕    EID▕    PID▕     G1▕     G2▕     G3▕     G4▕THETA..▕  ZOFFS▕+      ▕
$+     ▕       ▕  TFLAG▕     T1▕     T2▕     T3▕     T4▕       ▕       ▕       ▕
CQUAD4       111     203      31      74      75      32     2.6      .3+
+                      1    1.77    2.04    2.09     1.8
CQUAD4         1       1       5      12      15      13
CQUAD4         2       1       5      12      15      13       2"""

    assert nas == exp


def test_to_eid2gids(parsed_bulk):
    """test eid2gids() dictionnary"""
    cards = parsed_bulk
    eid2gids = cards.eid2gids()
    exp = {1: {13, 12, 5, 15}, 2: {13, 12, 5, 15}, 111: {32, 74, 75, 31}}
    assert eid2gids == exp
    eid2gids = cards.eid2gids(keep_order=True)
    exp = {1: [5, 12, 15, 13], 2: [5, 12, 15, 13], 111: [31, 74, 75, 32]}
    assert eid2gids == exp


def test_grinames(parsed_bulk):
    cards = parsed_bulk
    """ test gids_header() list
    """
    gridnames = cards.gids_header
    assert gridnames == ["G1", "G2", "G3", "G4"]


# def test_json(parsed_bulk):
#     cards = parsed_bulk
#     cards2 = CQUAD4()
#     cards2.from_json(cards.to_json())
#     assert cards2 == cards


def test_msgpack(parsed_bulk):
    cards = parsed_bulk
    cards2 = CQUAD4()
    cards2.from_msgpack(cards.to_msgpack())
    assert cards2 == cards


def test_thk(parsed_bulk):
    cards = parsed_bulk
    thks = cards.thk
    import pprint

    pprint.pprint(thks)  # TODO: remove me!
    np.testing.assert_array_equal(thks["data"], np.array([1.925, np.nan, np.nan]))
    np.testing.assert_array_equal(thks["index"], np.array([111, 1, 2]))
    assert thks["name"] == "thk"
