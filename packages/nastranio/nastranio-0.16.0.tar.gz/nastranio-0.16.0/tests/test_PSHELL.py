#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests PSHELL card parser"""

from pprint import pprint

import numpy as np

from nastranio.cards import PSHELL


def test_one_pshell():
    bulk1 = """\
$▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
PSHELL         1       1     .09       1               1              .1
"""
    cards = PSHELL()
    cards.parse(bulk1)
    # ========================================================================
    # test basic data
    # ========================================================================
    exp = {
        "PID": [1],
        "MID1": [1],
        "T": [0.09],
        "MID2": [1],
        "12I/T**3": [None],
        "MID3": [1],
        "TS/T": [None],
        "NSM": [0.1],
        "Z1": [None],
        "Z2": [None],
        "MID4": [None],
    }

    # pprint(cards.carddata['main'])  # TODO: remove me!(cards.carddata['main'])
    assert cards.carddata["main"] == exp
    # ========================================================================
    # test `merge` method
    # ========================================================================
    assert len(cards) == 1
    cards2 = PSHELL()
    bulk2 = """\
$▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
PSHELL       203     204    1.90     205     1.2     206     0.8    6.32+
+           +.95    -.95
"""
    cards2.parse(bulk2)
    cards.merge(cards2)
    exp = {
        "PID": [1, 203],
        "MID1": [1, 204],
        "T": [0.09, 1.9],
        "MID2": [1, 205],
        "12I/T**3": [None, 1.2],
        "MID3": [1, 206],
        "TS/T": [None, 0.8],
        "NSM": [0.1, 6.32],
        "Z1": [None, 0.95],
        "Z2": [None, -0.95],
        "MID4": [None, None],
    }

    # pprint(cards.carddata['main'])

    assert cards.carddata["main"] == exp
    # ========================================================================
    # test export_data() used for serialization
    # ========================================================================
    res = cards.export_data()
    exp = {
        "card": "PSHELL",
        "main": {
            "12I/T**3": [None, 1.2],
            "MID1": [1, 204],
            "MID2": [1, 205],
            "MID3": [1, 206],
            "MID4": [None, None],
            "NSM": [0.1, 6.32],
            "PID": [1, 203],
            "T": [0.09, 1.9],
            "TS/T": [None, 0.8],
            "Z1": [None, 0.95],
            "Z2": [None, -0.95],
        },
    }

    # pprint(res)

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
    expected = """\
$PSHELL▕    PID▕   MID1▕      T▕   MID2▕12I/T..▕   MID3▕   TS/T▕    NSM▕+      ▕
$+     ▕     Z1▕     Z2▕   MID4▕       ▕       ▕       ▕       ▕       ▕       ▕
PSHELL         1       1     .09       1               1              .1
PSHELL       203     204     1.9     205     1.2     206      .8    6.32+
+            .95    -.95"""
    print(expected)
    assert nas == expected

    # ========================================================================
    # thicknesses
    # ========================================================================
    thk = cards.thk
    print(thk["data"])
    np.testing.assert_allclose(thk["data"], np.array([0.09, 1.9]))
    print(thk["index"])
    np.testing.assert_allclose(thk["index"], np.array([1, 203]))
    assert thk["name"] == "pid2thk"
