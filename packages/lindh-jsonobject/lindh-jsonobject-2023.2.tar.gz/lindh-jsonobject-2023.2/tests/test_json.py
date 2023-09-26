from lindh.jsonobject import PropertySet, Property


def test_json_1():
    class O(PropertySet):
        a = Property(str)
        b = Property(int)
        c = Property(float)
        d = Property(bool)
        e = Property(list)

    o = O(
        a='test',
        b=42,
        c=42.3,
        d=True,
        e=[1, 'string', False],
    )

    assert o.to_dict() == O(o.to_dict()).to_dict()
    assert o.to_json() == O.FromJSON(o.to_json()).to_json()


def test_json_2():
    class P(PropertySet):
        a = Property(int)

    class O(PropertySet):
        a = Property(str)
        b = Property(int)
        c = Property(float)
        d = Property(bool)
        e = Property(list)
        f = Property(P)

    o = O(
        a='test',
        b=42,
        c=42.3,
        d=True,
        e=[1, 'string', False],
        f=P(a=45),
    )

    assert o.to_dict() == O(o.to_dict()).to_dict()
    assert o.to_json() == O.FromJSON(o.to_json()).to_json()


def test_json_3():
    class P(PropertySet):
        a = Property(int)

    class O(PropertySet):
        a = Property(str)
        b = Property(int)
        c = Property(float)
        d = Property(bool)
        e = Property(list)
        f = Property(P, is_list=True)

    o = O(
        a='test',
        b=42,
        c=42.3,
        d=True,
        e=[1, 'string', False],
        f=[P(a=45)],
    )

    assert o.to_dict() == O(o.to_dict()).to_dict()
    assert o.to_json() == O.FromJSON(o.to_json()).to_json()


def test_json_4():
    class P(PropertySet):
        a = Property(int)

    class O(PropertySet):
        d = Property(dict)

    o = O()

    assert o.to_dict().get('d') == {}
    assert o.to_dict() == O(o.to_dict()).to_dict()
    assert o.to_json() == O.FromJSON(o.to_json()).to_json()


def test_if_string_is_passed_to_sub_propertyset_it_should_be_parsed():
    class P(PropertySet):
        a: int = Property()

    class Q(PropertySet):
        p: P = Property()

    q = Q()
    q.p = '{"a": 42}'
    assert q.p.a == 42


def test_if_none_passed_to_from_json_results_in_unchanged():
    class P(PropertySet):
        a: int = Property(default=42)

    p = P()
    p.a = 5
    p.from_json(None)
    assert p.a == 5


def test_calculated_should_be_ignored():
    class A(PropertySet):
        a: int = Property()
        b: int = Property(calculated=True)

    a = A(a=42)
    a.b = a.a * 2
    assert a.b == 84
    da = a.to_dict()
    assert 'b' not in da.keys()
    a.b = 1
    a.from_dict(da)
    assert a.b == 1
    da['b'] = 14
    a.from_dict(da)
    assert a.b == 1
