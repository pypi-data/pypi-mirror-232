# -*- coding: utf-8 -*-

import pytest
from lindh.jsonobject import PropertySet, Property
from typing import List


def test_list_of_property_sets():
    class P(PropertySet):
        s = Property()

    class O(PropertySet):
        s = Property(P, is_list=True)

    p1 = P()
    p2 = P()
    p3 = P()
    o = O(s=[p1, p2, p3])

    assert len(o.s) == 3
    assert o.s == [p1, p2, p3]
    assert o.to_dict() == O(o.to_dict()).to_dict()


def test_list_of_property_sets_appending():
    class P(PropertySet):
        s = Property()

    class O(PropertySet):
        s = Property(P, is_list=True)

    p1 = P()
    p2 = P()
    p3 = P()
    o = O()

    assert len(o.s) == 0
    assert o.s == []
    assert o.to_dict() == O(o.to_dict()).to_dict()

    o.s.append(p1)
    o.s.append(p2)
    o.s.append(p3)

    assert len(o.s) == 3
    assert o.s == [p1, p2, p3]
    assert o.to_dict() == O(o.to_dict()).to_dict()


def test_list_of_property_sets_pop():
    class P(PropertySet):
        s = Property()

    class O(PropertySet):
        s = Property(P, is_list=True)

    p1 = P()
    p2 = P()
    p3 = P()
    o = O(s=[p1, p2, p3])

    assert len(o.s) == 3
    assert o.s == [p1, p2, p3]
    assert o.to_dict() == O(o.to_dict()).to_dict()

    p = o.s.pop()

    assert p == p3
    assert len(o.s) == 2
    assert o.s == [p1, p2]
    assert o.to_dict() == O(o.to_dict()).to_dict()

    p = o.s.pop(0)

    assert p == p1
    assert len(o.s) == 1
    assert o.s == [p2]
    assert o.to_dict() == O(o.to_dict()).to_dict()


def test_list_of_property_sets_not_set():
    class P(PropertySet):
        s = Property()

    class O(PropertySet):
        s = Property(P, is_list=True)

    o = O()

    assert len(o.s) == 0
    assert o.s == []
    assert o.to_dict() == O(o.to_dict()).to_dict()


def test_list_of_property_sets_unset():
    class P(PropertySet):
        s = Property()

    class O(PropertySet):
        s = Property(P, is_list=True)

    o = O(s=[P(), P()])

    assert len(o.s) == 2

    o.s = None

    assert o.s == []
    assert o.to_dict() == O(o.to_dict()).to_dict()


def test_list_of_property_sets_delete():
    class P(PropertySet):
        s = Property()

    class O(PropertySet):
        s = Property(P, is_list=True)

    o = O(s=[P(), P()])

    assert len(o.s) == 2

    del o.s

    assert o.s == []
    assert o.to_dict() == O(o.to_dict()).to_dict()


def test_strings():
    with pytest.raises(ValueError):
        class O(PropertySet):
            s = Property(is_list=True)


def test_ints():
    with pytest.raises(ValueError):
        class O(PropertySet):
            s = Property(int, is_list=True)


def test_booleans():
    with pytest.raises(ValueError):
        class O(PropertySet):
            s = Property(bool, is_list=True)


def test_floats():
    with pytest.raises(ValueError):
        class O(PropertySet):
            s = Property(float, is_list=True)


def test_none():
    class P(PropertySet):
        pass

    with pytest.raises(ValueError):
        class O(PropertySet):
            s = Property(P, is_list=True, none=1)


def test_default():
    class P(PropertySet):
        pass

    with pytest.raises(ValueError):
        class O(PropertySet):
            s = Property(P, is_list=True, default=1)


def test_list_via_hint():
    class P(PropertySet):
        s: str = Property()

    class O(PropertySet):
        s: List[P] = Property()

    p1 = P()
    p2 = P()
    p3 = P()
    o = O(s=[p1, p2, p3])

    assert len(o.s) == 3
    assert o.s == [p1, p2, p3]
    assert o.to_dict() == O(o.to_dict()).to_dict()
