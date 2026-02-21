def test_late_binding():
    x = 2
    f = lambda y: x * y  # noqa
    x = 3
    g = lambda y: x * y  # noqa

    assert f(10) == 30
    assert g(10) == 30

    assert len(f.__closure__) == 1
    assert len(g.__closure__) == 1


def test_late_binding_correct():
    x = 2
    f = lambda y, x=x: x * y  # noqa
    x = 3
    g = lambda y, x=x: x * y  # noqa

    assert f(10) == 20
    assert g(10) == 30

    assert f.__closure__ is None
    assert g.__closure__ is None
