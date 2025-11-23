def test_late_binding():
    x = 2
    f = lambda y: x * y
    x = 3
    g = lambda y: x * y

    assert f(10) == 30
    assert g(10) == 30

def test_late_binding_correct():
    x = 2
    f = lambda y, x = x: x * y
    x = 3
    g = lambda y, x = x: x * y

    assert f(10) == 20
    assert g(10) == 30
