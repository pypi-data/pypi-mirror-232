#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests NASTRAN fields writer"""

import pytest

from nastranio.fields_writer import trans


def test_trans():
    checks_8chars = (
        (6250, "6250"),
        (-6250, "-6250"),
        (0.0, "0."),
        (123456789, ValueError),
        (-123456789, ValueError),
        (-0.0, "0."),
        (6250.0, "6250."),
        (-0.123456789, "-.123457"),
        (0.123456789, ".1234568"),
        (0.0023148, ".0023148"),
        (0.023622, ".023622"),
        (-1.987654e-12, "-1.99-12"),
        (1.987654e-12, "1.988-12"),
        (None, ""),
    )
    errors = []
    for val, exp in checks_8chars:
        if exp == ValueError:
            with pytest.raises(ValueError) as e_info:
                act = trans(val)
        else:
            act = trans(val)
            if act != exp:
                errors.append((val, exp, trans(val)))
    assert errors == []
