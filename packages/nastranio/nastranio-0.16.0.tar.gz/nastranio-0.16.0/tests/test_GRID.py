#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low-Level Tests GRID card parser

    ref: NX Nastran 12 Quick Reference Guide 14-60 (p.1926)
"""

from io import StringIO
from pprint import pprint

import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal

from nastranio.cards import GRID

from .test_utils import df_from_csvstr


@pytest.fixture
def parsed_bulk():
    cards = GRID()
    # fmt: off
    cards_bulk = [
        """\
     $▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
     GRID           1       0 374.793-47.7918 14.6654       0""",
    "GRID           2       0 374.793 -46.965 14.6654       0     123       2"
    ]
    # fmt: on
    cards.parse(cards_bulk.pop(0))
    for card in cards_bulk:
        _ = GRID()
        _.parse(card)
        cards.merge(_)
    return cards


def test_card_main(parsed_bulk):
    cards = parsed_bulk
    exp = {
        "ID": [1, 2],
        "CP": [0, 0],
        "X1": [374.793, 374.793],
        "X2": [-47.7918, -46.965],
        "X3": [14.6654, 14.6654],
        "CD": [0, 0],
        "PS": [None, 123],
        "SEID": [None, 2],
    }
    assert cards.carddata["main"] == exp


def test_export_data(parsed_bulk):
    cards = parsed_bulk
    # ========================================================================
    # test export_data() used for serialization
    # ========================================================================
    res = cards.export_data()
    exp = {
        "main": {
            "ID": [1, 2],
            "CP": [0, 0],
            "X1": [374.793, 374.793],
            "X2": [-47.7918, -46.965],
            "X3": [14.6654, 14.6654],
            "CD": [0, 0],
            "PS": [None, 123],
            "SEID": [None, 2],
        },
        "card": "GRID",
    }
    assert res == exp


def test_to_nastran(parsed_bulk):
    """test to_nastran() method"""
    cards = parsed_bulk
    # test that nastran's output match previous input
    nas = "\n".join(cards.to_nastran(ruler=False))
    expected = """\
$GRID  ▕     ID▕     CP▕     X1▕     X2▕     X3▕     CD▕     PS▕   SEID▕       ▕
GRID           1       0 374.793-47.7918 14.6654       0
GRID           2       0 374.793 -46.965 14.6654       0     123       2"""
    nas = "\n".join(cards.to_nastran(ruler=True))
    assert nas == expected


def test_coords(parsed_bulk):
    cards = parsed_bulk
    gids, coords, csys = cards.coords()
    pprint(gids)
    pprint(coords)
    assert np.alltrue(gids == np.array([1, 2]))
    assert np.alltrue(
        coords == np.array([[374.793, -47.7918, 14.6654], [374.793, -46.965, 14.6654]])
    )


def test_coords_dataframe(parsed_bulk):
    cards = parsed_bulk
    coords = cards.coords(asdf=True)
    exp = "gid,csys,X,Y,Z\n1,0,374.793,-47.7918,14.6654\n2,0,374.793,-46.965,14.6654\n"
    expected = df_from_csvstr(exp)
    pprint(coords)
    pprint(expected)
    assert isinstance(coords, pd.DataFrame)
    assert_frame_equal(coords, expected)


def test_selected_coords(parsed_bulk):
    cards = parsed_bulk
    gids, coords, csys = cards.coords(gids=[-1, 2])
    pprint(gids)
    pprint(coords)
    assert np.alltrue(gids == np.array([2]))
    assert np.alltrue(coords == np.array([[374.793, -46.965, 14.6654]]))


# def test_json(parsed_bulk):
#     cards = parsed_bulk
#     cards2 = GRID()
#     cards2.from_json(cards.to_json())
#     assert cards2 == cards


def test_msgpack(parsed_bulk):
    cards = parsed_bulk
    arr = cards.array
    cards2 = GRID()
    cards2.from_msgpack(cards.to_msgpack())
    assert cards2 == cards
