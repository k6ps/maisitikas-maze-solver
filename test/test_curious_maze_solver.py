import unittest
from unittest.mock import call, MagicMock, Mock
from maze_solver.maze_solver import CuriousMazeSolver, Motors, NotificationType, Square
from maze_solver.direction import Direction
from test.test_maze_solver import BaseMazeResolverTest, MotorsCallCounter


class CuriousMazeSolverTest(BaseMazeResolverTest):

    def setUp(self):
        self.create_mocks()
        self._maze_solver = CuriousMazeSolver(self._motors, self._wall_detector, self._finish_detector, self._outputs)

    def set_front_of_x1_y1_as_dead_end(self):
        self._maze_solver.add_square_as_visited(Square(x = 1, y = 2, is_dead_end = True))

    def set_left_of_x1_y1_as_dead_end(self):
        self._maze_solver.add_square_as_visited(Square(x = 0, y = 1, is_dead_end = True))

    def set_right_of_x1_y1_as_dead_end(self):
        self._maze_solver.add_square_as_visited(Square(x = 2, y = 1, is_dead_end = True))

    def assert_only_turn_left_called(self):
        self._motors.no_turn.assert_not_called()
        self._motors.turn_left.assert_called()
        self._motors.turn_right.assert_not_called()
        self._motors.turn_back.assert_not_called()

    def assert_only_turn_right_called(self):
        self._motors.no_turn.assert_not_called()
        self._motors.turn_left.assert_not_called()
        self._motors.turn_right.assert_called()
        self._motors.turn_back.assert_not_called()

    def assert_only_no_turn_called(self):
        self._motors.no_turn.assert_called()
        self._motors.turn_left.assert_not_called()
        self._motors.turn_right.assert_not_called()
        self._motors.turn_back.assert_not_called()


class InitialStateTest(CuriousMazeSolverTest):

    def test_should_mark_the_x1_y1_start_square_as_current_when_created(self):
        self.assertEqual(1, self._maze_solver.current_square.x)
        self.assertEqual(1, self._maze_solver.current_square.y)

    def test_should_set_north_as_current_direction_when_created(self):
        self.assertEqual(Direction.NORTH, self._maze_solver.current_direction)


class VisitedSquaresTest(CuriousMazeSolverTest):

    def test_should_mark_start_square_as_visited_when_making_first_move(self):
        self.assertFalse(self._maze_solver.is_visited(x = 1, y = 1))
        self.prepare_mock_wall_detector(front_blocked = False)
        self._maze_solver.next_move()
        self.assertTrue(self._maze_solver.is_visited(x = 1, y = 1))

    def test_should_mark_the_second_square_as_visited_when_making_two_forward_moves(self):
        self.prepare_mock_wall_detector(front_blocked = False)
        self._maze_solver.next_move()
        self.assertFalse(self._maze_solver.is_visited(x = 1, y = 2))
        self._maze_solver.next_move()
        self.assertTrue(self._maze_solver.is_visited(x = 1, y = 2))

    def test_should_mark_the_third_square_as_visited_when_making_two_forward_and_one_right_moves(self):
        self._wall_detector.is_front_blocked.side_effect = [False, False, True]
        self._wall_detector.is_left_blocked.side_effect = [True, True, True]
        self._wall_detector.is_right_blocked.side_effect = [True, True, False]
        self._maze_solver.next_move()
        self._maze_solver.next_move()
        self.assertFalse(self._maze_solver.is_visited(x = 1, y = 3))
        self._maze_solver.next_move()
        self.assertTrue(self._maze_solver.is_visited(x = 1, y = 3))

    def test_should_mark_the_fourth_square_as_visited_when_making_two_forward_and_two_right_moves(self):
        self._wall_detector.is_front_blocked.side_effect = [False, False, True, True]
        self._wall_detector.is_left_blocked.side_effect = [True, True, True, True]
        self._wall_detector.is_right_blocked.side_effect = [True, True, False, False]
        self._maze_solver.next_move()
        self._maze_solver.next_move()
        self._maze_solver.next_move()
        self.assertFalse(self._maze_solver.is_visited(x = 2, y = 3))
        self._maze_solver.next_move()
        self.assertTrue(self._maze_solver.is_visited(x = 2, y = 3))


