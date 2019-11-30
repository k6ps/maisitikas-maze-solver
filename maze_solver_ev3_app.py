#!/usr/bin/python3

import logging
import logging.handlers
import queue
import sys
from ev3.maze_solver import EV3MazeSolver


def set_up_async_file_logging() -> list:
    console_log_message_queue = queue.Queue(-1)
    file_log_message_queue = queue.Queue(-1)
    console_queue_handler = logging.handlers.QueueHandler(console_log_message_queue)
    file_queue_handler = logging.handlers.QueueHandler(file_log_message_queue)
    file_handler = logging.FileHandler(filename='logs/ev3_maze_solver.log')
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    console_log_message_queue_listener = logging.handlers.QueueListener(console_log_message_queue, console_handler)
    file_log_message_queue_listener = logging.handlers.QueueListener(file_log_message_queue, file_handler)
    logging.basicConfig(level=logging.INFO, handlers=[console_queue_handler, file_queue_handler])
    logging.getLogger('ev3.position_corrector').setLevel(logging.DEBUG)
    logging.getLogger('ev3.wall_detector').setLevel(logging.DEBUG)
    return [console_log_message_queue_listener, file_log_message_queue_listener]


if __name__ == "__main__":
    log_message_queue_listeners = set_up_async_file_logging()
    for listener in log_message_queue_listeners:
        listener.start()
    logging.info('maze_solver_ev3_app: starting')
    maze_solver = EV3MazeSolver()
    try:
        maze_solver.start()
    except KeyboardInterrupt:
        maze_solver.stop()
        logging.info('maze_solver_ev3_app: stopped')
        for listener in log_message_queue_listeners:
            listener.stop()
