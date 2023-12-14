import asyncio
import curses
import time

async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(0)
    canvas.border('|', '|', '-', '-', '+', '+', '+', '+')
    coroutines = [
        blink(canvas, 5, 10),
        blink(canvas, 5, 15),
        blink(canvas, 5, 20),
        blink(canvas, 5, 25),
        blink(canvas, 5, 30)
    ]

    while True:
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(1)

if __name__ == '__main__':
    curses.wrapper(draw)