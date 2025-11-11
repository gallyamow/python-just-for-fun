import numpy as np

"""
NumPy (Numerical Python) — библиотека, которая добавляет быстрые массивы (ndarray) и функции для математики, статистики и линейной алгебры.
Почти все библиотеки для Data Science (Pandas, SciPy, scikit-learn, TensorFlow, PyTorch) так построены поверх NumPy.

Преимущества:

* NumPy-операции написаны на C и могут работать в десятки и сотни раз быстрее чем списки
* Многомерные массивы: векторы, матрицы, тензоры
* Векторизация - можно выполнять операции над массивами и столбцами целиком без циклов.

np.array - основной класс.
Перегрузка операторов позволяет записать операции очень ясно.

Особенности массивов:

* содержат элементы заданного типа
* фиксированный форма

Зачем нужен NumPy:

* Машинное обучение: Быстрая работа с матрицами → основа ML.
* Анализ данных: Pandas использует NumPy внутри.
⭐ Компьютерное зрение - Изображение = массив пикселей → NumPy идеален.
⭐ Симуляции, физика, математика: Большие многомерные данные.
"""

# Матрица A
A = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
], dtype=float)

print("Матрица A:\n", A, "\n")

# Определитель
det = np.linalg.det(A)
print("Определитель det(A):", det)

# Ранг
rank = np.linalg.matrix_rank(A)
print("Ранг matrix_rank(A):", rank, "(ожидается 3 для невырожденной матрицы)\n")

# Попытка вычислить обратную матрицу (ожидаем ошибку)
try:
    invA = np.linalg.inv(A)
    print("Обратная матрица inv(A):\n", invA)
except np.linalg.LinAlgError as e:
    print("Ошибка при np.linalg.inv(A):", repr(e), "\n")

# Псевдообратная матрица (Moore-Penrose)
A_pinv = np.linalg.pinv(A)
print("Псевдообратная матрица np.linalg.pinv(A):\n", A_pinv, "\n")

# Проверим свойства: A_pinv @ A и A @ A_pinv
print("A_pinv @ A:\n", A_pinv @ A, "\n")
print("A @ A_pinv:\n", A @ A_pinv, "\n")

# Пример решения системы Ax = b с использованием lstsq (наилучшее решение в смысле МНК)
b = np.array([1, 2, 3], dtype=float)
x_lstsq, residuals, rank_lstsq, s = np.linalg.lstsq(A, b, rcond=None)
print("Решение x = np.linalg.lstsq(A, b):\n", x_lstsq)
print("Residuals:", residuals)
print("rank (lstsq):", rank_lstsq, "\n")

# Проверяем качество решения (Ax_approx)
Ax = A @ x_lstsq
print("Ax_approx:\n", Ax)
print("Отклонение ||Ax - b||:", np.linalg.norm(Ax - b), "\n")

# Регуляризация: добавить маленькое значение к диагонали и взять обратную
eps = 1e-8
A_reg = A + eps * np.eye(A.shape[0])
print("Добавим eps =", eps, "к диагонали и попробуем инвертировать A_reg.")
det_reg = np.linalg.det(A_reg)
print("det(A_reg):", det_reg)
invA_reg = np.linalg.inv(A_reg)
print("inv(A_reg) (пример регуляризации):\n", invA_reg, "\n")

# Демонстрация, что pinv даёт "наилучшее" решение в смысле МНК: x_pinv = A_pinv @ b
x_pinv = A_pinv @ b
print("x_pinv = A_pinv @ b:\n", x_pinv)
print("||A @ x_pinv - b||:", np.linalg.norm(A @ x_pinv - b))

print("\nКраткие рекомендации:")
print("- Для вырожденных/почти-вырожденных матриц используйте np.linalg.pinv или np.linalg.lstsq.")
print("- Для численной устойчивости можно добавить регуляризацию (умножить единичную матрицу на малый eps).")
print("- Всегда проверяйте ранг (np.linalg.matrix_rank) и определитель перед попыткой инверсии.")
