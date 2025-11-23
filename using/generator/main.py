def count_down(start):
    while start > 0:
        yield start
        start -= 1


def gen2():
    """
    Пример использования finally для освобождения ресурсов.
    Альтернатива: реализация with
    """
    try:
        yield 1
        yield 2
    finally:
        print("final для освобождения ресурсов")


def merge(g1, g2):
    """
    Пример использования yield from для делегирования процесс перебора другой.
    """
    yield from g1
    yield from g2


def receive():
    """
    Пример получения значения.
    """
    while True:
        n = yield
        print("received ", n)


def main():
    g1 = count_down(5)
    print(type(g1))
    for i in g1:
        print(i)
        break

    # короткий способ создать генератор, а не tuple
    g2 = (i for i in count_down(5))
    print(type(g2))

    # итерация вручную
    print(next(g2))
    # внутри вызывается
    print(g2.__next__())

    # tuple тоже можно создать
    t = tuple(i for i in count_down(5))
    print(type(t))  # tuple

    l = [i for i in count_down(5)]  # list
    print(type(l))

    g3 = gen2()
    print(type(g3))
    next(g3)
    next(g3)

    # Если элементов не осталось, то бросается StopIteration. StopIteration не ошибка, а сигнал об окончании итератора.
    # В for-цикле вы никогда не увидите StopIteration напрямую, потому что Python обрабатывает его автоматически:
    try:
        next(g3)
    except StopIteration as e:
        print("Exception:", e)  # описание пустое если не было return
        print("Exception type:", type(e))

    # merge
    print("merge")
    for i in merge(count_down(2), count_down(2)):
        print(i)

    # send and close
    receiver = receive()
    receiver.send(None)  # Сначала отправляем None, иначе: can't send non-None value to a just-started generator
    receiver.send(1)
    receiver.send(2)
    receiver.close()


if __name__ == '__main__':
    main()