class DeadEndSquaresTest(CuriousMazeSolverTest):

    def test_should_mark_square_as_dead_end_when_all_sides_blocked(self):
        self._wall_detector.is_front_blocked.side_effect = [False, True]
        self._wall_detector.is_left_blocked.side_effect = [True, True]
        self._wall_detector.is_right_blocked.side_effect = [True, True]
        self._maze_solver.next_move()
        self.assertFalse(self._maze_solver.is_dead_end(x = 1, y = 2))
        self._maze_solver.next_move()
        self.assertTrue(self._maze_solver.is_dead_end(x = 1, y = 2))

    def test_should_mark_multiple_visited_squares_as_dead_end_when_coming_from_dead_end_with_one_possible_path_only(self):
        self._wall_detector.is_front_blocked.side_effect = [False, False, False, True, False, False]
        self._wall_detector.is_left_blocked.side_effect = [True, True, True, True, True, True]
        self._wall_detector.is_right_blocked.side_effect = [True, True, True, True, True, True]
        self._maze_solver.next_move()
        self._maze_solver.next_move()
        self._maze_solver.next_move()
        self.assertFalse(self._maze_solver.is_dead_end(x = 1, y = 2))
        self.assertFalse(self._maze_solver.is_dead_end(x = 1, y = 3))
        self._maze_solver.next_move()
        self._maze_solver.next_move()
        self._maze_solver.next_move()
        self.assertTrue(self._maze_solver.is_dead_end(x = 1, y = 2))
        self.assertTrue(self._maze_solver.is_dead_end(x = 1, y = 3))


class PreferredDirectionsTestNoneBlocked(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_call_recorder()
        self.prepare_mock_wall_detector(front_blocked = False, right_blocked = False, left_blocked = False)

    def test_should_turn_left_when_other_directions_are_dead_ends(self):
        self.set_front_of_x1_y1_as_dead_end()
        self.set_right_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_turn_right_when_other_directions_are_dead_ends(self):
        self.set_left_of_x1_y1_as_dead_end()
        self.set_front_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_make_no_turn_when_front_is_free_and_other_directions_are_dead_ends(self):
        self.set_left_of_x1_y1_as_dead_end()
        self.set_right_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()

    def test_should_randomly_either_turn_left_or_right_when_front_is_dead_end(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_front_of_x1_y1_as_dead_end()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns == 0, 'Unexpected no turn made!')

    def test_should_randomly_either_turn_left_or_make_no_turn_when_right_is_dead_end(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_right_of_x1_y1_as_dead_end()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.right_turns == 0, 'Unexpected right turn made!')

    def test_should_randomly_either_turn_right_or_make_no_turn_when_left_is_dead_end(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_left_of_x1_y1_as_dead_end()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.left_turns == 0, 'Unexpected left turn made!')


class PreferredDirectionsTestFrontBlocked(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(right_blocked = False, left_blocked = False)

    def test_should_turn_left_when_front_blocked_and_right_dead_end(self):
        self.set_right_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_turn_right_when_front_blocked_and_left_dead_end(self):
        self.set_left_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()


class PreferredDirectionsTestRightBlocked(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(front_blocked = False, left_blocked = False)

    def test_should_turn_left_when_front_dead_end_and_right_blocked(self):
        self.set_front_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_make_no_turn_when_right_blocked_and_left_dead_end(self):
        self.set_left_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()


class PreferredDirectionsTestLeftBlocked(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(front_blocked = False, right_blocked = False)

    def test_should_turn_right_when_front_dead_end_and_left_blocked(self):
        self.set_front_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_make_no_turn_when_left_blocked_and_right_dead_end(self):
        self.set_right_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()


if __name__ == '__main__':
    unittest.main()
