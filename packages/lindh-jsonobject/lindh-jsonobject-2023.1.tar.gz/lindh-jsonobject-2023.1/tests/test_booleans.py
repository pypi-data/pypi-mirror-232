# -*- coding: utf-8 -*-

import pytest
from lindh.jsonobject import PropertySet, Property


def test_set_via_constructor():
    class O(PropertySet):
        s = Property(bool)

    o = O(s=True)

    assert o.s is True


def test_set_via_attribute():
    class O(PropertySet):
        s = Property(bool)

    o = O()
    o.s = True

    assert o.s is True


def test_set_default():
    class O(PropertySet):
        s = Property(bool, default=True)

    o = O()

    assert o.s is True


def test_set_required_missing():
    class O(PropertySet):
        s = Property(bool, required=True)

    with pytest.raises(ValueError):
        o = O(s=None)

    with pytest.raises(ValueError):
        o = O(s=True)
        o.s = None


def test_set_required_present():
    class O(PropertySet):
        s = Property(bool, required=True)

    o = O(s=True)

    assert o.s is True


def test_none_by_kwarg():
    class O(PropertySet):
        s = Property(bool, none=False)

    o = O(s=None)

    assert o.s is False


def test_none_by_default():
    class O(PropertySet):
        s = Property(bool, none=False)

    o = O()

    assert o.s is False


def test_none_by_explicit_default():
    class O(PropertySet):
        s = Property(bool, default=None, none=False)

    o = O()

    assert o.s is False


def test_none_by_attribute():
    class O(PropertySet):
        s = Property(bool, none=False)

    o = O()
    o.s = None

    assert o.s is False


def test_external_validator():
    def validator(value):
        if value is False:
            raise ValueError

    class O(PropertySet):
        s = Property(bool, validator=validator)

    o = O(s=True)

    with pytest.raises(ValueError):
        o.s = False


def test_bad_input_by_kwarg():
    class O(PropertySet):
        s = Property(bool)

    o = None
    with pytest.raises(ValueError):
        o = O(s='string')

    assert o is None


def test_bad_input_by_attribute():
    class O(PropertySet):
        s = Property(bool)

    o = O()

    with pytest.raises(ValueError):
        o.s = 'string'


@pytest.mark.parametrize("word,expected", [
    ("yes", True),
    ("no", False),
    ("true", True),
    ("false", False),
    ("0", False),
    ("1", True),
    (0, False),
    (1, True),
])
def test_bool_word(word, expected):
    class O(PropertySet):
        s = Property(bool)

    o = O()
    o.s = word

    assert o.s is expected


def test_boo_tuple_should_raise():
    class O(PropertySet):
        s = Property(bool)

    o = O()
    with pytest.raises(ValueError):
        o.s = (True, False)


def test_delete():
    class O(PropertySet):
        s = Property(bool)

    o = O(s=True)
    del o.s

    assert o.s is None


def test_type_via_hint():
    class O(PropertySet):
        s: bool = Property()

    o = O(s='yes')

    assert type(o.s) is bool
