import unittest
from unittest.mock import call, MagicMock, Mock
from maze_solver.maze_solver import MazeSolver, Motors, NotificationType


class MotorsCallCounter(object):

    def __init__(self):
        self._left_turns = 0
        self._right_turns = 0
        self._no_turns = 0

    @property
    def left_turns(self) -> int:
        return self._left_turns

    @property
    def right_turns(self) -> int:
        return self._right_turns

    @property
    def no_turns(self) -> int:
        return self._no_turns

    def count_call(self, actual_call):
        if str(actual_call) == 'call.the_mock_motors.no_turn()':
            self._no_turns += 1
        elif str(actual_call) == 'call.the_mock_motors.turn_left()':
            self._left_turns += 1
        elif str(actual_call) == 'call.the_mock_motors.turn_right()':
            self._right_turns += 1


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

    def assert_call_is_one_of(self, actual_call, expected_call_choice: list):
        self.assertTrue(
            actual_call in expected_call_choice,
            'Call {} is not one of the expected calls!'.format(actual_call)
        )

    def prepare_mock_wall_detector(self, left_blocked: bool = True, front_blocked: bool = True, right_blocked: bool = True):
        self._wall_detector.is_left_blocked.return_value = left_blocked
        self._wall_detector.is_front_blocked.return_value = front_blocked
        self._wall_detector.is_right_blocked.return_value = right_blocked

    def prepare_call_recorder(self):
        self._call_recorder = Mock()
        self._call_recorder.the_mock_motors = self._motors
        self._call_recorder.the_mock_wall_detector = self._wall_detector
        self._call_recorder.the_mock_finish_detector = self._finish_detector

    def setUp(self):
        self._motors = MagicMock()
        self._wall_detector = MagicMock()
        self._finish_detector = MagicMock()
        self._finish_detector.is_finish.return_value = False
        self._outputs = MagicMock()
        self._maze_solver = MazeSolver(self._motors, self._wall_detector, self._finish_detector, self._outputs)


class InFinishSquare(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False, front_blocked = False)
        self._finish_detector.is_finish.return_value = True

    def test_should_not_make_any_turns_and_moves(self):
        self._maze_solver.next_move()
        self._motors.no_turn.assert_not_called()
        self._motors.turn_left.assert_not_called()
        self._motors.turn_right.assert_not_called()
        self._motors.move_forward.assert_not_called()

    def test_should_notify_info_finished(self):
        self._maze_solver.next_move()
        self._outputs.notify.assert_called_with(NotificationType.INFO, 'Finised successfully in finish square!')

    def test_should_return_true(self):
        self.assertTrue(self._maze_solver.next_move())


class InNonFinishSquareWithAllSidesBlocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector() 
        self.prepare_call_recorder()

    def test_should_check_if_is_in_finish_square_as_first_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_finish_detector.is_finish(), self._call_recorder.mock_calls[0])

    def test_should_check_if_walls_blocked_as_second_action(self):
        self._maze_solver.next_move()
        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, self._call_recorder.mock_calls[1:4])

    def test_should_turn_randomly_either_left_or_right_and_check_again(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
            self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, self._call_recorder.mock_calls[5:8])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns == 0, 'Unexpected no turn made!')

    def test_should_notify_error(self):
        self._maze_solver.next_move()
        self._outputs.notify.assert_called_with(NotificationType.ERROR, 'Cannot move, blocked from all sides!')

    def test_should_return_true(self):
        self.assertTrue(self._maze_solver.next_move())


class InNonFinishSquareWithOnlyFrontSideUnblocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(front_blocked = False)
        self.prepare_call_recorder()

    def test_should_check_if_is_in_finish_square_as_first_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_finish_detector.is_finish(), self._call_recorder.mock_calls[0])

    def test_should_check_if_walls_blocked_as_second_action(self):
        self._maze_solver.next_move()
        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, self._call_recorder.mock_calls[1:4])

    def test_should_make_no_turn(self):
        self._maze_solver.next_move()
        self._motors.no_turn.assert_called()
        self._motors.turn_left.assert_not_called()
        self._motors.turn_right.assert_not_called()

    def test_should_move_forward_as_last_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_motors.move_forward(), self._call_recorder.mock_calls[-1])

    def test_should_return_false(self):
        self.assertFalse (self._maze_solver.next_move())


class InNonFinishSquareWithOnlyLeftSideUnblocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False)
        self.prepare_call_recorder()

    def test_should_check_if_is_in_finish_square_as_first_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_finish_detector.is_finish(), self._call_recorder.mock_calls[0])

    def test_should_check_if_walls_blocked_as_second_action(self):
        self._maze_solver.next_move()
        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, self._call_recorder.mock_calls[1:4])

    def test_should_turn_left(self):
        self._maze_solver.next_move()
        self._motors.no_turn.assert_not_called()
        self._motors.turn_left.assert_called()
        self._motors.turn_right.assert_not_called()

    def test_should_move_forward_as_last_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_motors.move_forward(), self._call_recorder.mock_calls[-1])

    def test_should_return_false(self):
        self.assertFalse (self._maze_solver.next_move())


