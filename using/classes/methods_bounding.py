class A:
    def __init__(self, name):
        self.name = name

    @classmethod
    def class_method(cls):
        return "res of class_method of " + str(type(cls))

    @staticmethod
    def static_method():
        return "res of static_method"

    def instance_function(self):
        return "res of " + self.name + " instance_function of ", str(type(self))

    def recall_instance_function(self, obj):
        # можно вызвать метод на другом объекте
        return A.instance_function(obj)


def main():
    a = A("AA")
    print(a.instance_function())
    print(A.static_method())
    print(A.class_method())

    print("bounding")
    b = A("BB")
    print()
    m = a.instance_function
    print(m)  # <bound method Animal.instance_function of <__main__.Animal object at 0x102e95df0>>
    print("result", m())
    print()

    print("recalling on another object")
    print(a.recall_instance_function(b))

    m = A.class_method
    print(m)  # <bound method Animal.class_method of <class '__main__.Animal'>>
    print("result", m())
    print()

    m = A.static_method
    print(m)  # <function Animal.static_method at 0x102e88a60>
    print("result", m())
    print()


if __name__ == '__main__':
    main()
