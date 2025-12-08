class Barrier:
    """
    Аналог threading.Barrier, реализованный на собственном condition.
    TODO

    Для чего:
    - чтобы группа потоков достигла одной точки и продолжила выполнение только вместе

    Как работает:
    - При создании барьера задаётся число участников (количество потоков, которые должны его пройти).
    - Каждый поток вызывает barrier.wait().
    - Потоки блокируются на wait(), пока не соберётся вся группа.
    - Когда последний поток достигает барьера — все одновременно продолжают выполнение.
    """

    __slots__=('__parties', '__action', '__timeout')

    def __init__(self, parties, action=None, timeout=None):
        self.__parties = parties
        self.__action = action
        self.__timeout = timeout

    def wait(self, timeout=None):
        pass

    def reset(self):
        pass

    def abort(self):
        pass

    @property
    def parties(self):
        return self.__parties

    @property
    def n_waiting(self):
        pass

    @property
    def broken(self):
        pass
