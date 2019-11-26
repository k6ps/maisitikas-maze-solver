from enum import Enum
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors


class Correction(Enum):
    LEFT = -1
    RIGHT = 1
    NONE = 0


class SteeringCorrector(object):

    def __init__(self, distance_sensors: EV3UltrasoundDistanceDetectors, **kwargs) -> Correction:
        self._distance_sensors = distance_sensors
        self._last_left_distances_queue = []
        self._last_right_distances_queue = []
        self._MAX_LAST_DISTANCES_QUEUE_LENGTH = 20
        self._correct_counts = self._get_kwarg_or_default(2, 'correct_counts', **kwargs)
        self._correct_back_later_counts = self._get_kwarg_or_default(10, 'correct_back_later_counts', **kwargs)
        self._side_distance_difference_tolerance_cm = self._get_kwarg_or_default(0.8, 'side_distance_difference_tolerance_cm', **kwargs)
        self._side_distance_difference_tolerance_count = self._get_kwarg_or_default(4, 'side_distance_difference_tolerance_count', **kwargs)
        self._counter = 0
        self._correct_back_left_counter = 0
        self._correct_back_right_counter = 0
        self._correct_left_counter_start = 0
        self._correct_right_counter_start = 0
        self._correct_left_counter_end = 0
        self._correct_right_counter_end = 0

    def _get_kwarg_or_default(self, default_value, param_key: str, **kwargs):
        if kwargs is None or param_key not in kwargs: 
            return default_value
        else:
            return kwargs[param_key]

    def _add_distance_to_queue(self, queue: list, distance: float):
        queue.append(distance)
        if len(queue) > self._MAX_LAST_DISTANCES_QUEUE_LENGTH:
            queue.pop(0)

    def _add_left_distance_to_queue(self, distance: float):
        self._add_distance_to_queue(self._last_left_distances_queue, distance)

    def _add_right_distance_to_queue(self, distance: float):
        self._add_distance_to_queue(self._last_right_distances_queue, distance)

    def _not_enough_data_in_distance_queues(self) -> bool:
        return len(self._last_right_distances_queue) < self._side_distance_difference_tolerance_count or len(self._last_right_distances_queue) < self._side_distance_difference_tolerance_count

    def _last_n_left_distances_less_than_right_distances(self) -> bool:
        if self._not_enough_data_in_distance_queues():
            return False
        result = True
        for i in range(1, self._side_distance_difference_tolerance_count + 1):
            result = result and ((self._last_right_distances_queue[-i] - self._last_left_distances_queue[-i]) > self._side_distance_difference_tolerance_cm)
        return result

    def _last_n_right_distances_less_than_left_distances(self) -> bool:
        if self._not_enough_data_in_distance_queues():
            return False
        result = True
        for i in range(1, self._side_distance_difference_tolerance_count + 1):
            result = result and ((self._last_left_distances_queue[-i] - self._last_right_distances_queue[-i]) > self._side_distance_difference_tolerance_cm)
        return result

    def _empty_distance_queues(self):
        self._last_left_distances_queue.clear()
        self._last_right_distances_queue.clear()

    def _not_waiting_for_correction_back(self):
        return self._correct_back_left_counter == 0 and self._correct_back_right_counter == 0

    def _start_correct_to_left(self):
        self._empty_distance_queues()
        self._correct_left_counter_start = self._counter
        self._correct_left_counter_end = self._correct_left_counter_start + self._correct_counts - 1
        return Correction.LEFT

    def _start_correct_to_right(self):
        self._empty_distance_queues()
        self._correct_right_counter_start = self._counter
        self._correct_right_counter_end = self._correct_right_counter_start + self._correct_counts - 1
        return Correction.RIGHT

    def get_side_corrections_needed(self):
        self._counter += 1
        _distances = self._distance_sensors.get_distances()
        _left_distance = _distances['left']
        _right_distance = _distances['right']
        print('DEBUG - SteeringCorrector: left={}, right={}'.format(_left_distance, _right_distance))
        self._add_left_distance_to_queue(_left_distance)
        self._add_right_distance_to_queue(_right_distance)
        if self._counter >= self._correct_left_counter_start and self._counter <= self._correct_left_counter_end:
            print('DEBUG - SteeringCorrector: continuing to correct left')
            return Correction.LEFT
        elif self._counter >= self._correct_right_counter_start and self._counter <= self._correct_right_counter_end:
            print('DEBUG - SteeringCorrector: continuing to correct right')
            return Correction.RIGHT
        elif self._correct_back_left_counter == self._counter:
            print('DEBUG - SteeringCorrector: correcting back to left')
            self._correct_back_left_counter = 0
            return self._start_correct_to_left()
        elif self._correct_back_right_counter == self._counter:
            print('DEBUG - SteeringCorrector: correcting back to right')
            self._correct_back_right_counter = 0
            return self._start_correct_to_right()
        elif self._last_n_left_distances_less_than_right_distances() and self._not_waiting_for_correction_back():
            print('DEBUG - SteeringCorrector: correcting to right')
            self._correct_back_left_counter = self._counter + self._correct_back_later_counts
            return self._start_correct_to_right()
        elif self._last_n_right_distances_less_than_left_distances() and self._not_waiting_for_correction_back():
            print('DEBUG - SteeringCorrector: correcting to left')
            self._correct_back_right_counter = self._counter + self._correct_back_later_counts
            return self._start_correct_to_left()
        else:
            # print('DEBUG - SteeringCorrector: no correction needed')
            self._correct_left_counter_start = 0
            self._correct_right_counter_start = 0
            self._correct_left_counter_end = 0
            self._correct_right_counter_end = 0
            return Correction.NONE
