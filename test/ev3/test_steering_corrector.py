import unittest
from unittest.mock import call, MagicMock, Mock
from test.ev3.ev3dev_test_util import Ev3devTestUtil
Ev3devTestUtil.create_fake_ev3dev2_module()
from ev3.steering_corrector import SteeringCorrector, Correction

# TODO: Remove, replaced by PositionCorrector


class SteeringCorrectorTest(unittest.TestCase):

    def setUp(self):
        self._mock_distance_sensors = MagicMock()
        self._steering_corrector = SteeringCorrector(
            distance_sensors=self._mock_distance_sensors,
            side_distance_difference_tolerance_count=7,
            correct_back_later_counts=5,
            side_distance_difference_tolerance_cm=1.5
        )

    def _check_correction_n_times(self, n: int):
        for _ in range(n):
            self._steering_corrector.get_side_corrections_needed()

    def test_should_return_no_correction_needed_when_asked_for_first_time_with_both_sides_equal(self):
        self._mock_distance_sensors.get_distances.side_effect = [{'left': 3.0, 'right': 3.0, 'front': 18.0}]
        _corrections = self._steering_corrector.get_side_corrections_needed()
        self.assertEqual(Correction.NONE, _corrections)

    def test_should_return_no_correction_needed_when_both_sides_are_equal_for_several_times(self):
        self._mock_distance_sensors.get_distances.side_effect = [
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0}
        ]
        self._check_correction_n_times(14)
        _corrections = self._steering_corrector.get_side_corrections_needed()
        self.assertEqual(Correction.NONE, _corrections)

    def test_should_return_correction_to_left_when_right_is_less_than_left_for_distance_diff_tolerance_times(self):
        self._mock_distance_sensors.get_distances.side_effect = [
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0}
         ]
        self._check_correction_n_times(14)
        _corrections = self._steering_corrector.get_side_corrections_needed()
        self.assertEqual(Correction.LEFT, _corrections)

    def test_should_return_no_correction_when_right_is_less_than_left_for_less_than_tolerance(self):
        self._mock_distance_sensors.get_distances.side_effect = [
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.5, 'right': 2.5, 'front': 18.0},
            {'left': 3.5, 'right': 2.5, 'front': 18.0},
            {'left': 3.5, 'right': 2.5, 'front': 18.0},
            {'left': 3.5, 'right': 2.5, 'front': 18.0},
            {'left': 3.5, 'right': 2.5, 'front': 18.0},
            {'left': 3.5, 'right': 2.5, 'front': 18.0},
            {'left': 3.5, 'right': 2.5, 'front': 18.0}
         ]
        self._check_correction_n_times(14)
        _corrections = self._steering_corrector.get_side_corrections_needed()
        self.assertEqual(Correction.NONE, _corrections)

    def test_should_return_no_correction_when_left_is_less_than_right_for_less_than_tolerance(self):
        self._mock_distance_sensors.get_distances.side_effect = [
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 2.5, 'right': 3.5, 'front': 18.0},
            {'left': 2.5, 'right': 3.5, 'front': 18.0},
            {'left': 2.5, 'right': 3.5, 'front': 18.0},
            {'left': 2.5, 'right': 3.5, 'front': 18.0},
            {'left': 2.5, 'right': 3.5, 'front': 18.0},
            {'left': 2.5, 'right': 3.5, 'front': 18.0},
            {'left': 2.5, 'right': 3.5, 'front': 18.0}
         ]
        self._check_correction_n_times(14)
        _corrections = self._steering_corrector.get_side_corrections_needed()
        self.assertEqual(Correction.NONE, _corrections)

    def test_should_return_correction_to_right_when_left_is_less_than_right_for_distance_diff_tolerance_times(self):
        self._mock_distance_sensors.get_distances.side_effect = [
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0}
         ]
        self._check_correction_n_times(14)
        _corrections = self._steering_corrector.get_side_corrections_needed()
        self.assertEqual(Correction.RIGHT, _corrections)

    def test_should_return_correction_to_right_when_back_from_left_correction(self):
        self._mock_distance_sensors.get_distances.side_effect = [
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0},
            {'left': 4.0, 'right': 2.0, 'front': 18.0}
         ]
        self._check_correction_n_times(14)
        _corrections = self._steering_corrector.get_side_corrections_needed()
        self.assertEqual(Correction.RIGHT, _corrections)

    def test_should_return_correction_to_left_when_back_from_right_correction(self):
        self._mock_distance_sensors.get_distances.side_effect = [
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 3.0, 'right': 3.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0},
            {'left': 2.0, 'right': 4.0, 'front': 18.0}
         ]
        self._check_correction_n_times(14)
        _corrections = self._steering_corrector.get_side_corrections_needed()
        self.assertEqual(Correction.LEFT, _corrections)
