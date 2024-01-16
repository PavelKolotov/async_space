import asyncio
import curses
import random
import time
import itertools


from curses_tools import get_frame_size, draw_frame, read_controls
from fire_animation import fire
from obstacles import show_obstacles
from physics import update_speed
from space_garbage import fly_garbage, obstacles


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


async def animate_spaceship(canvas, row, column, frames):
    cycle = itertools.cycle(frames)
    rows_direction, columns_direction = 0, 0
    row_speed, column_speed = 0, 0

    first_frame = frames[0]
    rows_ships, columns_ships = get_frame_size(first_frame)
    start_row = (row - rows_ships) // 2
    start_column = (column - columns_ships) // 2

    space_pressed = False

    while True:
        frame = next(cycle)

        for _ in range(2):
            rows_ships, columns_ships = get_frame_size(frame)
            row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)

            start_row += row_speed
            start_column += column_speed

            start_row = max(0, min(start_row, row - rows_ships))
            start_column = max(0, min(start_column, column - columns_ships))

            draw_frame(canvas, start_row, start_column, frame)

            if space_pressed:
                coroutine_fire = fire(canvas, start_row, start_column + columns_ships // 2)
                coroutines.append(coroutine_fire)

            await asyncio.sleep(0)

            draw_frame(canvas, start_row, start_column, frame, True)
            rows_direction, columns_direction, space_pressed = read_controls(canvas)


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

    frames = read_file(file_paths)
    coroutine_spaceship = animate_spaceship(canvas, row - 1, column, frames)
    coroutines.append(coroutine_spaceship)

    coroutine_garbage_generator = fill_orbit_with_garbage(canvas, column, delay_garbage)
    coroutines.append(coroutine_garbage_generator)

    show_obstacles_garbage = show_obstacles(canvas, obstacles)
    coroutines.append(show_obstacles_garbage)

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