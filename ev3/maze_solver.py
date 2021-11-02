import logging
from ev3.motors import EV3Motors
from ev3.wall_detector import EV3WallDetector
from ev3.distance_detectors import EV3DistanceDetectors
from ev3.gyro import Gyro
from ev3.buttons import EV3Buttons
from ev3.simple_worker_thread import SimplePeriodicWorkerThread
from maze_solver.curious_maze_solver import CuriousMazeSolver
from maze_solver.maze_solver import FinishDetector, Outputs, NotificationType


class DummyFinishDetector(FinishDetector):

    def is_finish(self):
        return False


class DummyOutputs(Outputs):

    def notify(self, type: NotificationType, message: str):
        pass


class EV3MazeSolver(SimplePeriodicWorkerThread):

    def __init__(self, logger = None):
        self._logger = logger or logging.getLogger(__name__)
        super().__init__(thread_name = 'EV3MazeSolver')
        self._ev3_distance_sensors = EV3DistanceDetectors()
        self._ev3_distance_sensors.start()
        self._ev3_gyro = Gyro()
        self._ev3_gyro.start()
        self._motors = EV3Motors(distance_sensors = self._ev3_distance_sensors, gyro = self._ev3_gyro)
        self._wall_detector = EV3WallDetector(distance_sensors = self._ev3_distance_sensors)
        self._maze_solver = CuriousMazeSolver(
            motors=self._motors, 
            wall_detector=self._wall_detector, 
            finish_detector=DummyFinishDetector(), 
            outputs=DummyOutputs
        )
        self._ev3_buttons = EV3Buttons()
        self._ev3_buttons.start()
        self._ev3_buttons.add_enter_button_listener(self.start_maze_solving)

    def run(self):
        super().run()
        self._ev3_gyro.stop()
        self._ev3_distance_sensors.stop()
        self._ev3_buttons.stop()

    def perform_cycle(self):
        # Don't do anything, just listen for events.
        pass

    def start_maze_solving(self):
        self._logger.debug('Start event received')
        self._ev3_buttons.remove_enter_button_listener()
        self._maze_solver.start()

    def stop(self):
        self._logger.debug('Stop event received')
        super().stop()
