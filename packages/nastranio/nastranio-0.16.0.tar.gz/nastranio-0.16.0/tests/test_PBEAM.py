#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Low-Level Tests PBEAM card parser

    ref: NX Nastran 12 Quick Reference Guide 16-48 (p.2278)
"""

from pprint import pprint

import pytest

from nastranio.cards import PBEAM


@pytest.fixture
def parsed_bulk():
    cards = PBEAM()
    # fmt: off
    cards_bulk = [
        """\
        $ MULTI-SECTIONS EXAMPLE:
     $▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
     PBEAM         39       6     2.9     3.5    5.97                        +
     +                            2.0    -4.0                                +
     +            YES     0.3     5.3    56.2    78.6                        +
     +                            2.5    -5.0                                +
     +            YES     0.7     6.3    56.2    78.6                        +
     +                            2.5    -6.0                                +
     +            YES     1.0     7.3    56.2    78.6                        +
     +                            2.5    -7.0                                +
     +                            1.1             2.1            0.21        +
     +                                            0.5             0.0""",
        """\
     $ EXAMPLE FROM NASTRAN QRF:
     $▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
     PBEAM         38       6     2.9     3.5    5.97                        +
     +                            2.0    -4.0                                +
     +            YES     1.0     5.3    56.2    78.6                        +
     +                            2.5    -5.0                                +
     +                            1.1             2.1            0.21        +
     +                                            0.5             0.0""",
        """\
     $ NON-TAPERED Example from FEMAP output
     $▔▔1▔▔▔╲╱▔▔2▔▔▔╲╱▔▔3▔▔▔╲╱▔▔4▔▔▔╲╱▔▔5▔▔▔╲╱▔▔6▔▔▔╲╱▔▔7▔▔▔╲╱▔▔8▔▔▔╲╱▔▔9▔▔▔╲╱▔▔10▔▔╲
     PBEAM          3       1194.608516472.8212762.021742.82119826.97      0.+
     +       21.8391310.80548-10.04788.933607-9.78819-10.188521.83913-1.69452+
     +           YESA      1.                                                +
     +       .5070713.4308804""",
    ]
    # fmt: on
    cards.parse(cards_bulk.pop(0))
    for card in cards_bulk:
        _ = PBEAM()
        _.parse(card)
        cards.merge(_)
    return cards


def test_to_nastran_nodefault(parsed_bulk):
    """test to_nastran() method without expliciting default values"""
    cards = parsed_bulk
    nas = "\n".join(cards.to_nastran(ruler=True, with_default=False))
    expected = """\
$PBEAM ▕    PID▕    MID▕   A(A)▕  I1(A)▕  I2(A)▕ I12(A)▕   J(A)▕ NSM(A)▕+      ▕
$+     ▕  C1(A)▕  C2(A)▕  D1(A)▕  D2(A)▕  E1(A)▕  E2(A)▕  F1(A)▕  F2(A)▕       ▕
$ + repeated fields...
PBEAM         39       6     2.9     3.5    5.97                        +
+                             2.     -4.                                +
+            YES      .3     5.3    56.2    78.6                        +
+                            2.5     -5.                                +
+            YES      .7     6.3    56.2    78.6                        +
+                            2.5     -6.                                +
+            YES      1.     7.3    56.2    78.6                        +
+                            2.5     -7.                                +
+                            1.1             2.1             .21        +
+                                             .5              0.
PBEAM         38       6     2.9     3.5    5.97                        +
+                             2.     -4.                                +
+            YES      1.     5.3    56.2    78.6                        +
+                            2.5     -5.                                +
+                            1.1             2.1             .21        +
+                                             .5              0.
PBEAM          3       1194.608516472.8212762.021742.82119826.97        +
+       21.8391310.80548-10.04788.933607-9.78819-10.188521.83913-1.69452+
+           YESA      1.                                                +
+       .5070713.4308804"""

    print(nas)
    assert nas == expected


def test_to_nastran(parsed_bulk):
    """test to_nastran() method"""
    cards = parsed_bulk
    nas = "\n".join(cards.to_nastran(ruler=True))
    expected = """\
