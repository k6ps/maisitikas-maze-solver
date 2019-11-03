from maze_solver.maze_solver import Motors, FinishDetector, WallDetector, Outputs, NotificationType

class SimulatorMotors(Motors):
    
    def __init__(self, move_forward_callback, turn_right_callback, turn_left_callback, no_turn_callback):
        self._move_forward_callback = move_forward_callback
        self._turn_right_callback = turn_right_callback
        self._turn_left_callback = turn_left_callback
        self._no_turn_callback = no_turn_callback

    def move_forward(self):
        self._move_forward_callback()

    def turn_right(self):
        self._turn_right_callback()

    def turn_left(self):
        self._turn_left_callback()

    def no_turn(self):
        self._no_turn_callback()


class SimulatorFinishDetector(FinishDetector):

    def __init__(self, is_finish_callback):
        self._is_finish_callback = is_finish_callback

    def is_finish(self) -> bool:
        return self._is_finish_callback()


class SimulatorWallDetector(WallDetector):

    def __init__(self, is_left_blocked_callback, is_front_blocked_callback, is_right_blocked_callback):
        self._is_left_blocked_callback = is_left_blocked_callback
        self._is_front_blocked_callback = is_front_blocked_callback
        self._is_right_blocked_callback = is_right_blocked_callback

    def is_left_blocked(self) -> bool:
        return self._is_left_blocked_callback()
    
    def is_front_blocked(self) -> bool:
        return self._is_front_blocked_callback()
    
    def is_right_blocked(self) -> bool:
        return self._is_right_blocked_callback()


class SimulatorOutputs(Outputs):

    def __init__(self, notify_callback):
        self._notify_callback = notify_callback

    def notify(self, type: NotificationType, message: str):
        self._notify_callback(type, message)
