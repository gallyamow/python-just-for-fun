from typing import List


def func_accepts_immutable(s: str = "") -> str:
    s += "edited"
    return s


def func_accepts_mutable(l: List[str] = []) -> List[str]:
    l.append("edited")
    return l

def func_accepts_mutable_safe(l: List[str] = None) -> List[str]:
    if l is None:
        l = []

    l.append("edited")
    return l


def test_immutable():
    assert func_accepts_immutable() == "edited"
    assert func_accepts_immutable("start_") == "start_edited"

def test_mutable():
    # use always new
    assert func_accepts_mutable(["start"]) == ["start", "edited"]
    assert func_accepts_mutable(["start"]) == ["start", "edited"]

    # use the same default value
    assert func_accepts_mutable() == ["edited"]
    assert func_accepts_mutable() == ["edited", "edited"]
    assert func_accepts_mutable() == ["edited", "edited", "edited"]

def test_mutable_safe():
    # use always new
    assert func_accepts_mutable_safe(["start"]) == ["start", "edited"]
    assert func_accepts_mutable_safe(["start"]) == ["start", "edited"]

    # don't use the same default value
    assert func_accepts_mutable_safe() == ["edited"]
    assert func_accepts_mutable_safe() == ["edited"]
    assert func_accepts_mutable_safe() == ["edited"]
