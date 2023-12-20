import asyncio
import curses
import random
import time

from fire_animation import fire
from rocket_animation import animate_spaceship


TIC_TIMEOUT = 0.1

async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for x in range(random.randint(5, 20)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for x in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for x in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for x in range(3):
            await asyncio.sleep(0)

def read_file(file_paths):
    contents = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            contents.append(file.read())
    return contents


def draw(canvas):
    curses.curs_set(0)
    canvas.nodelay(True)
    y, x = canvas.getmaxyx()
    start_row = y // 2
    start_column = x // 2
    star_count = 100
    file_paths = ['animations/rocket_frame_1.txt', 'animations/rocket_frame_2.txt']
    coroutines = []
    for _ in range(star_count):
        coroutines.append(blink(canvas, random.randint(1, y - 2), random.randint(1, x - 2), random.choice('+*.:')))
    # coroutine_shot = fire(canvas, y - 1, x/2)
    # coroutines.append(coroutine_shot)
    frames = read_file(file_paths)
    coroutine_spaceship = animate_spaceship(canvas, start_row - 1, start_column, frames)
    coroutines.append(coroutine_spaceship)

    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':

    curses.wrapper(draw)