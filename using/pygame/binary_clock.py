import pygame
import sys
import time

WIDTH, HEIGHT = 480, 200

COLOR_BACKGROUND = (0, 0, 0)
COLOR_FILL = (0, 255, 0)
OFF_COLOR = (50, 50, 50)

CIRCLE_RADIUS = 15
CIRCLE_PADDING = 10

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Binary clock")

font = pygame.font.SysFont(None, 30)  # None = системный шрифт, 14 = размер


def draw_circle(number, x, y):
    for bi in range(4):  # max 4 бита
        bit = (number >> bi) & 1
        color = COLOR_FILL if bit else OFF_COLOR
        zi = 4 - bi - 1
        pygame.draw.circle(
            screen,
            color,
            (x, y + zi * (CIRCLE_RADIUS * 2 + CIRCLE_PADDING)),
            CIRCLE_RADIUS,
        )


def loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        t = time.localtime()
        hour = t.tm_hour
        minute = t.tm_min
        second = t.tm_sec

        # заливать надо в цикле
        screen.fill(COLOR_BACKGROUND)

        # параметры нельзя передавать как kwargs, даже если сигнатура позволяет, так как это обертка над C
        text = font.render(time.strftime("%H:%M:%S", t), True, COLOR_FILL)
        text_rect = text.get_rect(center=(WIDTH // 2, 16))  # позиция текста
        screen.blit(text, text_rect)

        for i, h in enumerate([hour // 10, hour % 10]):
            draw_circle(h, 50 + i * 60, 50)

        for i, m in enumerate([minute // 10, minute % 10]):
            draw_circle(m, 200 + i * 60, 50)

        for i, s in enumerate([second // 10, second % 10]):
            draw_circle(s, 350 + i * 60, 50)

        # Все эти изменения происходят в памяти, на так называемом back buffer (задний буфер), а пользователь этого сразу не видит.
        # pygame.display.flip() - копирует содержимое back buffer на видимый экран (front buffer).
        pygame.display.flip()
        pygame.time.delay(1000)


if __name__ == "__main__":
    loop()
