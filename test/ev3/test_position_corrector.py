import logging
import unittest
import sys
import math
from unittest.mock import call, MagicMock, Mock
from test.ev3.ev3dev_test_util import Ev3devTestUtil
Ev3devTestUtil.create_fake_ev3dev2_module()
from ev3.position_corrector import PositionCorrector

class PositionCorrectorTests(unittest.TestCase):

    def setUp(self):
        self._set_up_console_logging()
        self._ev3_motor_pair = MagicMock()
        self._gyro = MagicMock()
        self._test_wheel_diameter_mm = 10
        self._position_corrector = PositionCorrector(
            ev3_motor_pair=self._ev3_motor_pair, 
            ev3_gyro=self._gyro,
            wheel_diameter_mm = self._test_wheel_diameter_mm
        )

    def _set_up_console_logging(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.basicConfig(level=logging.INFO, handlers=[console_handler])
        logging.getLogger('ev3.position_corrector').setLevel(logging.DEBUG)

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
        _distances_before = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 3.0}
        _distances_after = {'left': 3.0, 'right': 3.0, 'front': 5.0}
        self._position_corrector.correct_after_move_forward(_distances_before, 0, _distances_after, 0)
        self._ev3_motor_pair.on_for_rotations.assert_called()
        args, kwargs = self._ev3_motor_pair.on_for_rotations.call_args
        _expected_rotations = 2.0 / (self._test_wheel_diameter_mm / 10 * math.pi)
        self.assertAlmostEqual(_expected_rotations, kwargs.get('rotations'), places=3)

    def test_should_move_backward_when_front_distance_before_move_is_too_small(self):
        _distances_before = {'left': 3.0, 'right': 3.0, 'front': 18.0 + 3.0 - 2.0}
        _distances_after = {'left': 3.0, 'right': 3.0, 'front': 3.0 - 2.0}
        self._position_corrector.correct_after_move_forward(_distances_before, 0, _distances_after, 0)
        self._ev3_motor_pair.on_for_rotations.assert_called()
        args, kwargs = self._ev3_motor_pair.on_for_rotations.call_args
        _expected_rotations = -(2.0 / (self._test_wheel_diameter_mm / 10 * math.pi))
        self.assertAlmostEqual(_expected_rotations, kwargs.get('rotations'), places=3)
