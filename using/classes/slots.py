import sys


class SlotsPoint:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "SlotsPoint(%r, %r)" % (self.x, self.y)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point(%r, %r)" % (self.x, self.y)


def main():
    sp = SlotsPoint(1, 2)
    # sp.z = 3 # не разрешено
    print(sp, "size", sys.getsizeof(sp))  # 48

    # getsizeof не считает размер вложенных структур, поэтому прибавим отдельно __dict__
    p = Point(1, 2)
    p.z = 3
    print(p, "size", sys.getsizeof(p) + sys.getsizeof(p.__dict__))  # 152
    print()

    print("Using total_size")
    # Более точный расчет
    print(sp, "size", total_size(sp))  # 104
    print(p, "size", total_size(p))  # 386


def total_size(obj, seen=None):
    if seen is None:
        seen = set()

    size = sys.getsizeof(obj)

    obj_id = id(obj)
    if obj_id in seen:
        return 0

    seen.add(obj_id)

    if isinstance(obj, dict):
        size += sum(total_size(v, seen) + total_size(k, seen) for k, v in obj.items())
    elif hasattr(obj, "__dict__"):
        size += total_size(obj.__dict__, seen)
    elif hasattr(obj, "__slots__"):
        for slot in obj.__slots__:
            size += total_size(getattr(obj, slot), seen)
    return size


if __name__ == "__main__":
    main()
