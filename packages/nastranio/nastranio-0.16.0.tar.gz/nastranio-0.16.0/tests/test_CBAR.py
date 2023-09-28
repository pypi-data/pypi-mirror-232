#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low-Level Tests CBAR card parser

    ref: NX Nastran 12 Quick Reference Guide 11-20 (p.1380)
"""

from pprint import pprint

import pytest

from nastranio.cards import CBAR


@pytest.fixture
def parsed_bulk():
    cards = CBAR()
    # fmt: off
    cards_bulk = [
        """\
     $▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
     CBAR           2      39       7       3     0.6     18.     26.        +
     +                    513""",
        """\
     $ ALTERNATE FORMAT
     CBAR           3      39       7       6     10                         +
     +                    513"""
    ]
    # fmt: on
    cards.parse(cards_bulk.pop(0))
    for card in cards_bulk:
        _ = CBAR()
        _.parse(card)
        cards.merge(_)
    return cards


def test_export_data(parsed_bulk):
    cards = parsed_bulk
    # ========================================================================
    # test export_data() used for serialization
    # ========================================================================
    res = cards.export_data()
    pprint(res)

    exp = {
        "main": {
            "EID": [2, 3],
            "GO": [None, 10],
            "GO/X1": [0.6, 10],
            "GA": [7, 7],
            "GB": [3, 6],
            "PA": [None, None],
            "PB": [513, 513],
            "PID": [39, 39],
            "W1A": [None, None],
            "W1B": [None, None],
            "W2A": [None, None],
            "W2B": [None, None],
            "W3B": [None, None],
            "W3A": [None, None],
            "X1": [0.6, None],
            "X2": [18.0, None],
            "X3": [26.0, None],
        },
        "card": "CBAR",
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
$CBAR  ▕    EID▕    PID▕     GA▕     GB▕  GO/X1▕     X2▕     X3▕       ▕+      ▕
$+     ▕     PA▕     PB▕    W1A▕    W2A▕    W3A▕    W1B▕    W2B▕    W3B▕       ▕
CBAR           2      39       7       3      .6     18.     26.        +
+                    513
CBAR           3      39       7       6      10                        +
+                    513"""

    assert nas == exp


def test_to_eid2gids(parsed_bulk):
    """test eid2gids() dictionnary"""
    cards = parsed_bulk
    eid2gids = cards.eid2gids()
    exp = {2: {3, 7}, 3: {6, 7}}
    assert eid2gids == exp
    eid2gids = cards.eid2gids(keep_order=True)
    exp = {2: [7, 3], 3: [7, 6]}
    assert eid2gids == exp


def test_grinames(parsed_bulk):
    cards = parsed_bulk
    """ test gids_header() list
    """
    gridnames = cards.gids_header
    assert gridnames == ["GA", "GB"]
