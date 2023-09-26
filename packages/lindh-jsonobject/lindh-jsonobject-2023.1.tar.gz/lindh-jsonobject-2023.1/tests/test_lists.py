# -*- coding: utf-8 -*-

import pytest
from lindh.jsonobject import PropertySet, Property


def test_set_via_constructor():
    class O(PropertySet):
        s = Property(list)

    o = O(s=[1, 2, 3])

    assert o.s == [1, 2, 3]


def test_set_via_attribute():
    class O(PropertySet):
        s = Property(list)

    o = O()
    o.s = [1, 2, 3]

    assert o.s == [1, 2, 3]


def test_set_required_missing():
    class O(PropertySet):
        s = Property(list, required=True)

    with pytest.raises(ValueError):
        o = O(s=None)

    with pytest.raises(ValueError):
        o = O(s=[1, 2, 3])
        o.s = None


def test_set_required_present():
    class O(PropertySet):
        s = Property(list, required=True)

    o = O(s=[1, 2, 3])

    assert o.s == [1, 2, 3]


def test_external_validator():
    def validator(value):
        if len(value) != 1:
            raise ValueError

    class O(PropertySet):
        s = Property(list, validator=validator)

    o = O(s=[1])

    with pytest.raises(ValueError):
        o.s = [1, 2]


def test_bad_input_by_kwarg():
    class O(PropertySet):
        s = Property(list)

    o = None
    with pytest.raises(ValueError):
        o = O(s=1)

    assert o is None


def test_bad_input_by_attribute():
    class O(PropertySet):
        s = Property(list)

    o = O()

    with pytest.raises(ValueError):
        o.s = 'string'


def test_no_shared_references():
    class O(PropertySet):
        s = Property(list)

    o1 = O()
    o2 = O()

    o1.s.append(1)

    assert o1.s == [1]
    assert o2.s == []


def test_delete():
    class O(PropertySet):
        s = Property(list)

    o = O(s=[1, 2, 3])
    del o.s

    assert o.s is None
