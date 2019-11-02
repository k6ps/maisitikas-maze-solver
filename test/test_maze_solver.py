import unittest
from unittest.mock import call, MagicMock, Mock
from maze_solver.maze_solver import MazeSolver, Motors

class MazeSolverTest(unittest.TestCase):

    def assert_wall_detector_calls_in_any_order(self, wall_detector_mock, actual_calls):
        _expected_calls = [
            wall_detector_mock.is_left_blocked(),
            wall_detector_mock.is_front_blocked(),
            wall_detector_mock.is_right_blocked()
        ]
        self.assertEqual(3, len(actual_calls))
        for _expected_call in _expected_calls:
            self.assertTrue(_expected_call in actual_calls, 'Call {} not found!'.format(_expected_call))

    def setUp(self):
        self._motors = MagicMock()
        self._wall_detector = MagicMock()
        self._maze_solver = MazeSolver(self._motors, self._wall_detector)

    def test_should_check_walls_when_performing_next_move(self):
        self._wall_detector.is_left_blocked.return_value = True
        self._wall_detector.is_front_blocked.return_value = False
        self._wall_detector.is_right_blocked.return_value = True

        self._maze_solver.next_move()

        self._wall_detector.is_left_blocked.assert_called()
        self._wall_detector.is_front_blocked.assert_called()
        self._wall_detector.is_right_blocked.assert_called()

    def test_should_make_no_turn_and_move_forward_when_sides_are_blocked_and_front_is_not(self):
        self._wall_detector.is_left_blocked.return_value = True
        self._wall_detector.is_front_blocked.return_value = False
        self._wall_detector.is_right_blocked.return_value = True
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        self._maze_solver.next_move()

        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
        self.assertEqual(call.the_mock_motors.no_turn(), manager.mock_calls[3])
        self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])

    def test_should_turn_right_and_move_forward_when_only_right_side_is_unblocked(self):
        self._wall_detector.is_left_blocked.return_value = True
        self._wall_detector.is_front_blocked.return_value = True
        self._wall_detector.is_right_blocked.return_value = False
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        self._maze_solver.next_move()

        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
        self.assertEqual(call.the_mock_motors.turn_right(), manager.mock_calls[3])
        self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])

    def test_should_turn_left_and_move_forward_when_only_left_side_is_unblocked(self):
        self._wall_detector.is_left_blocked.return_value = False
        self._wall_detector.is_front_blocked.return_value = True
        self._wall_detector.is_right_blocked.return_value = True
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        self._maze_solver.next_move()

        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
        self.assertEqual(call.the_mock_motors.turn_left(), manager.mock_calls[3])
        self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])

    def test_should_turn_randomly_either_left_or_right_and_move_forward_when_only_front_is_blocked(self):
        self._wall_detector.is_left_blocked.return_value = False
        self._wall_detector.is_front_blocked.return_value = True
        self._wall_detector.is_right_blocked.return_value = False

        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _left_turns = 0
        _right_turns = 0
        for x in range(20):
            manager.reset_mock()

            self._maze_solver.next_move()

            self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
            self.assertTrue(
                manager.mock_calls[3] in [call.the_mock_motors.turn_right(), call.the_mock_motors.turn_left()],
                'Call {} is not one of the expected calls!'.format(manager.mock_calls[3])
            )
            if str(manager.mock_calls[3]) == 'call.the_mock_motors.turn_right()':
                _right_turns += 1
            elif str(manager.mock_calls[3]) == 'call.the_mock_motors.turn_left()':
                _left_turns += 1
            self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])
        self.assertTrue(_left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_right_turns > 3, 'Too few right turns made!')

    def test_should_turn_randomly_either_left_or_right_and_check_again_when_all_sides_are_blocked(self):
        self._wall_detector.is_left_blocked.return_value = True
        self._wall_detector.is_front_blocked.return_value = True
        self._wall_detector.is_right_blocked.return_value = True

        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _left_turns = 0
        _right_turns = 0
        for x in range(20):
            manager.reset_mock()

            try:
                self._maze_solver.next_move()
            except:
                # For this test, ignore the "cannot move" or any other exeption
                pass

            self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
            self.assertTrue(
                manager.mock_calls[3] in [call.the_mock_motors.turn_right(), call.the_mock_motors.turn_left()],
                'Call {} is not one of the expected calls!'.format(manager.mock_calls[3])
            )
            if str(manager.mock_calls[3]) == 'call.the_mock_motors.turn_right()':
                _right_turns += 1
            elif str(manager.mock_calls[3]) == 'call.the_mock_motors.turn_left()':
                _left_turns += 1
            self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[4:7])
        self.assertTrue(_left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_right_turns > 3, 'Too few right turns made!')

    def test_should_turn_randomly_either_left_or_make_no_turn_and_move_forward_when_only_right_is_blocked(self):
        self._wall_detector.is_left_blocked.return_value = False
        self._wall_detector.is_front_blocked.return_value = False
        self._wall_detector.is_right_blocked.return_value = True

        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _left_turns = 0
        _no_turns = 0
        for x in range(20):
            manager.reset_mock()

            self._maze_solver.next_move()

            self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
            self.assertTrue(
                manager.mock_calls[3] in [call.the_mock_motors.no_turn(), call.the_mock_motors.turn_left()],
                'Call {} is not one of the expected calls!'.format(manager.mock_calls[3])
            )
            if str(manager.mock_calls[3]) == 'call.the_mock_motors.no_turn()':
                _no_turns += 1
            elif str(manager.mock_calls[3]) == 'call.the_mock_motors.turn_left()':
                _left_turns += 1
            self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])
        self.assertTrue(_left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_no_turns > 3, 'Too few no turns made!')

    def test_should_turn_randomly_either_right_or_make_no_turn_and_move_forward_when_only_left_is_blocked(self):
        self._wall_detector.is_left_blocked.return_value = True
        self._wall_detector.is_front_blocked.return_value = False
        self._wall_detector.is_right_blocked.return_value = False

        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _right_turns = 0
        _no_turns = 0
        for x in range(20):
            manager.reset_mock()

            self._maze_solver.next_move()

            self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
            self.assertTrue(
                manager.mock_calls[3] in [call.the_mock_motors.no_turn(), call.the_mock_motors.turn_right()],
                'Call {} is not one of the expected calls!'.format(manager.mock_calls[3])
            )
            if str(manager.mock_calls[3]) == 'call.the_mock_motors.no_turn()':
                _no_turns += 1
            elif str(manager.mock_calls[3]) == 'call.the_mock_motors.turn_right()':
                _right_turns += 1
            self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])
        self.assertTrue(_right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_no_turns > 3, 'Too few no turns made!')

    def test_should_randomly_either_turn_right_or_turn_left_or_make_no_turn_and_move_forward_when_nothing_is_blocked(self):
        self._wall_detector.is_left_blocked.return_value = False
        self._wall_detector.is_front_blocked.return_value = False
        self._wall_detector.is_right_blocked.return_value = False

        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _left_turns = 0
        _right_turns = 0
        _no_turns = 0
        for x in range(30):
            manager.reset_mock()

            self._maze_solver.next_move()

            self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
            self.assertTrue(
                manager.mock_calls[3] in [
                    call.the_mock_motors.no_turn(), 
                    call.the_mock_motors.turn_right(), 
                    call.the_mock_motors.turn_left()
                ],
                'Call {} is not one of the expected calls!'.format(manager.mock_calls[3])
            )
            if str(manager.mock_calls[3]) == 'call.the_mock_motors.no_turn()':
                _no_turns += 1
            elif str(manager.mock_calls[3]) == 'call.the_mock_motors.turn_left()':
                _left_turns += 1
            elif str(manager.mock_calls[3]) == 'call.the_mock_motors.turn_right()':
                _right_turns += 1
            self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])
        self.assertTrue(_right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_no_turns > 3, 'Too few no turns made!')


if __name__ == '__main__':
    unittest.main()
