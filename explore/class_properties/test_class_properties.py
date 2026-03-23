from dataclasses import dataclass
from typing import ClassVar


def test_declare_fields_in_general_class():
    class User:
        # Поля класса (отличаются тем что есть установка значения)
        untyped_class_field = 'untyped_class_field'
        typed_class_field: str = 'typed_class_field'

        # Это поле экземпляра c аннотацией типа (поле не создано, создана только аннотация)
        typed_instance_field: str

        def __init__(self, undeclared_instance_field: str):
            self.undeclared_instance_field = undeclared_instance_field
            self.typed_instance_field = 'typed_instance_field'

    u1 = User('undeclared_instance_field')

    """
    Аннотация типа не создает поля, это просто информация о типе значения
    """
    # Аннотации типа появилась для типизированного поля класса и не появилась для не типизированного
    assert 'typed_class_field' in User.__annotations__
    assert 'untyped_class_field' not in User.__annotations__
    # В том числе в аннотации КЛАССА видно и поле экземпляра
    assert 'typed_instance_field' in User.__annotations__

    # Аннотации типа появилась для типизированного поля экземпляра и не появилась для не типизированного
    assert 'typed_instance_field' in u1.__annotations__
    assert 'undeclared_instance_field' not in u1.__annotations__
    # В том числе в аннотации экземпляра видно и поле класса
    assert 'typed_class_field' in u1.__annotations__

    # В аннотациях класса хранятся инфа о полях КЛАССА и ЭКЗЕМПЛЯРА.
    # Затем они копируются в экземпляры.
    assert User.__annotations__ == u1.__annotations__

    # Поля экземпляра есть в экземпляре
    assert 'undeclared_instance_field' in u1.__dict__
    assert 'typed_instance_field' in u1.__dict__

    # В том числе добавленное:
    u1.added_instance_field = 'added'
    assert u1.added_instance_field == 'added'
    assert 'added_instance_field' in u1.__dict__

    # Полей класса нет в экземпляре
    assert 'untyped_class_field' not in u1.__dict__
    assert 'typed_class_field' not in u1.__dict__
    # Но поля класса доступны по обращению (через resolving)
    assert u1.untyped_class_field == 'untyped_class_field'
    assert u1.typed_class_field == 'typed_class_field'

    # Поля класса есть в классе
    assert 'untyped_class_field' in User.__dict__
    assert 'typed_class_field' in User.__dict__

    # Полей экземпляра нет в классе
    assert 'undeclared_instance_field' not in User.__dict__
    assert 'typed_instance_field' not in User.__dict__
    assert 'added_instance_field' not in User.__dict__

    # И они недоступны по обращению
    try:
        assert User.undeclared_instance_field == 'undeclared_instance_field'
        assert User.typed_instance_field == 'typed_instance_field'
    except AttributeError as e:
        assert 'has no attribute' in str(e)

    # Добавленное в класс поле видно только в классе
    User.added_class_field = 'added_class_field'
    assert 'added_class_field' in User.__dict__
    # Не видно в ранее созданном экземпляре
    assert 'added_class_field' not in u1.__dict__

    u2 = User('undeclared_instance_field')
    # Не видно в ранее созданном экземпляре
    assert 'added_class_field' not in u2.__dict__


def test_shadows_class_fields():
    class User:
        typed_class_field: str = 'typed_class_field'

    u1, u2 = User(), User()
    assert u1.typed_class_field == 'typed_class_field'
    assert u2.typed_class_field == 'typed_class_field'

    # При перекрытии поля класса в экземпляре:
    u1.typed_class_field = 'new_value'
    # Она остается в классе
    assert 'typed_class_field' in User.__dict__

    # И оно добавляется в __dict__ экземпляра
    assert 'typed_class_field' in u1.__dict__
    # именно этим и достигается это перекрытие
    assert u1.typed_class_field == 'new_value'

    # Для второго объекта все осталось как есть
    assert u2.typed_class_field == 'typed_class_field'


def test_declare_fields_in_dataclass_class():
    @dataclass
    class User:
        # Поля класса (отличаются тем что есть установка значения, точно также как и в обычном)
        untyped_class_field = 'untyped_class_field'

        # Но, без classVar нельзя создать типизированное поле КЛАССА (т.е. typed_class_field: str = 'typed_class_field')
        # Потому что оно начинает классифицироваться как поле ЭКЗЕМПЛЯРА c default-значением.
        typed_class_field: ClassVar[str] = 'typed_class_field'

        # Это поле экземпляра c аннотацией типа (поле не создано, создана только аннотация)
        typed_instance_field: str
        typed_instance_field_with_default_value: str = 'typed_class_field'

    assert 'untyped_class_field' in User.__dict__
    assert 'typed_class_field' in User.__dict__

    # @dataclass автоматически создаёт __init__, __repr__, __eq__, поэтому требуется передать значения полей без default-значения
    u1 = User('typed_instance_field')

    # Поля экземпляра точно также хранятся в его __dict__
    assert 'typed_instance_field' in u1.__dict__
    assert 'typed_instance_field_with_default_value' in u1.__dict__

    # Поля класса точно также хранятся в его __dict__
    assert 'typed_class_field' in User.__dict__
    assert 'untyped_class_field' in User.__dict__

    # В аннотациях класса хранятся инфа о полях КЛАССА и ЭКЗЕМПЛЯРА.
    # Затем они копируются в экземпляры.
    assert User.__annotations__ == u1.__annotations__
