import asyncio
import itertools

from curses_tools import get_frame_size, draw_frame, read_controls


async def animate_spaceship(canvas, row, column, frames):
    cycle = itertools.cycle(frames)
    rows_direction, columns_direction = 0, 0
    first_frame = frames[0]
    rows_ships, columns_ships = get_frame_size(first_frame)
    start_row = (row - rows_ships) // 2
    start_column = (column - columns_ships) // 2

    while True:
        frame = next(cycle)

        for _ in range(2):
            rows_ships, columns_ships = get_frame_size(frame)

            start_row += rows_direction
            start_column += columns_direction

            start_row = max(0, min(start_row, row - rows_ships))
            start_column = max(0, min(start_column, column - columns_ships))

            draw_frame(canvas, start_row, start_column, frame)

            await asyncio.sleep(0)

            draw_frame(canvas, start_row, start_column, frame, True)
            rows_direction, columns_direction, space_pressed = read_controls(canvas)