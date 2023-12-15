import asyncio
import curses
import time


TIC_TIMEOUT = 0.1

async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for x in range(20):
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
        time.sleep(TIC_TIMEOUT)

if __name__ == '__main__':
    curses.wrapper(draw)