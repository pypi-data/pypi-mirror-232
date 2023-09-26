# -*- coding: utf-8 -*-

import pytest
from lindh.jsonobject import PropertySet, Property


def test_set_via_constructor():
    class O(PropertySet):
        s = Property(int)

    o = O(s=1)

    assert o.s == 1


def test_type_hint_set_via_constructor():
    class O(PropertySet):
        s: int = Property()

    o = O(s=1)

    assert o.s == 1


def test_set_via_attribute():
    class O(PropertySet):
        s = Property(int)

    o = O()
    o.s = 1

    assert o.s == 1


def test_type_hint_set_via_attribute():
    class O(PropertySet):
        s: int = Property()

    o = O()
    o.s = 1

    assert o.s == 1


def test_set_default():
    class O(PropertySet):
        s = Property(int, default=1)

    o = O()

    assert o.s == 1


def test_set_required_missing():
    class O(PropertySet):
        s = Property(int, required=True)

    with pytest.raises(ValueError):
        o = O(s=None)

    with pytest.raises(ValueError):
        o = O(s=1)
        o.s = None


def test_set_required_present():
    class O(PropertySet):
        s = Property(int, required=True)

    o = O(s=1)

    assert o.s == 1


def test_none_by_kwarg():
    class O(PropertySet):
        s = Property(int, none=0)

    o = O(s=None)

    assert o.s == 0


def test_none_by_default():
    class O(PropertySet):
        s = Property(int, none=0)

    o = O()

    assert o.s == 0


def test_none_by_explicit_default():
    class O(PropertySet):
        s = Property(int, default=None, none=-1)

    o = O()

    assert o.s == -1


def test_none_by_attribute():
    class O(PropertySet):
        s = Property(int, none=-1)

    o = O()
    o.s = None

    assert o.s == -1


def test_external_validator():
    def validator(value):
        if value < 0:
            raise ValueError

    class O(PropertySet):
        s = Property(int, validator=validator)

    o = O(s=1)

    with pytest.raises(ValueError):
        o.s = -1


def test_bad_input_by_kwarg():
    class O(PropertySet):
        s = Property(int)

    o = None
    with pytest.raises(ValueError):
        o = O(s='string')

    assert o is None


def test_bad_input_by_attribute():
    class O(PropertySet):
        s = Property(int)

    o = O()

    with pytest.raises(ValueError):
        o.s = 'string'


def test_delete():
    class O(PropertySet):
        s = Property(int)

    o = O(s=1)
    del o.s

    assert o.s is None
