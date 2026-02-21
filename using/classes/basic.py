from abc import abstractmethod, ABC
from functools import singledispatchmethod


class Animal:
    # Поля класса: тут важен знак "="
    LEGS_COUNT = 4  # uppercase указывает что это константа (соглашение)
    default_color = "red"

    # Поле экземпляра с аннотацией типа, знака "=" нет
    color: str

    def __init__(self, name, age):
        self.__name = name  # соглашение о private
        self._age = age  # соглашение о protected
        self.color = self.default_color

    @property
    def name(self):
        print("called getter of name")
        return self.__name

    @name.setter
    def name(self, value):
        print("called setter of name")
        self.__name = value

    @name.deleter
    def name(self):
        print("called deleter of name")

    # Перегрузки методов - нет. Но можно реализовать через аннотации @singledispatchmethod
    @singledispatchmethod
    def method(self, arg):
        print("run " + str(type(self)))

    @method.register
    def _(self, a: int):
        print("run " + str(type(self)))

    @method.register
    def _(self, arg: str):
        print("str:", arg)


class Dog(Animal):
    # Переопределил конструктор
    def __init__(self, name, age):
        super().__init__(name, age)
        self.breed = "todo"

    @classmethod
    def create_unknown_breed(cls, name, age):
        res = cls(name, age)
        res.breed = "unknown"
        return res

    @staticmethod
    def helper_function():
        return "this_is_animal"


class Cat(Animal):
    pass


class FlyableAnimal(ABC):
    @abstractmethod
    def fly(self):
        pass


class ButterFly(Animal, FlyableAnimal):
    # без реализации получим: Can't instantiate abstract class ButterFly with abstract method fly
    def fly(self):
        print("fly")


def main():
    print("Property")
    print()
    c = Cat("Kitty", 2)
    print(c.name)

    d = Dog("Bob", 1)
    print(d.name)

    del d.name

    print("Class methods")
    print()
    # Можно изменить переменную класса, то это не сработает глобально если делать на экземпляре
    d.LEGS_COUNT = 5
    print(d.LEGS_COUNT, c.LEGS_COUNT, Animal.LEGS_COUNT)  # 5, 4, 4

    # Но сработает если менять на классе
    Animal.LEGS_COUNT = 5
    print(d.LEGS_COUNT, c.LEGS_COUNT, Animal.LEGS_COUNT)  # 5, 5, 5

    # new legs count
    print(c.LEGS_COUNT)

    # @classmethod обычно используется для static-конструктор
    ud1 = Dog.create_unknown_breed("sema1", 4)
    print(ud1.breed)

    # @classmethod можно вызывать и на instance, но не принято
    ud2 = ud1.create_unknown_breed("sema2", 4)
    print(ud2.breed)

    print("Static methods")
    print()
    # @staticmethod - используется когда надо сгруппировать функции, например при создании helpers.
    # Точно также вызывается и для cls и для self.
    print(d.helper_function())
    print(Dog.helper_function())

    print("Name mangling")
    print()
    # print(d.__name) # "private" - не работает
    print(d._Animal__name)  # по mangling имени все работает
    print(d._age)  # "protected" - работает

    print("Check instances")
    print(isinstance(d, Dog))  # True
    print(isinstance(c, Dog))  # False
    print(issubclass(Dog, Animal))  # True

    print("Using ABC to implement interface")
    bf = ButterFly("bf", 1)
    print(bf.fly())


if __name__ == "__main__":
    main()
