import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt

"""
Загружаем MNIST

MNIST — это самый известный учебный датасет для машинного обучения.
Он содержит 70 000 изображений рукописных цифр от 0 до 9.

x_train — сами картинки (формат 28×28)
y_train — правильные цифры (0–9)
"""
(x_train, _), _ = tf.keras.datasets.mnist.load_data()
x_train = x_train.astype("float32") / 255.0
x_train = x_train.reshape(-1, 28 * 28)


# Генератор — создаёт изображения
def build_generator():
    model = tf.keras.Sequential(
        [
            layers.Dense(128, activation="relu", input_dim=100),
            layers.Dense(784, activation="sigmoid"),
        ]
    )
    return model


# Дискриминатор — пытается определить, настоящее изображение или фейк.
def build_discriminator():
    model = tf.keras.Sequential(
        [
            layers.Dense(128, activation="relu", input_dim=784),
            layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(optimizer="adam", loss="binary_crossentropy")
    return model


generator = build_generator()
discriminator = build_discriminator()

""""
GAN = генератор + дискриминатор
Sequential — это упрощённый способ собрать модель в Keras, где слои идут один за другим.

В случае GAN мы соединяем две модели в одну: 

- generator — генератор: создаёт «фейковые» изображения из случайного шума.
- discriminator — дискриминатор: пытается отличить настоящие изображения от фейковых.

Что такое GAN?

GAN — это тип нейросети, которая состоит из двух частей:

- Генератор (Generator)
    Создаёт новые данные (например, изображения цифр, лица, музыку) из случайного шума.
    Цель: обмануть дискриминатор, чтобы он думал, что эти данные настоящие.
- Дискриминатор (Discriminator)
    Определяет, являются данные настоящими (из обучающего набора) или фейковыми (сгенерированными генератором).

[Случайный шум] → [Генератор] → [Сгенерированное изображение] → [Дискриминатор] → [Вероятность "настоящее/фейк"]

Для чего используется GAN

- Генерация изображений (цифры, лица, искусственные пейзажи)
- Улучшение качества фото (суперрезолюция)
- Генерация музыки или текста
- Синтетические данные для обучения других моделей

"""
discriminator.trainable = False
gan = tf.keras.Sequential([generator, discriminator])
gan.compile(optimizer="adam", loss="binary_crossentropy")


def train_gan(epochs=3000, batch_size=64):
    """
    Определяем функцию для обучения GAN.
    - epochs=3000 — сколько раз прогоняем весь цикл обучения.
    - batch_size=64 — сколько изображений используем за один шаг обновления модели.
    """
    for epoch in range(epochs):
        # Обучаем дискриминатор

        # берем batch_size случайных настоящих изображений из обучающего датасета x_tra
        real_imgs = x_train[np.random.randint(0, x_train.shape[0], batch_size)]

        # генерируем случайный шум — вектор длины 100 для генератора.
        noise = np.random.normal(0, 1, (batch_size, 100))

        # на его основе генератор создаст "фейковые" изображения.
        fake_imgs = generator.predict(noise, verbose=0)

        """
        Объединяем настоящие и фейковые изображения в одну матрицу x.
        y — метки: 1 для настоящих, 0 для фейковых.
        """
        x = np.vstack([real_imgs, fake_imgs])
        y = np.hstack([np.ones(batch_size), np.zeros(batch_size)])

        # Обучаем дискриминатор
        discriminator.trainable = True
        discriminator.train_on_batch(
            x, y
        )  # train_on_batch обновляет веса только на этом батче, а не на всей эпохе.

        # Обучаем генератор
        # Генератор снова получает случайный шум.
        # Метки y_gen = 1 → мы хотим, чтобы дискриминатор думал, что сгенерированные картинки настоящие.
        noise = np.random.normal(0, 1, (batch_size, 100))
        y_gen = np.ones(batch_size)  # хотим обмануть дискриминатор

        # Выключаем обучение дискриминатора, чтобы обновлялись только веса генератора.
        # GAN (генератор + дискриминатор) обучается так, чтобы обмануть дискриминатор.
        discriminator.trainable = False
        gan.train_on_batch(noise, y_gen)

        # Каждые 500 эпох показываем прогресс
        if epoch % 500 == 0:
            print(f"Epoch {epoch}")
            show_generated(f"Epoch {epoch}")


# Показываем сгенерированную картинку
def show_generated(title):
    noise = np.random.normal(0, 1, (1, 100))
    generated_img = generator.predict(noise, verbose=0)[0].reshape(28, 28)
    plt.imshow(generated_img, cmap="gray")
    plt.title(title)
    plt.show()


# Запуск
train_gan()
