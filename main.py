import asyncio
import curses
import random
import time

from fire_animation import fire
from rocket_animation import animate_spaceship
from space_garbage import fly_garbage
from curses_tools import get_frame_size


TIC_TIMEOUT = 0.1


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, offset_tics, symbol='*'):

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(offset_tics)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)



async def fill_orbit_with_garbage(canvas, column, delay):
    while True:
        garbage_files = ['animations/garbage/duck.txt',
                         'animations/garbage/trash_large.txt',
                         'animations/garbage/trash_small.txt',
                         'animations/garbage/trash_xl.txt']
        frames = read_file(garbage_files)
        garbage_frame = random.choice(frames)
        _, columns_garbage = get_frame_size(garbage_frame)
        column_position = random.randint(0, column - columns_garbage)
        coroutine_garbage = fly_garbage(canvas, column_position, garbage_frame)
        coroutines.append(coroutine_garbage)
        await sleep(delay)


def read_file(file_paths):
    contents = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            contents.append(file.read())
    return contents


def draw(canvas):
    global coroutines
    coroutines = []
    curses.curs_set(0)
    canvas.nodelay(True)
    row, column = canvas.getmaxyx()
    delay_garbage = 15
    star_count = 100
    file_paths = ['animations/rocket_frame_1.txt', 'animations/rocket_frame_2.txt']
    for _ in range(star_count):
        random_row = random.randint(1, row - 2)
        random_column = random.randint(1, column - 2)
        random_symbol = random.choice('+*.:')
        offset_tics = random.randint(5, 20)
        coroutines.append(blink(canvas, random_row, random_column, offset_tics, random_symbol))

    coroutine_shot = fire(canvas, row - 1, column/2 - 1)
    coroutines.append(coroutine_shot)
    frames = read_file(file_paths)
    coroutine_spaceship = animate_spaceship(canvas, row - 1, column, frames)
    coroutines.append(coroutine_spaceship)

    coroutine_garbage_generator = fill_orbit_with_garbage(canvas, column, delay_garbage)
    coroutines.append(coroutine_garbage_generator)

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