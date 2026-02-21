"""
matplotlib — это самая популярная библиотека Python для визуализации данных. Она позволяет строить графики любого типа:
линейные, столбчатые, круговые диаграммы, гистограммы, тепловые карты и многое другое.

Для чего:
- Построение базовых графиков: линии, точки, столбцы.
- Настройка осей, подписей, легенд.
- Работа с несколькими графиками на одном рисунке.
- Сохранение графиков в файлы различных форматов (PNG, JPG, PDF).
- Гибкая настройка внешнего вида.
"""

import random
import matplotlib
import numpy as np

matplotlib.use("TkAgg")  # ВАЖНО: до pyplot!, требует sudo apt install python3-tk

import matplotlib.pyplot as plt


def plot_line():
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 3, 6, 5]

    plt.plot(x, y)
    plt.title("Простой линейный график")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()


def plot_several_lines():
    x = [1, 2, 3, 4]

    plt.plot(x, [i * 1 for i in x], label="×1")
    plt.plot(x, [i * 2 for i in x], label="×2")
    plt.plot(x, [i * 3 for i in x], label="×3")

    plt.title("Несколько линий на одном графике")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_bar():
    labels = ["A", "B", "C", "D"]
    values = [10, 24, 36, 18]

    plt.bar(labels, values)
    plt.title("Столбчатая диаграмма")
    plt.xlabel("Категории")
    plt.ylabel("Значения")
    plt.show()


def plot_diagram():
    x = [i for i in range(50)]
    y = [random.randint(0, 100) for _ in range(50)]

    plt.scatter(x, y)
    plt.title("Диаграмма рассеяния")
    plt.xlabel("Номер")
    plt.ylabel("Случайное значение")
    plt.show()


def plot_3d_surface():
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    # Создаёт список (массив) чисел, равномерно распределённых между двумя значениями.
    x = np.linspace(-5, 5, 60)
    y = np.linspace(-5, 5, 60)

    # Делает сетку всех возможных сочетаний X и Y
    # Теперь каждая позиция (i, j) — это точка (X[i][j], Y[i][j]).
    x, y = np.meshgrid(x, y)

    # Функция Z = sin( sqrt(x²+y²) )
    z = np.sin(np.sqrt(x**2 + y**2))

    # Рисуем 3D поверхность
    ax.plot_surface(x, y, z, cmap="viridis", edgecolor="none")

    ax.set_title("3D поверхность — волна")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    """
    linspace = [0,1,2,3,4,5,6,7,8,9,10]
    """
    # x = np.linspace(0, 10, 11)
    # y = np.linspace(0, 10, 11)
    # print(x)
    # x, y = np.meshgrid(x, y)
    """
    meshgrid = 
    [[ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
     [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]]
     """

    plt.show()


if __name__ == "__main__":
    # plot_line()
    # plot_several_lines()
    # plot_bar()
    # plot_diagram()
    plot_3d_surface()
