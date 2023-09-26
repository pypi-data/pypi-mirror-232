# -*- coding: utf-8 -*-

import pytest
from lindh.jsonobject import PropertySet, Property
import typing


def test_set_via_constructor():
    class O(PropertySet):
        s = Property(dict)

    o = O(s={'a': 1, 'b': 2, 'c': 3})

    assert o.s == {'a': 1, 'b': 2, 'c': 3}


def test_set_via_attribute():
    class O(PropertySet):
        s = Property(dict)

    o = O()
    o.s = {'a': 1, 'b': 2, 'c': 3}

    assert o.s == {'a': 1, 'b': 2, 'c': 3}


def test_set_required_missing():
    class O(PropertySet):
        s = Property(dict, required=True)

    with pytest.raises(ValueError):
        o = O(s=None)

    with pytest.raises(ValueError):
        o = O(s={'a': 1, 'b': 2, 'c': 3})
        o.s = None


def test_set_required_present():
    class O(PropertySet):
        s = Property(dict, required=True)

    o = O(s={'a': 1, 'b': 2, 'c': 3})

    assert o.s == {'a': 1, 'b': 2, 'c': 3}


def test_external_validator():
    def validator(value):
        if value.get('a') != 1:
            raise ValueError

    class O(PropertySet):
        s = Property(dict, validator=validator)

    o = O(s={'a': 1})

    with pytest.raises(ValueError):
        o.s = {'a': 3}


def test_bad_input_by_kwarg():
    class O(PropertySet):
        s = Property(dict)

    o = None
    with pytest.raises(ValueError):
        o = O(s=1)

    assert o is None


def test_bad_input_by_attribute():
    class O(PropertySet):
        s = Property(dict)

    o = O()

    with pytest.raises(ValueError):
        o.s = 'string'


def test_no_shared_references():
    class O(PropertySet):
        s = Property(dict)

    o1 = O()
    o2 = O()

    o1.s['a'] = 1

    assert o1.s.get('a') == 1
    assert o2.s.get('a') is None


def test_delete():
    class O(PropertySet):
        s = Property(dict)

    o = O(s={'a': 1, 'b': 2, 'c': 3})
    del o.s

    assert o.s is None


def test_default_type():
    class O(PropertySet):
        s = Property(dict)

    o = O()

    assert type(o.s) is dict


def test_via_hint():
    class O(PropertySet):
        s: dict = Property()

    o = O()

    assert type(o.s) is dict


def test_via_abstract_hint():
    class O(PropertySet):
        s: typing.Dict[str, str] = Property()

    o = O()

    assert type(o.s) is dict
