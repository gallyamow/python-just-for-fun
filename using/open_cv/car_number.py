import cv2
import pytesseract
import imutils

"""
OpenCV — это библиотека компьютерного зрения и обработки изображений.

Что умеет OpenCV:
- Предварительная обработка изображений (фильтры, изменение размера, повороты, обрезка, сглаживание)
- Обнаружение объектов (лица, глаза, автомобили, люди, жесты, контуры)
- Распознавание изображений (классификация с использованием моделей машинного обучения)
- Работа с видео (захват с камеры, отслеживание движения, кадрирование)
- Калибровка камер и 3D-реконструкция(работа с несколькими камерами, восстановление глубины)
- Создание эффектов в реальном времени (фильтры как в Instagram, AR-эффекты)

Библиотека может визуализировать результат в отдельных окнах и работать с клавиатурой (используя HighGUI => GUI системы).
"""

source = cv2.imread("car.jpg")
if source is None:
    print("Failed to open image")
    exit()

source = imutils.resize(source, width=600)
cv2.imshow("Source", source)

"""
Подготовка:
- Перевод в grayscale
- Нормализация контраста
"""
prepared = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
prepared = cv2.bilateralFilter(prepared, 11, 17, 17)
cv2.imshow("Prepared", prepared)

"""
Поиск границ на изображении с помощью алгоритма Canny Edge Detection:
- Сначала изображение размывается (обычно GaussianBlur), чтобы убрать шум.
- Находит градиенты яркости по x и y с помощью оператора Собеля.
- Применяет немаксимальное подавление — оставляет только пиксели, где граница максимальна.
- Применяет гистерезис — оставляет только те границы, где интенсивность между threshold1 и threshold2.
"""
edges = cv2.Canny(prepared, 30, 200)
cv2.imshow("Edges", edges)

"""
cv2.findContours - для поиска контуров на бинарном изображении (например, после применения cv2.Canny.
"""
cnts, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

contoured = cv2.drawContours(source.copy(), cnts, -1, (0, 255, 0), 2)
cv2.imshow("Contoured", contoured)

# Ищем прямоугольный контур (номер)
plate_contour = None
for c in cnts:
    """
    cv2.arcLength — вычисляет периметр (длину) контура.
    Параметры:
    - c — один контур из списка cnts.
    - True — контур замкнутый (контур замкнутый, а не открытая линия).
    """
    peri = cv2.arcLength(c, True)

    """
    cv2.approxPolyDP — аппроксимация контура (сокращает число точек, упрощает контур).
    Параметры:
    - c — исходный контур.
    - 0.018 * peri — точность аппроксимации (чем меньше, тем точнее контур повторяет исходный).
    - True — контур замкнутый.
    Результат: approx — массив точек, описывающих упрощённый контур.
    """
    approx = cv2.approxPolyDP(c, 0.018 * peri, True)

    """
    Идея: прямоугольник (номер авто) будет иметь 4 угла, поэтому после аппроксимации контур должен состоять из 4 точек.
    """
    if len(approx) == 4:
        plate_contour = approx
        break

# Маска под номер
masked = cv2.drawContours(source.copy(), [plate_contour], -1, (0, 0, 255), 3)
cv2.imshow("Masked", masked)

# Вырезаем прямоугольник с номером
x, y, w, h = cv2.boundingRect(plate_contour)
cut = prepared[y : y + h, x : x + w]

cv2.imshow("Cut", cut)

"""
pytesseract.image_to_string - распознавание текста на изображении с номером с помощью Tesseract OCR.
Параметры:
 - masked — это изображение, где выделена область с номером автомобиля (например, после cv2.drawContours и вырезания прямоугольника).
 - config='--psm 8' — конфигурация Tesseract: --psm (Page Segmentation Mode) управляет способом сегментации текста. 
   8 означает: «одна строка текста». Идеально для автомобильных номеров, потому что они находятся в одной линии.
"""
text = pytesseract.image_to_string(cut, config="--psm 8")
print("Распознанный номер:", text)

cv2.waitKey(0)
cv2.destroyAllWindows()
