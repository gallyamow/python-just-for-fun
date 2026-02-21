from dataclasses import dataclass, field

"""
dataclass — это декоратор из модуля dataclasses, который автоматически создаёт “базовые” методы для класса, такие как:
    * __init__ — конструктор
    * __repr__ — строковое представление
    * __eq__ — сравнение объектов
Идея: сократить рутину при создании классов, которые хранят данные.
Особенность: поля - cls.
Работает на eval.
"""


@dataclass
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class ImmutablePoint:
    x: int
    y: int


@dataclass
class Person:
    name: str
    password: str = field(
        repr=False
    )  # вот так можно указать не показывать это поле в __repr__


class BasicPoint:
    # Это поле класса
    default_color = "red"

    # Это поля экземпляра с аннотацией типов.
    x: int
    y: int

    def __init__(self, x, y):
        # Это конструктор, который создаст реальные поля x и y для каждого экземпляра класса.
        self.x = x
        self.y = y

    def __repr__(self):
        return f"BasicPoint({self.x}, {self.y})"


def main():
    p1 = Point(1, 2)
    print(p1)

    p2 = ImmutablePoint(1, 2)
    # fp.x = 3 # AttributeError: can't set attribute
    print(p2)

    u = Person("ivan", "123")
    print(u)

    bp = BasicPoint(1, 2)
    print(bp)


if __name__ == "__main__":
    main()