$PBEAM ▕    PID▕    MID▕   A(A)▕  I1(A)▕  I2(A)▕ I12(A)▕   J(A)▕ NSM(A)▕+      ▕
$+     ▕  C1(A)▕  C2(A)▕  D1(A)▕  D2(A)▕  E1(A)▕  E2(A)▕  F1(A)▕  F2(A)▕       ▕
$ + repeated fields...
PBEAM         39       6     2.9     3.5    5.97      0.      0.      0.+
+                             2.     -4.                                +
+            YES      .3     5.3    56.2    78.6                        +
+                            2.5     -5.                                +
+            YES      .7     6.3    56.2    78.6                        +
+                            2.5     -6.                                +
+            YES      1.     7.3    56.2    78.6                        +
+                            2.5     -7.                                +
+                            1.1             2.1             .21        +
+                                             .5              0.
PBEAM         38       6     2.9     3.5    5.97      0.      0.      0.+
+                             2.     -4.                                +
+            YES      1.     5.3    56.2    78.6                        +
+                            2.5     -5.                                +
+                            1.1             2.1             .21        +
+                                             .5              0.
PBEAM          3       1194.608516472.8212762.021742.82119826.97      0.+
+       21.8391310.80548-10.04788.933607-9.78819-10.188521.83913-1.69452+
+           YESA      1.                                                +
+       .5070713.4308804"""

    print(nas)
    assert nas == expected


def test_export_data(parsed_bulk):
    cards = parsed_bulk
    res = cards.export_data()
    pprint(res)

    exp = {
        "main": {
            "A(A)": [2.9, 2.9, 194.6085],
            "C1(A)": [None, None, 21.83913],
            "C2(A)": [None, None, 10.80548],
            "CW(A)": [0.21, 0.21, None],
            "CW(B)": [None, None, None],
            "D1(A)": [2.0, 2.0, -10.0478],
            "D2(A)": [-4.0, -4.0, 8.933607],
            "E1(A)": [None, None, -9.78819],
            "E2(A)": [None, None, -10.1885],
            "F1(A)": [None, None, 21.83913],
            "F2(A)": [None, None, -1.69452],
            "I1(A)": [3.5, 3.5, 16472.82],
            "I12(A)": [0.0, 0.0, 1742.821],
            "I2(A)": [5.97, 5.97, 12762.02],
            "J(A)": [0.0, 0.0, 19826.97],
            "K1": [None, None, 0.5070713],
            "K2": [None, None, 0.4308804],
            "M1(A)": [None, None, None],
            "M1(B)": [None, None, None],
            "M2(A)": [None, None, None],
            "M2(B)": [None, None, None],
            "MID": [6, 6, 1],
            "N1(A)": [0.5, 0.5, None],
            "N1(B)": [0.0, 0.0, None],
            "N2(A)": [None, None, None],
            "N2(B)": [None, None, None],
            "NSI(A)": [2.1, 2.1, None],
            "NSI(B)": [None, None, None],
            "NSM(A)": [0.0, 0.0, 0.0],
            "PID": [39, 38, 3],
            "S1": [1.1, 1.1, None],
            "S2": [None, None, None],
            "pbeam_stationsID": [0, 1, 2],
        },
        "card": "PBEAM",
        "pbeam_stations": [
            [
                {
                    "A": 5.3,
                    "C1": None,
                    "C2": None,
                    "D1": 2.5,
                    "D2": -5.0,
                    "E1": None,
                    "E2": None,
                    "F1": None,
                    "F2": None,
                    "I1": 56.2,
                    "I12": None,
                    "I2": 78.6,
                    "J": None,
                    "NSM": None,
                    "SO": "YES",
                    "X/XB": 0.3,
                },
                {
                    "A": 6.3,
                    "C1": None,
                    "C2": None,
                    "D1": 2.5,
                    "D2": -6.0,
                    "E1": None,
                    "E2": None,
                    "F1": None,
                    "F2": None,
                    "I1": 56.2,
                    "I12": None,
                    "I2": 78.6,
                    "J": None,
                    "NSM": None,
                    "SO": "YES",
                    "X/XB": 0.7,
                },
                {
                    "A": 7.3,
                    "C1": None,
                    "C2": None,
                    "D1": 2.5,
                    "D2": -7.0,
                    "E1": None,
                    "E2": None,
                    "F1": None,
                    "F2": None,
                    "I1": 56.2,
                    "I12": None,
                    "I2": 78.6,
                    "J": None,
                    "NSM": None,
                    "SO": "YES",
                    "X/XB": 1.0,
                },
            ],
            [
                {
                    "A": 5.3,
                    "C1": None,
                    "C2": None,
                    "D1": 2.5,
                    "D2": -5.0,
                    "E1": None,
                    "E2": None,
                    "F1": None,
                    "F2": None,
                    "I1": 56.2,
                    "I12": None,
                    "I2": 78.6,
                    "J": None,
                    "NSM": None,
                    "SO": "YES",
                    "X/XB": 1.0,
                }
            ],
            [
                {
                    "A": None,
                    "C1": None,
                    "C2": None,
                    "D1": None,
                    "D2": None,
                    "E1": None,
                    "E2": None,
                    "F1": None,
                    "F2": None,
                    "I1": None,
                    "I12": None,
                    "I2": None,
                    "J": None,
                    "NSM": None,
                    "SO": "YESA",
                    "X/XB": 1.0,
                }
            ],
        ],
    }

    assert res == exp
