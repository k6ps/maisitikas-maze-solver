#!/usr/bin/python3

import logging
import logging.handlers
import queue
import sys
from ev3.motors import EV3Motors
from ev3.wall_detector import EV3WallDetector
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors
from ev3.gyro import Gyro
from ev3.buttons import EV3Buttons
from ev3.maze_solver import EV3MazeSolver
from maze_solver.curious_maze_solver import CuriousMazeSolver
from maze_solver.maze_solver import FinishDetector, Outputs, NotificationType


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
    # ev3_distance_sensors = EV3UltrasoundDistanceDetectors()
    # ev3_distance_sensors.start()
    # ev3_gyro = Gyro()
    # ev3_gyro.start()
    # motors = EV3Motors(distance_sensors = ev3_distance_sensors, gyro = ev3_gyro)
    # wall_detector = EV3WallDetector(distance_sensors = ev3_distance_sensors)
    # maze_solver = CuriousMazeSolver(
    #     motors=motors, 
    #     wall_detector=wall_detector, 
    #     finish_detector=DummyFinishDetector(), 
    #     outputs=DummyOutputs
    # )
    # ev3_buttons = EV3Buttons()
    # ev3_buttons.start()
    try:
        maze_solver.start()
    except KeyboardInterrupt:
        maze_solver.stop()
        # ev3_gyro.stop()
        # ev3_distance_sensors.stop()
        # ev3_buttons.stop()
        logging.info('maze_solver_ev3_app: stopped')
        for listener in log_message_queue_listeners:
            listener.stop()
