import logging
import unittest
import sys
import math
from unittest.mock import call, MagicMock, Mock
from test.ev3.ev3dev_test_util import Ev3devTestUtil
Ev3devTestUtil.create_fake_ev3dev2_module()
from ev3.position_corrector import PositionCorrector
from ev3.steering import Steering


class PositionCorrectorTests(unittest.TestCase):

    def setUp(self):
        self._set_up_console_logging()
        self._ev3_motor_pair = MagicMock()
        self._gyro = MagicMock()
        self._distance_sensors = MagicMock()
        self._test_wheel_diameter_mm = 10
        self._test_ideal_side_turn_angle = 90
        self._test_turn_side_bad_angle_max_treshold = 60
        self._test_wheelbase_width_at_centers_mm = 150
        self._position_corrector = PositionCorrector(
            ev3_motor_pair=self._ev3_motor_pair, 
            ev3_gyro=self._gyro,
            ev3_distance_sensors = self._distance_sensors,
            wheel_diameter_mm = self._test_wheel_diameter_mm,
            ideal_side_turn_angle = self._test_ideal_side_turn_angle,
            turn_side_bad_angle_max_treshold = self._test_turn_side_bad_angle_max_treshold,
            wheelbase_width_at_centers_mm = self._test_wheelbase_width_at_centers_mm
        )

    def _set_up_console_logging(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.basicConfig(level=logging.INFO, handlers=[console_handler])
        logging.getLogger('ev3.position_corrector').setLevel(logging.DEBUG)

    def _calculate_expected_rotations_for_robot_turn(self, robot_turn_degrees: int) -> float:
        return (self._test_wheelbase_width_at_centers_mm * robot_turn_degrees) / (self._test_wheel_diameter_mm * 360)

    def _assert_no_corrections_made(self):
        self._ev3_motor_pair.on_for_degrees.assert_not_called()
        self._ev3_motor_pair.on_for_seconds.assert_not_called()
        self._ev3_motor_pair.on_for_rotations.assert_not_called()
        self._ev3_motor_pair.on.assert_not_called()


class MoveForwardCorrectionTests(PositionCorrectorTests):

    def test_should_not_do_anything_when_distances_and_angles_are_correct(self):
        _distances_before = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 3.0}
        _distances_after = {'left': 3.0, 'right': 3.0, 'front': 3.0}
        self._position_corrector.correct_after_move_forward(_distances_before, 0, _distances_after, 0)
        self._assert_no_corrections_made()

    def test_should_move_forward_when_front_distance_after_move_is_too_big(self):
        _distances_before = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 2.0}
        _distances_after = {'left': 3.0, 'right': 3.0, 'front': 5.0}
        self._position_corrector.correct_after_move_forward(_distances_before, 0, _distances_after, 0)
        self._ev3_motor_pair.on_for_rotations.assert_called()
        args, kwargs = self._ev3_motor_pair.on_for_rotations.call_args
        _expected_rotations = 3.0 / (self._test_wheel_diameter_mm / 10 * math.pi)
        self.assertAlmostEqual(_expected_rotations, kwargs.get('rotations'), places=3)

    def test_should_move_backward_when_front_distance_before_move_is_too_small(self):
        _distances_before = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 1.0}
        _distances_after = {'left': 3.0, 'right': 3.0, 'front': 1.0}
        self._position_corrector.correct_after_move_forward(_distances_before, 0, _distances_after, 0)
        self._ev3_motor_pair.on_for_rotations.assert_called()
        args, kwargs = self._ev3_motor_pair.on_for_rotations.call_args
        _expected_rotations = -(1.0 / (self._test_wheel_diameter_mm / 10 * math.pi))
        self.assertAlmostEqual(_expected_rotations, kwargs.get('rotations'), places=3)

    def test_should_move_back_and_correct_turn_back_to_right_when_has_hit_left_wall(self):
        _distances_before = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 3.0}
        _distances_after = {'left': 3.0, 'right': 3.0, 'front': 15.0}
        self._distance_sensors.get_distances.return_value = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 15.0}
        self._gyro.get_orientation.side_effect = [0, 0]
        self._position_corrector.correct_after_move_forward(_distances_before, 0, _distances_after, -45)
        self.assertEqual(3, len(self._ev3_motor_pair.mock_calls))
        name, args, kwargs = self._ev3_motor_pair.on_for_rotations.mock_calls[0]
        _expected_rotations_move_back = -(2.0 / (self._test_wheel_diameter_mm / 10 * math.pi))
        self.assertAlmostEqual(_expected_rotations_move_back, kwargs.get('rotations'), places=3)
        self.assertEqual(Steering.STRAIGHT.value, kwargs.get('steering'))
        name, args, kwargs = self._ev3_motor_pair.on_for_rotations.mock_calls[1]
        _expected_rotations_turn = self._calculate_expected_rotations_for_robot_turn(45)
        self.assertAlmostEqual(_expected_rotations_turn, kwargs.get('rotations'), places=3)
        self.assertEqual(Steering.RIGHT_ON_SPOT.value, kwargs.get('steering'))
        name, args, kwargs = self._ev3_motor_pair.on_for_rotations.mock_calls[2]
        _expected_rotations_move_forward = (15.0 - 2.0) / (self._test_wheel_diameter_mm / 10 * math.pi)
        self.assertAlmostEqual(_expected_rotations_move_forward, kwargs.get('rotations'), places=3)
        self.assertEqual(Steering.STRAIGHT.value, kwargs.get('steering'))

    def test_should_move_back_and_correct_turn_back_to_left_when_has_hit_right_wall(self):
        _distances_before = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 3.0}
        _distances_after = {'left': 3.0, 'right': 3.0, 'front': 15.0}
        self._distance_sensors.get_distances.return_value = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 15.0}
        self._gyro.get_orientation.side_effect = [0, 0]
        self._position_corrector.correct_after_move_forward(_distances_before, 0, _distances_after, 45)
        self.assertEqual(3, len(self._ev3_motor_pair.mock_calls))
        name, args, kwargs = self._ev3_motor_pair.on_for_rotations.mock_calls[0]
        _expected_rotations_move_back = -(2.0 / (self._test_wheel_diameter_mm / 10 * math.pi))
        self.assertAlmostEqual(_expected_rotations_move_back, kwargs.get('rotations'), places=3)
        self.assertEqual(Steering.STRAIGHT.value, kwargs.get('steering'))
        name, args, kwargs = self._ev3_motor_pair.on_for_rotations.mock_calls[1]
        _expected_rotations_turn = self._calculate_expected_rotations_for_robot_turn(45)
        self.assertAlmostEqual(_expected_rotations_turn, kwargs.get('rotations'), places=3)
        self.assertEqual(Steering.LEFT_ON_SPOT.value, kwargs.get('steering'))
        name, args, kwargs = self._ev3_motor_pair.on_for_rotations.mock_calls[2]
        _expected_rotations_move_forward = (15.0 - 2.0) / (self._test_wheel_diameter_mm / 10 * math.pi)
        self.assertAlmostEqual(_expected_rotations_move_forward, kwargs.get('rotations'), places=3)
        self.assertEqual(Steering.STRAIGHT.value, kwargs.get('steering'))


