from lindh.jsonobject import Property, Query


def test_to_query_string():
    class Q(Query):
        a: int = Property()
        b: str = Property()

    q = Q(a=42, b='blerg')
    qs = q.to_query_string()
    assert qs == 'a=42&b=blerg'
