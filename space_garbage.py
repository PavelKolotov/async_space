import asyncio

from curses_tools import draw_frame, get_frame_size
from obstacles import Obstacle


obstacles = []
obstacles_in_last_collisions = []


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    global obstacles
    global obstacles_in_last_collisions

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    rows_garbage, columns_garbage = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, rows_garbage, columns_garbage)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            if obstacle in obstacles_in_last_collisions:
                return
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row = row
    finally:
        obstacles.remove(obstacle)