class InNonFinishSquareWithOnlyRightSideUnblocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(right_blocked = False)
        self.prepare_call_recorder()

    def test_should_check_if_is_in_finish_square_as_first_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_finish_detector.is_finish(), self._call_recorder.mock_calls[0])

    def test_should_check_if_walls_blocked_as_second_action(self):
        self._maze_solver.next_move()
        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, self._call_recorder.mock_calls[1:4])

    def test_should_turn_right(self):
        self._maze_solver.next_move()
        self._motors.no_turn.assert_not_called()
        self._motors.turn_left.assert_not_called()
        self._motors.turn_right.assert_called()

    def test_should_move_forward_as_last_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_motors.move_forward(), self._call_recorder.mock_calls[-1])

    def test_should_return_false(self):
        self.assertFalse (self._maze_solver.next_move())


class InNonFinishSquareWithOnlyFrontSideBlocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False, right_blocked = False)
        self.prepare_call_recorder()

    def test_should_check_if_is_in_finish_square_as_first_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_finish_detector.is_finish(), self._call_recorder.mock_calls[0])

    def test_should_check_if_walls_blocked_as_second_action(self):
        self._maze_solver.next_move()
        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, self._call_recorder.mock_calls[1:4])

    def test_should_turn_randomly_either_left_or_right_and_move_forward(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns == 0, 'Unexpected no turn made!')

    def test_should_move_forward_as_last_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_motors.move_forward(), self._call_recorder.mock_calls[-1])

    def test_should_return_false(self):
        self.assertFalse (self._maze_solver.next_move())


class InNonFinishSquareWithOnlyLeftSideBlocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(front_blocked = False, right_blocked = False)
        self.prepare_call_recorder()

    def test_should_check_if_is_in_finish_square_as_first_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_finish_detector.is_finish(), self._call_recorder.mock_calls[0])

    def test_should_check_if_walls_blocked_as_second_action(self):
        self._maze_solver.next_move()
        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, self._call_recorder.mock_calls[1:4])

    def test_should_turn_randomly_either_right_or_make_no_turn_and_move_forward(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.left_turns == 0, 'Unexpected left turn made!')

    def test_should_move_forward_as_last_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_motors.move_forward(), self._call_recorder.mock_calls[-1])

    def test_should_return_false(self):
        self.assertFalse (self._maze_solver.next_move())


class InNonFinishSquareWithOnlyRightSideBlocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False, front_blocked = False)
        self.prepare_call_recorder()

    def test_should_check_if_is_in_finish_square_as_first_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_finish_detector.is_finish(), self._call_recorder.mock_calls[0])

    def test_should_check_if_walls_blocked_as_second_action(self):
        self._maze_solver.next_move()
        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, self._call_recorder.mock_calls[1:4])

    def test_should_randomly_either_turn_left_or_make_no_turn(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.right_turns == 0, 'Unexpected right turn made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')

    def test_should_move_forward_as_last_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_motors.move_forward(), self._call_recorder.mock_calls[-1])

    def test_should_return_false(self):
        self.assertFalse (self._maze_solver.next_move())


class InNonFinishSquareWithAllSidesUnblocked(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False, front_blocked = False, right_blocked = False)
        self.prepare_call_recorder()

    def test_should_check_if_is_in_finish_square_as_first_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_finish_detector.is_finish(), self._call_recorder.mock_calls[0])

    def test_should_check_if_walls_blocked_as_second_action(self):
        self._maze_solver.next_move()
        self.assert_wall_detector_calls_in_any_order(call.the_mock_wall_detector, self._call_recorder.mock_calls[1:4])

    def test_should_randomly_either_turn_right_or_turn_left_or_make_no_turn(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(30):
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')

    def test_should_move_forward_as_last_action(self):
        self._maze_solver.next_move()
        self.assertEqual(call.the_mock_motors.move_forward(), self._call_recorder.mock_calls[-1])

    def test_should_return_false(self):
        self.assertFalse (self._maze_solver.next_move())


class BorderlessMazeWithNoWallsAndNoFinish(BaseMazeResolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(left_blocked = False, front_blocked = False, right_blocked = False)
        self.prepare_call_recorder()
        self._test_max_call_count = 13

    def test_should_perform_maximum_allowed_number_of_moves(self):
        self._maze_solver.moves_left = self._test_max_call_count
        self._maze_solver.start()
        _move_forward_call_count = 0
        for actual_call in self._call_recorder.mock_calls:
            if str(actual_call) == 'call.the_mock_motors.move_forward()':
                _move_forward_call_count += 1
        self.assertEqual(self._test_max_call_count, _move_forward_call_count)

    def test_should_notfy_max_call_count_reached(self):
        self._maze_solver.moves_left = self._test_max_call_count
        self._maze_solver.start()
        self._outputs.notify.assert_called_with(NotificationType.ERROR, 'Maximum allowed call count={} reached!'.format(self._test_max_call_count))


if __name__ == '__main__':
    unittest.main()
