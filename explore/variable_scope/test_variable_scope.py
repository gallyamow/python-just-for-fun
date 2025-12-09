global_var = "global"


def test_func_can_read_global():
    assert global_var == "global"


def test_inner_func_can_read_global():
    def inner():
        assert global_var == "global"

    inner()


def test_inner_func_can_read_outer():
    outer_var = "outer"

    def inner():
        assert outer_var == "outer"

    inner()


def test_func_cant_write_global_without_global_statement():
    def func():
        # this assignment creates a local variable, so doesn't modify the global one
        global_var = "new_global_var"

    func()

    # the same val
    assert global_var == "global"


def test_func_can_write_global_with_global_statement():
    def func():
        global global_var
        global_var = "new_global_var"

    func()

    # changed
    assert global_var == "new_global_var"


def test_func_cant_write_outer_without_nonlocal_statement():
    outer_var = "outer"

    def func():
        # this assignment creates a local variable, so doesn't modify the outer one
        outer_var = "new_outer"

    func()

    # the same val
    assert outer_var == "outer"


def test_func_can_write_outer_with_nonlocal_statement():
    outer_var = "outer"

    def func():
        nonlocal outer_var
        outer_var = "new_outer"

    func()

    # changed
    assert outer_var == "new_outer"
