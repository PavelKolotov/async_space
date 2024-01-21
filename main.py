import asyncio
import curses
import itertools
import random
import time
import threading


from curses_tools import get_frame_size, draw_frame, read_controls
from obstacles import show_obstacles
from physics import update_speed
from space_garbage import fly_garbage, obstacles, obstacles_in_last_collisions


TIC_TIMEOUT = 0.1
PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}

game_over_condition_met = False
year = 1957


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


async def increment_year(tic):
    global year
    while True:
        await sleep(tic)
        year += 1


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def show_year(canvas, rows, columns):
    phrase = ''
    height, width, begin_y, begin_x = 2, 70, rows - 2, columns // 2
    derwin_window = canvas.derwin(height, width, begin_y, begin_x)
    while True:
        if year in PHRASES:
            phrase = PHRASES[year]
        derwin_window.clear()
        derwin_window.addstr(1, 1, f'Year {year}: {phrase}')
        derwin_window.refresh()
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


async def fill_orbit_with_garbage(canvas, column):
    while True:
        delay = get_garbage_delay_tics(year)
        if delay is None:
            await asyncio.sleep(0)
        else:
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
    global game_over_condition_met
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

            if space_pressed and year >= 2020:
                coroutine_fire = fire(canvas, start_row, start_column + columns_ships // 2)
                coroutines.append(coroutine_fire)

            draw_frame(canvas, start_row, start_column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, start_row, start_column, frame, True)

            for obstacle in obstacles:
                if obstacle.has_collision(start_row, start_column + columns_ships // 2):
                    game_over_condition_met = True
                    return

            rows_direction, columns_direction, space_pressed = read_controls(canvas)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(round(row), round(column)):
                obstacles_in_last_collisions.append(obstacle)
                return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def show_gameover(canvas, rows, columns):
    gameover_file = ['animations/gameover_frame.txt', ]
    frame = read_file(gameover_file)
    gameover_frame = frame[0]
    rows_gameover, columns_gameover = get_frame_size(gameover_frame)
    column_position = columns // 2 - columns_gameover // 2
    rows_position = rows // 2 - rows_gameover // 2
    while True:
        if game_over_condition_met:
            draw_frame(canvas, rows_position, column_position, gameover_frame)
            await asyncio.sleep(0)
        else:
            await asyncio.sleep(0)


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
    star_count = 100
    file_paths = ['animations/rocket_frame_1.txt', 'animations/rocket_frame_2.txt']

    coroutines.append(increment_year(15))

    for _ in range(star_count):
        random_row = random.randint(1, row - 2)
        random_column = random.randint(1, column - 2)
        random_symbol = random.choice('+*.:')
        offset_tics = random.randint(5, 20)
        coroutines.append(blink(canvas, random_row, random_column, offset_tics, random_symbol))

    frames = read_file(file_paths)
    coroutine_spaceship = animate_spaceship(canvas, row - 1, column, frames)
    coroutines.append(coroutine_spaceship)

    coroutine_garbage_generator = fill_orbit_with_garbage(canvas, column)
    coroutines.append(coroutine_garbage_generator)

    coroutine_gameover_generator = show_gameover(canvas, row, column)
    coroutines.append(coroutine_gameover_generator)

    show_obstacles_garbage = show_obstacles(canvas, obstacles)
    coroutines.append(show_obstacles_garbage)

    coroutine_show_year = show_year(canvas, row, column)
    coroutines.append(coroutine_show_year)

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
