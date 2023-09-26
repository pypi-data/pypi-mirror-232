# -*- coding: utf-8 -*-

import pytest
from lindh.jsonobject import PropertySet, Property


def test_other_name():
    class O(PropertySet):
        id = Property(name='_id')

    o = O(id='myid')

    assert o.id == 'myid'


def test_other_name_to_dict():
    class O(PropertySet):
        id = Property(name='_id')

    o = O(id='myid')
    d = o.to_dict()

    assert d == {'*schema': 'O', '_id': 'myid'}


def test_getting_property_from_class_object_should_return_property_object():
    class O(PropertySet):
        id = Property()

    po = O.id
    assert isinstance(po, Property)
    assert po.serialized_name == 'id'


def test_same_name_in_subclass_should_raise_error():
    class Base(PropertySet):
        a: int = Property()

    with pytest.raises(AttributeError):
        class Sub(Base):
            a: str = Property()


def test_same_name_in_two_baseclasses_should_raise_error():
    class Base1(PropertySet):
        a: int = Property()

    class Base2(PropertySet):
        a: str = Property()

    with pytest.raises(AttributeError):
        class Sub(Base1, Base2):
            pass
