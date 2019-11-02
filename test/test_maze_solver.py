import unittest
from unittest.mock import call, MagicMock, Mock
from maze_solver.maze_solver import MazeSolver, Motors, NotificationType


class BaseMazeResolverTest(unittest.TestCase):

    def assert_wall_detector_calls_in_any_order(self, wall_detector_mock, actual_calls):
        _expected_calls = [
            wall_detector_mock.is_left_blocked(),
            wall_detector_mock.is_front_blocked(),
            wall_detector_mock.is_right_blocked()
        ]
        self.assertEqual(3, len(actual_calls))
        for _expected_call in _expected_calls:
            self.assertTrue(_expected_call in actual_calls, 'Call {} not found!'.format(_expected_call))

    def prepare_mock_wall_detector(self, left_blocked: bool = True, front_blocked: bool = True, right_blocked: bool = True):
        self._wall_detector.is_left_blocked.return_value = left_blocked
        self._wall_detector.is_front_blocked.return_value = front_blocked
        self._wall_detector.is_right_blocked.return_value = right_blocked

    def setUp(self):
        self._motors = MagicMock()
        self._wall_detector = MagicMock()
        self._finish_detector = MagicMock()
        self._outputs = MagicMock()
        self._maze_solver = MazeSolver(self._motors, self._wall_detector, self._finish_detector, self._outputs)


class InNonFinishSquareWithAllSidesBlocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector()

    def test_should_turn_randomly_either_left_or_right_and_check_again(self):
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _left_turns = 0
        _right_turns = 0
        for _ in range(20):
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
            self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[4:7])
        self.assertTrue(_left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_right_turns > 3, 'Too few right turns made!')

    def test_should_notify_error(self):
        self._maze_solver.next_move()
        self._outputs.notify.assert_called_with(NotificationType.ERROR, 'Cannot move, blocked from all sides!')


class InNonFinishSquareWithOnlyFrontSideUnblocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(front_blocked = False)

    def test_should_make_no_turn_and_move_forward(self):
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        self._maze_solver.next_move()

        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
        self.assertEqual(call.the_mock_motors.no_turn(), manager.mock_calls[3])
        self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])


class InNonFinishSquareWithOnlyLeftSideUnblocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False)

    def test_should_turn_left_and_move_forward(self):
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        self._maze_solver.next_move()

        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
        self.assertEqual(call.the_mock_motors.turn_left(), manager.mock_calls[3])
        self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])


class InNonFinishSquareWithOnlyRightSideUnblocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(right_blocked = False)

    def test_should_turn_right_and_move_forward(self):
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        self._maze_solver.next_move()

        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, manager.mock_calls[0:3])
        self.assertEqual(call.the_mock_motors.turn_right(), manager.mock_calls[3])
        self.assertEqual(call.the_mock_motors.move_forward(), manager.mock_calls[4])


class InNonFinishSquareWithOnlyFrontSideBlocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False, right_blocked = False)

    def test_should_turn_randomly_either_left_or_right_and_move_forward(self):
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _left_turns = 0
        _right_turns = 0
        for _ in range(20):
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


class InNonFinishSquareWithOnlyLeftSideBlocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(front_blocked = False, right_blocked = False)

    def test_should_turn_randomly_either_right_or_make_no_turn_and_move_forward(self):
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _right_turns = 0
        _no_turns = 0
        for _ in range(20):
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


class InNonFinishSquareWithOnlyRightSideBlocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False, front_blocked = False)

    def test_should_turn_randomly_either_left_or_make_no_turn_and_move_forward(self):
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _left_turns = 0
        _no_turns = 0
        for _ in range(20):
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


class InNonFinishSquareWithAllSidesUnblocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False, front_blocked = False, right_blocked = False)

    def test_should_randomly_either_turn_right_or_turn_left_or_make_no_turn_and_move_forward(self):
        manager = Mock()
        manager.the_mock_motors = self._motors
        manager.the_mock_wall_detector = self._wall_detector

        _left_turns = 0
        _right_turns = 0
        _no_turns = 0
        for _ in range(30):
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
