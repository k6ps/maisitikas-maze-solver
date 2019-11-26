#!/usr/bin/python3

from ev3.motors import EV3Motors
from ev3.wall_detector import EV3WallDetector
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors
from ev3.gyro import Gyro
from maze_solver.curious_maze_solver import CuriousMazeSolver
from maze_solver.maze_solver import FinishDetector, Outputs, NotificationType

class DummyFinishDetector(FinishDetector):

    def is_finish(self):
        return False


class DummyOutputs(Outputs):

    def notify(self, type: NotificationType, message: str):
        pass


if __name__ == "__main__":
    ev3_distance_sensors = EV3UltrasoundDistanceDetectors()
    ev3_distance_sensors.start()
    ev3_gyro = Gyro()
    motors = EV3Motors(distance_sensors = ev3_distance_sensors, gyro = ev3_gyro)
    wall_detector = EV3WallDetector(distance_sensors = ev3_distance_sensors)
    maze_solver = CuriousMazeSolver(
        motors=motors, 
        wall_detector=wall_detector, 
        finish_detector=DummyFinishDetector(), 
        outputs=DummyOutputs
    )
    try:
        maze_solver.start()
    except KeyboardInterrupt:
        ev3_gyro.stop()
        ev3_distance_sensors.stop()
