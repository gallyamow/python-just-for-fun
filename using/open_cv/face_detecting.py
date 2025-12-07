import cv2

"""
Работает на основе предварительно обученная модели (Pre-trained-model) - haarcascade_frontalface_default.

Файлы Haar Cascade, например haarcascade_frontalface_default.xml, представляют собой XML-файлы, которые 
содержат структурированное описание обученного каскада признаков. Они не содержат изображения, а описывают шаблоны 
 и правила для обнаружения объектов.
 
Основные элементы:

<size> – размер окна, с которым работает каскад (обычно 24x24 пикселя для лиц).
<stages> – последовательность «ступеней» (каскад), каждая из которых проверяет признаки.
<weakClassifiers> – «слабые» классификаторы (решают простую задачу, вместе дают точный результат).
<features> – признаки Хаара (прямоугольные шаблоны с весами), по которым происходит детекция.

Ещё нагляднее можно показать прямоугольный шаблон:
<rects>
  <_>1 2 3 4 -1.</_>
  <_>2 3 4 5 1.</_>
</rects>
Каждая строка <_> — один прямоугольник.
Первые 4 числа — координаты: x, y, ширина, высота.
Последнее число — вес прямоугольника (положительный или отрицательный).

Когда OpenCV проверяет лицо, оно суммирует все веса по этим прямоугольникам и сравнивает с порогом. Если проходит — 
каскад идёт дальше, если нет — окно отбрасывается.
"""

# Загружаем классификатор лица (входит в состав OpenCV)
# (файл /Users/ramil/Projects/python-just-for-fun/venv/lib/python3.13/site-packages/cv2/data/haarcascade_frontalface_default.xml)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
# Открываем веб-камеру
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Переводим в ч/б — так быстрее работает
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Поиск лиц
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Рисуем прямоугольники вокруг лиц
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Показываем результат
    cv2.imshow("Face detection", frame)

    # Нажмите «q» для выхода
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()
