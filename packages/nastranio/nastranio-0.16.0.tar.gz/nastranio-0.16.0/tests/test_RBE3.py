#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Low-Level Tests RBE3 card parser

    ref: NX Nastran 12 Quick Reference Guide 17-48 (p.2522)
"""

from pprint import pprint

import pytest

from nastranio.cards import RBE3


@pytest.fixture
def parsed_bulk():
    cards = RBE3()
    # fmt: off
    cards_bulk = [
        """\
     $▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
     RBE3          14             100    1234     1.0     123       1       3+
     +              5     4.7       1       2       4       6     5.2       2+
     +              7       8       9     5.1       1      15      16        +
     +             UM     100      14       5       3       7       2        +
     +          ALPHA 17.3E-6""",
        """\
     RBE3       12986           12515  123456      1.      23    3919    3920+
     +           3921    3922    3923    3924    6482    6483    6484    6485+
     +             1.     123    5852      1.      23    4184    4185    4186+
     +           4187    4188    4189""",
        """\
     RBE3          13             102     456      1.      23    3919    3920+
     +           3921    3922    3923    3924    6482    6483    6484    6485+
     +             UM     102       1      23      23    3919    1234""",
    "RBE3          16               2       6      1.      23      17"
    ]
    # fmt: on
    cards.parse(cards_bulk.pop(0))
    for card in cards_bulk:
        _ = RBE3()
        _.parse(card)
        cards.merge(_)
    return cards


def test_export_data(parsed_bulk):
    cards = parsed_bulk
    res = cards.export_data()
    pprint(res)
    exp = {
        "main": {
            "ALPHA": [1.73e-05, 0.0, 0.0, 0.0],
            "EID": [14, 12986, 13, 16],
            "REFC": [1234, 123456, 456, 6],
            "REFGRID": [100, 12515, 102, 2],
            "rbe3_umID": [0, 1, 2, 1],
            "rbe3_wcgID": [0, 1, 2, 3],
        },
        "card": "RBE3",
        "rbe3_um": [
            [[100, 14], [5, 3], [7, 2]],
            [],
            [[102, 1], [23, 23], [3919, 1234]],
        ],
        "rbe3_wcg": [
            [
                {"C": 123, "Gi": {1, 3, 5}, "W": 1.0},
                {"C": 1, "Gi": {2, 4, 6}, "W": 4.7},
                {"C": 2, "Gi": {8, 9, 7}, "W": 5.2},
                {"C": 1, "Gi": {16, 15}, "W": 5.1},
            ],
            [
                {
                    "C": 23,
                    "Gi": {3919, 3920, 3921, 3922, 3923, 3924, 6482, 6483, 6484, 6485},
                    "W": 1.0,
                },
                {"C": 123, "Gi": {5852}, "W": 1.0},
                {"C": 23, "Gi": {4184, 4185, 4186, 4187, 4188, 4189}, "W": 1.0},
            ],
            [
                {
                    "C": 23,
                    "Gi": {3919, 3920, 3921, 3922, 3923, 3924, 6482, 6483, 6484, 6485},
                    "W": 1.0,
                }
            ],
            [{"C": 23, "Gi": {17}, "W": 1.0}],
        ],
    }

    assert res == exp


# def test_to_nastran(parsed_bulk):
#     """ test to_nastran() method """
#     cards = parsed_bulk
#     nas = '\n'.join(cards.to_nastran(ruler=True))
#     expected = """\
# $RBE3  ▕    EID▕     GN▕     CM▕    GM1▕    GM2▕    GM3▕    GM4▕    GM5▕+      ▕
# $+     ▕    GM6▕    GM7▕    GM8▕ -etc.-▕  ALPHA▕       ▕       ▕       ▕       ▕
# RBE3           9       8      12      10      12      14      15      16+
# +             20      0.
# RBE3       12154    5124  123456    6170      2."""

#     print(nas)
#     assert nas == expected


def test_eid2gids(parsed_bulk):
    """test eid2gids() dictionnary"""
    cards = parsed_bulk
    eid2gids = cards.eid2gids()
    exp = {
        # 13: OK
        13: {102, 3919, 3920, 3921, 3922, 3923, 3924, 6482, 6483, 6484, 6485},
        # 14: OK
        14: {1, 2, 3, 100, 4, 5, 6, 7, 8, 9, 15, 16},
        # 16: OK
        16: {2, 17},
        # 12986: OK
        12986: {
            3919,
            3920,
            3921,
            3922,
            3923,
            3924,
            4184,
            4185,
            4186,
            4187,
            4188,
            4189,
            5852,
            6482,
            6483,
            6484,
            6485,
            12515,
        },
    }
    assert eid2gids == exp
    eid2gids = cards.eid2gids(keep_order=True)
    pprint(eid2gids)
    exp = {
        13: [102, 3919, 3920, 3921, 3922, 3923, 3924, 6482, 6483, 6484, 6485],
        14: [100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16],
        16: [2, 17],
        12986: [
            12515,
            4189,
            4187,
            3919,
            3920,
            3921,
            3922,
            3923,
            3924,
            6482,
            6483,
            6484,
            6485,
            4185,
            4186,
            4184,
            5852,
            4188,
        ],
    }
    assert eid2gids == exp


def test_grinames(parsed_bulk):
    cards = parsed_bulk
    """ test gids_header() list
    """
    gridnames = cards.gids_header
    assert gridnames == ["REFGRID"]
