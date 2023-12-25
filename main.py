import asyncio
import curses
import random
import time

from fire_animation import fire
from rocket_animation import animate_spaceship


TIC_TIMEOUT = 0.1

async def blink(canvas, row, column, offset_tics, symbol='*'):

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(offset_tics):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
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
    row, column = canvas.getmaxyx()
    star_count = 100
    file_paths = ['animations/rocket_frame_1.txt', 'animations/rocket_frame_2.txt']
    coroutines = []
    for _ in range(star_count):
        offset_tics = random.randint(5, 20)
        coroutines.append(blink(canvas, random.randint(1, row - 2), random.randint(1, column - 2), offset_tics, random.choice('+*.:')))
    coroutine_shot = fire(canvas, row - 1, column/2)
    coroutines.append(coroutine_shot)
    frames = read_file(file_paths)
    coroutine_spaceship = animate_spaceship(canvas, row - 1, column, frames)
    coroutines.append(coroutine_spaceship)

    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.wrapper(draw)