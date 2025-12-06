import types
import typing
from contextlib import contextmanager

import pytest


def count_down(start):
    while start > 0:
        yield start
        start -= 1


def test_count_down():
    it = count_down(3)

    assert type(it) is types.GeneratorType

    assert 3 == next(it)
    assert 2 == next(it)
    assert 1 == next(it)

    with pytest.raises(StopIteration):
        next(it)


def test_generator_expression():
    # @idiomatic: generator expression
    it = (i for i in range(3, 0, -1))

    assert type(it) is types.GeneratorType

    assert 3 == next(it)
    assert 2 == next(it)
    assert 1 == next(it)

    with pytest.raises(StopIteration):
        next(it)


def test_generator_expression_to_tuple():
    it = (i for i in range(3, 0, -1))

    # @idiomatic: way to create tuple from iterator
    t = tuple(it)
    assert type(t) is tuple


def test_iterator_protocol():
    it = count_down(3)
    assert 3 == it.__next__()
    assert 2 == it.__next__()
    assert 1 == it.__next__()


def test_stop_iteration_in_loop():
    it = count_down(3)

    """
    Если элементов не осталось, то бросается StopIteration. StopIteration не ошибка, а сигнал об окончании итератора.
    В for-цикле вы никогда не увидите StopIteration напрямую, потому что Python обрабатывает его автоматически:
    """
    res = []
    for x in it:
        res.append(x)

    # @idiomatic: first actual result, second wanted result
    assert res == [3, 2, 1]


def merge(g1, g2) -> typing.Generator:
    """
    Пример использования yield from для делегирования процесс перебора другой.
    """
    yield from g1
    yield from g2


def test_yield_from():
    it = merge(count_down(2), (i for i in range(2)))

    assert type(it) is types.GeneratorType

    res = []
    for x in it:
        res.append(x)

    assert res == [2, 1, 0, 1]


def gen_with_finally(resource: dict[str, str]):
    """
    Пример использования finally для освобождения ресурсов.
    Альтернатива: реализация with
    """
    resource['status'] = 'busy'

    try:
        yield 1
        yield 2
        yield 3
    finally:
        resource['status'] = 'free'


def test_gen_with_finally_exhausted():
    resource = {'status': 'free'}
    it = gen_with_finally(resource)

    # @idiomatic: generator is lazy
    # пока не было итераций, то функция и не вызывалась
    assert resource['status'] == 'free'
    next(it)

    assert resource['status'] == 'busy'

    # когда генератор исчерпан
    for _ in it:
        pass

    assert resource['status'] == 'free'


def test_gen_with_finally_closed():
    resource = {'status': 'free'}
    it = gen_with_finally(resource)

    # @idiomatic: generator is lazy
    # пока не было итераций, то функция и не вызывалась
    assert resource['status'] == 'free'
    next(it)

    assert resource['status'] == 'busy'

    # просто закрыли
    it.close()

    assert resource['status'] == 'free'


@contextmanager
def context_managed_generator(resource: dict[str, str]):
    """
    Пример как сделать контекстный менеджер, который автоматически захватывает и освобождает ресурс.
    На самом деле пример неудачный, так как может обрабатывать только 1 yield.
    """
    resource['status'] = 'busy'

    try:
        yield 1
    finally:
        resource['status'] = 'free'


def test_context_managed_generator():
    resource = {'status': 'free'}
    it = context_managed_generator(resource)

    with it:
        # @idiomatic: consume all values from iterator
        # collections.deque(it, maxlen=0)
        # or can use list if memory is not a problem
        # list(it)
        assert resource['status'] == 'busy'

    assert resource['status'] == 'free'


# @idiomatic: using list[], dict[] instead of typing.List, typing.Dict
def get_with_receiving(res: list[int]):
    """
    Пример получения значения.
    """
    while True:
        n = yield
        res.append(n)


def test_receive():
    res = []
    it = get_with_receiving(res)

    # Сначала должны отправлять None, иначе:
    # can't send non-None value to a just-started generator
    it.send(None)

    it.send(1)
    it.send(2)
    it.send(3)
    it.close()

    assert res == [1,2,3]
