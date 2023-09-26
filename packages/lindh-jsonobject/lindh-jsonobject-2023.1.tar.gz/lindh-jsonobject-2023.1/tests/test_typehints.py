import pytest
from .util import uses_typehints
from lindh.jsonobject import PropertySet, Property, EnumProperty
from typing import List


@uses_typehints
def test_simple_object():
    class A(PropertySet):
        a: str = Property()
        b: int = Property()
        c: float = Property()

    a = A(a='hej', b=42, c=2.0)

    assert type(a.a) is str
    assert a.a == 'hej'
    assert type(a.b) is int
    assert a.b == 42
    assert type(a.c) is float
    assert a.c == 2.0


@uses_typehints
def test_object_with_enum():
    class E(EnumProperty):
        a = 'aaa'
        b = 'ccc'

    class A(PropertySet):
        e: E = Property(default=E.a)

    a = A()

    assert type(a.e) is E
    assert a.e is E.a


@uses_typehints
def test_complex_object_with_list():
    class B(PropertySet):
        i: int = Property()

    class A(PropertySet):
        l: List[B] = Property(name='Listan')

    a = A()
    a.l.append(B(i=1))
    a.l.append(B(i=2))

    assert type(a.l) is list
    assert len(a.l) == 2
    assert a.l[0].i == 1
    assert a.l[1].i == 2


@uses_typehints
def test_list_without_type_raises_exception():
    with pytest.raises(TypeError):
        class A(PropertySet):
            l: List = Property(name='Listan')
