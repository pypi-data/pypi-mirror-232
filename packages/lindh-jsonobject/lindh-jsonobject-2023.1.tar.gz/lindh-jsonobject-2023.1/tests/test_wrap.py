import pytest
from lindh.jsonobject import register_schema, wrap_raw_json, wrap_dict
from lindh.jsonobject import PropertySet, Property


def test_wrapping_a():
    class A(PropertySet):
        a: int = Property()

    class B(PropertySet):
        a: str = Property()

    register_schema(A)
    register_schema(B)

    class C(PropertySet):
        child = Property(wrap=True)

    c = C()
    c.child = A(a=42)
    c2 = C.FromJSON(c.to_json())

    assert isinstance(c2.child, A)
    assert c2.child.a == 42


def test_wrapping_b():
    class A(PropertySet):
        a: int = Property()

    class B(PropertySet):
        a: str = Property()

    register_schema(A)
    register_schema(B)

    class C(PropertySet):
        child = Property(wrap=True)

    c = C()
    c.child = B(a='hej')
    c2 = C.FromJSON(c.to_json())

    assert isinstance(c2.child, B)
    assert c2.child.a == 'hej'


def test_wrapping_parsed():
    class A(PropertySet):
        a: int = Property()

    class B(PropertySet):
        a: str = Property()

    register_schema(A)
    register_schema(B)

    class C(PropertySet):
        child = Property(wrap=True)

    c = C()
    a = A(a=42)
    c.child = a.to_json()

    assert isinstance(c.child, A)
    assert c.child.a == 42


def test_wrapping_parsed_none():
    assert wrap_raw_json(None) is None


def test_wrapping_dict_none():
    assert wrap_dict(None) is None


def test_wrapping_dict_with_no_schema():
    with pytest.raises(NameError):
        wrap_dict({})
