import asyncio
import itertools


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def animate_spaceship(canvas, start_row, start_column, frames):
    cycle = itertools.cycle(frames)

    while True:
        frame = next(cycle)
        rows_ships, columns_ships = get_frame_size(frame)
        ship_y = round(start_row/2) - round(rows_ships/2)
        ship_x = round(start_column/2) - round(columns_ships/2)
        draw_frame(canvas, ship_y, ship_x, frame)
        canvas.refresh()

        for x in range(3):
            await asyncio.sleep(0)

        draw_frame(canvas, ship_y, ship_x, frame, True)