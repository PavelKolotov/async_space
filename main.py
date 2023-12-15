import asyncio
import curses
import random
import time


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


def draw(canvas):
    curses.curs_set(0)
    canvas.border('|', '|', '-', '-', '+', '+', '+', '+')
    y, x = canvas.getmaxyx()
    star_count = 100
    coroutines = []
    for _ in range(star_count):
        coroutines.append(blink(canvas, random.randint(1, y - 2), random.randint(1, x - 2), random.choice('+*.:')))

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