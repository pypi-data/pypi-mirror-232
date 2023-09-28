#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests PCOMP card parser"""

from pprint import pprint

import numpy as np

from nastranio.cards import PCOMP


def test_one_pcomp():
    bulk1 = """\
PCOMP          4         .017505                              0.        +
+              2 .023622      0.     YES       3 .452756      0.     YES+
+              2 .023622      0.     YES"""
    cards = PCOMP()
    cards.parse(bulk1)
    # ========================================================================
    # test basic data
    # ========================================================================
    exp = {
        "FT": [None],
        "GE": [0.0],
        "LAM": [None],
        "NSM": [0.017505],
        "PID": [4],
        "SB": [None],
        "TREF": [None],
        "Z0": [None],
        "pcomp_layupID": [0],
    }

    assert cards.carddata["main"] == exp
    # ========================================================================
    # test `merge` method
    # ========================================================================
    assert len(cards) == 1
    cards2 = PCOMP()
    bulk2 = """\
PCOMP          5         .016245                              0.        +
+              2    .018      0.     YES       4    .339      0.     YES+
+              2    .018      0.     YES"""
    cards2.parse(bulk2)
    cards.merge(cards2)
    exp = {
        "FT": [None, None],
        "GE": [0.0, 0.0],
        "LAM": [None, None],
        "NSM": [0.017505, 0.016245],
        "PID": [4, 5],
        "SB": [None, None],
        "TREF": [None, None],
        "Z0": [None, None],
        "pcomp_layupID": [0, 1],
    }
    pprint(cards.carddata["main"])

    assert cards.carddata["main"] == exp
    # ========================================================================
    # test export_data() used for serialization
    # ========================================================================
    res = cards.export_data()
    exp = {
        "card": "PCOMP",
        "main": {
            "FT": [None, None],
            "GE": [0.0, 0.0],
            "LAM": [None, None],
            "NSM": [0.017505, 0.016245],
            "PID": [4, 5],
            "SB": [None, None],
            "TREF": [None, None],
            "Z0": [None, None],
            "pcomp_layupID": [0, 1],
        },
        "pcomp_layup": [
            [
                {"MID": 2, "SOUT": "YES", "T": 0.023622, "THETA": 0.0},
                {"MID": 3, "SOUT": "YES", "T": 0.452756, "THETA": 0.0},
                {"MID": 2, "SOUT": "YES", "T": 0.023622, "THETA": 0.0},
            ],
            [
                {"MID": 2, "SOUT": "YES", "T": 0.018, "THETA": 0.0},
                {"MID": 4, "SOUT": "YES", "T": 0.339, "THETA": 0.0},
                {"MID": 2, "SOUT": "YES", "T": 0.018, "THETA": 0.0},
            ],
        ],
    }

    assert res == exp
    # ========================================================================
    # to_nastran
    # ========================================================================
    nas = "\n".join(cards.to_nastran(ruler=True))
    print(80 * "*")
    print("actual:")
    print(nas)
    print(80 * "-")
    print("expected:")
    expected = bulk1 + "\n" + bulk2
    print(expected)
    # test that nastran's output match previous input
    nas = "\n".join(cards.to_nastran(ruler=False))
    assert nas == expected
    # test ruler fields
    expected = """\
$PCOMP ▕    PID▕     Z0▕    NSM▕     SB▕     FT▕   TREF▕     GE▕    LAM▕+      ▕
$+     ▕   MID1▕     T1▕ THETA1▕  SOUT1▕   MID2▕     T2▕ THETA2▕  SOUT2▕+      ▕
$+     ▕   MID3▕     T3▕ THETA3▕  SOUT3▕ -etc.-▕       ▕       ▕       ▕       ▕
PCOMP          4         .017505                              0.        +
+              2 .023622      0.     YES       3 .452756      0.     YES+
+              2 .023622      0.     YES
PCOMP          5         .016245                              0.        +
+              2    .018      0.     YES       4    .339      0.     YES+
+              2    .018      0.     YES"""
    nas = "\n".join(cards.to_nastran(ruler=True))
    assert nas == expected

    # ========================================================================
    # thicknesses
    # ========================================================================
    thk = cards.thk
    print(thk["data"])
    np.testing.assert_allclose(thk["data"], np.array([0.5, 0.375]))
    print(thk["index"])
    np.testing.assert_allclose(thk["index"], np.array([4, 5]))
    assert thk["name"] == "pid2thk"