class TurnLeftCorrectionTests(PositionCorrectorTests):

    def test_should_correct_turn_when_turned_too_little(self):
        _distances_before = {'left': 18.0 + 3.0, 'right': 3.0, 'front': 3.0}
        _distances_after = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 3.0}
        self._position_corrector.correct_after_turn_left(_distances_before, 0, _distances_after, -45)
        print(self._ev3_motor_pair.mock_calls)
        self._ev3_motor_pair.on_for_rotations.assert_called()
        args, kwargs = self._ev3_motor_pair.on_for_rotations.call_args
        _expected_rotations = self._calculate_expected_rotations_for_robot_turn(45)
        self.assertAlmostEqual(_expected_rotations, kwargs.get('rotations'), places=3)
        self.assertEqual(Steering.LEFT_ON_SPOT.value, kwargs.get('steering'))


class TurnRightCorrectionTests(PositionCorrectorTests):

    def test_should_correct_turn_when_turned_too_little(self):
        _distances_before = {'left': 3.0, 'right': 18.0 + 3.0, 'front': 3.0}
        _distances_after = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 3.0}
        self._position_corrector.correct_after_turn_right(_distances_before, 0, _distances_after, 45)
        print(self._ev3_motor_pair.mock_calls)
        self._ev3_motor_pair.on_for_rotations.assert_called()
        args, kwargs = self._ev3_motor_pair.on_for_rotations.call_args
        _expected_rotations = self._calculate_expected_rotations_for_robot_turn(45)
        self.assertAlmostEqual(_expected_rotations, kwargs.get('rotations'), places=3)
        self.assertEqual(Steering.RIGHT_ON_SPOT.value, kwargs.get('steering'))
