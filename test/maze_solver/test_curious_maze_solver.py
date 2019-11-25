import unittest
from unittest.mock import call, MagicMock, Mock
from maze_solver.maze_solver import CuriousMazeSolver, Motors, NotificationType, Square
from maze_solver.direction import Direction
from test.maze_solver.test_maze_solver import BaseMazeResolverTest, MotorsCallCounter


class CuriousMazeSolverTest(BaseMazeResolverTest):

    def setUp(self):
        self.create_mocks()
        self._maze_solver = CuriousMazeSolver(self._motors, self._wall_detector, self._finish_detector, self._outputs)
        self.prepare_call_recorder()

    def set_front_of_x1_y1_as_dead_end(self):
        self._maze_solver.add_square_as_visited(Square(x = 1, y = 2, is_dead_end = True))

    def set_left_of_x1_y1_as_dead_end(self):
        self._maze_solver.add_square_as_visited(Square(x = 0, y = 1, is_dead_end = True))

    def set_right_of_x1_y1_as_dead_end(self):
        self._maze_solver.add_square_as_visited(Square(x = 2, y = 1, is_dead_end = True))

    def set_front_of_x1_y1_as_visited(self):
        self._maze_solver.add_square_as_visited(Square(x = 1, y = 2))

    def set_left_of_x1_y1_as_visited(self):
        self._maze_solver.add_square_as_visited(Square(x = 0, y = 1))

    def set_right_of_x1_y1_as_visited(self):
        self._maze_solver.add_square_as_visited(Square(x = 2, y = 1))

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


class MarkVisitedSquaresTest(CuriousMazeSolverTest):

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


class MarkDeadEndSquaresTest(CuriousMazeSolverTest):

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


class InSquareNoneBlockedTest(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(front_blocked = False, right_blocked = False, left_blocked = False)


class InSquareLeftBlockedTest(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(front_blocked = False, right_blocked = False)


class InSquareRightBlockedTest(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(front_blocked = False, left_blocked = False)


class InSquareFrontBlockedTest(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.prepare_mock_wall_detector(right_blocked = False, left_blocked = False)


class AvoidDeadEndsTest(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.set_other_weights_to_zero_except_dead_end()

    def set_other_weights_to_zero_except_dead_end(self):
        self._maze_solver.prefer_closer_to_center_weight = 0
        self._maze_solver.prefer_no_turns_weight = 0
        self._maze_solver.prefer_unvisited_paths_weight = 0


class PreferUnvisitedTest(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.set_other_weights_to_zero_except_unvisited()

    def set_other_weights_to_zero_except_unvisited(self):
        self._maze_solver.prefer_closer_to_center_weight = 0
        self._maze_solver.prefer_no_turns_weight = 0
        self._maze_solver.prefer_non_dead_ends_weight = 0


class AvoidDeadEndsWithNoneBlockedTest(InSquareNoneBlockedTest, AvoidDeadEndsTest):

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


class PreferUnvisitedWithNoneBlockedTest(InSquareNoneBlockedTest,PreferUnvisitedTest):

    def test_should_turn_left_when_other_directions_are_visited(self):
        self.set_front_of_x1_y1_as_visited()
        self.set_right_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_turn_right_when_other_directions_are_visited(self):
        self.set_left_of_x1_y1_as_visited()
        self.set_front_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_make_no_turn_when_front_is_free_and_other_directions_are_visited(self):
        self.set_left_of_x1_y1_as_visited()
        self.set_right_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()

    def test_should_randomly_either_turn_left_or_right_when_front_is_visited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_front_of_x1_y1_as_visited()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns == 0, 'Unexpected no turn made!')

    def test_should_randomly_either_turn_left_or_make_no_turn_when_right_is_visited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_right_of_x1_y1_as_visited()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.right_turns == 0, 'Unexpected right turn made!')

    def test_should_randomly_either_turn_right_or_make_no_turn_when_left_is_visited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_left_of_x1_y1_as_visited()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.left_turns == 0, 'Unexpected left turn made!')


class AvoidDeadEndsWithFrontBlockedTest(InSquareFrontBlockedTest, AvoidDeadEndsTest):

    def test_should_turn_left_when_right_dead_end(self):
        self.set_right_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_turn_right_when_left_dead_end(self):
        self.set_left_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_randomly_either_turn_left_or_right_when_both_are_dead_ends(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_left_of_x1_y1_as_dead_end()
            self.set_right_of_x1_y1_as_dead_end()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns == 0, 'Unexpected no turn made!')


class PreferUnvisitedWithFrontBlockedTest(InSquareFrontBlockedTest, PreferUnvisitedTest):

    def test_should_turn_left_when_right_is_visited_and_left_is_unvisited(self):
        self.set_right_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_turn_right_when_right_is_unvisited_and_left_is_visited(self):
        self.set_left_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_randomly_either_turn_left_or_right_when_both_left_and_right_are_visited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_right_of_x1_y1_as_visited()
            self.set_left_of_x1_y1_as_visited()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns == 0, 'Unexpected no turn made!')

    def test_should_randomly_either_turn_left_or_right_when_both_left_and_right_are_unvisited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns == 0, 'Unexpected no turn made!')


class AvoidDeadEndsTestRightBlocked(InSquareRightBlockedTest, AvoidDeadEndsTest):

    def test_should_turn_left_when_front_dead_end(self):
        self.set_front_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_make_no_turn_when_left_dead_end(self):
        self.set_left_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()

    
class PreferUnvisitedTestRightBlocked(InSquareRightBlockedTest, PreferUnvisitedTest):

    def test_should_turn_left_when_front_is_visited_and_left_is_unvisited(self):
        self.set_front_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_make_no_turn_when_front_is_unvisited_and_left_is_visited(self):
        self.set_left_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()

    def test_should_randomly_either_turn_left_or_make_no_turn_when_both_left_and_front_are_visited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_front_of_x1_y1_as_visited()
            self.set_left_of_x1_y1_as_visited()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.right_turns == 0, 'Unexpected right turn made!')

    def test_should_randomly_either_turn_left_or_make_no_turn_when_both_left_and_front_are_unvisited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.right_turns == 0, 'Unexpected right turn made!')


class AvoidDeadEndsTestLeftBlocked(InSquareLeftBlockedTest, AvoidDeadEndsTest):

    def test_should_turn_right_when_front_dead_end(self):
        self.set_front_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_make_no_turn_when_right_dead_end(self):
        self.set_right_of_x1_y1_as_dead_end()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()


class PreferUnvisitedTestLeftBlocked(InSquareLeftBlockedTest, PreferUnvisitedTest):

    def test_should_turn_right_when_front_is_visited_and_right_is_unvisited(self):
        self.set_front_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_make_no_turn_when_front_is_unvisited_and_right_is_visited(self):
        self.set_right_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()

    def test_should_randomly_either_turn_right_or_make_no_turn_when_both_right_and_front_are_visited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_front_of_x1_y1_as_visited()
            self.set_right_of_x1_y1_as_visited()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.left_turns == 0, 'Unexpected left turn made!')

    def test_should_randomly_either_turn_right_or_make_no_turn_when_both_right_and_front_are_unvisited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.left_turns == 0, 'Unexpected left turn made!')


class PreferUnvisitedTestWithDeadEnds(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self._maze_solver.prefer_closer_to_center_weight = 0
        self._maze_solver.prefer_no_turns_weight = 0
        self.prepare_mock_wall_detector(front_blocked = False, right_blocked = False, left_blocked = False)


class PreferUnvisitedTestNoneBlockedLeftDeadEnd(PreferUnvisitedTestWithDeadEnds):

    def setUp(self):
        super().setUp()
        self.set_left_of_x1_y1_as_dead_end()

    def test_should_turn_right_when_front_is_visited_and_right_is_unvisited(self):
        self.set_front_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_make_no_turn_when_front_is_unvisited_and_right_is_visited(self):
        self.set_right_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()

    def test_should_randomly_either_turn_right_or_make_no_turn_when_both_right_and_front_are_visited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_left_of_x1_y1_as_dead_end()
            self.set_front_of_x1_y1_as_visited()
            self.set_right_of_x1_y1_as_visited()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.left_turns == 0, 'Unexpected left turn made!')

    def test_should_randomly_either_turn_right_or_make_no_turn_when_both_right_and_front_are_unvisited(self):
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


class PreferUnvisitedTestNoneBlockedRightDeadEnd(PreferUnvisitedTestWithDeadEnds):

    def setUp(self):
        super().setUp()
        self.set_right_of_x1_y1_as_dead_end()

    def test_should_turn_left_when_front_is_visited_and_left_is_unvisited(self):
        self.set_front_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_make_no_turn_when_front_is_unvisited_and_left_is_visited(self):
        self.set_left_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()

    def test_should_randomly_either_turn_left_or_make_no_turn_when_both_left_and_front_are_visited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_right_of_x1_y1_as_dead_end()
            self.set_front_of_x1_y1_as_visited()
            self.set_left_of_x1_y1_as_visited()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.no_turns > 3, 'Too few no turns made!')
        self.assertTrue(_motors_call_counter.right_turns == 0, 'Unexpected right turn made!')

    def test_should_randomly_either_turn_left_or_make_no_turn_when_both_left_and_front_are_unvisited(self):
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


class PreferUnvisitedTestNoneBlockedFrontDeadEnd(PreferUnvisitedTestWithDeadEnds):

    def setUp(self):
        super().setUp()
        self.set_front_of_x1_y1_as_dead_end()

    def test_should_turn_left_when_right_is_visited_and_left_is_unvisited(self):
        self.set_right_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_turn_right_when_right_is_unvisited_and_left_is_visited(self):
        self.set_left_of_x1_y1_as_visited()
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_randomly_either_turn_left_or_right_when_both_left_and_right_are_visited(self):
        _motors_call_counter = MotorsCallCounter()
        for _ in range(20):
            self._maze_solver.reset_to_start_and_forget_everything()
            self.set_front_of_x1_y1_as_dead_end()
            self.set_right_of_x1_y1_as_visited()
            self.set_left_of_x1_y1_as_visited()
            self._call_recorder.reset_mock()
            self._maze_solver.next_move()
            _motors_call_counter.count_call(self._call_recorder.mock_calls[4])
        self.assertTrue(_motors_call_counter.left_turns > 3, 'Too few left turns made!')
        self.assertTrue(_motors_call_counter.right_turns > 3, 'Too few right turns made!')
        self.assertTrue(_motors_call_counter.no_turns == 0, 'Unexpected no turn made!')

    def test_should_randomly_either_turn_left_or_right_when_both_left_and_right_are_unvisited(self):
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


class PreferCloserToAssumedFinishTest(CuriousMazeSolverTest):

    def setUp(self):
        super().setUp()
        self.set_other_weights_to_zero_except_closer_to_assumed_finish()

    def set_other_weights_to_zero_except_closer_to_assumed_finish(self):
        self._maze_solver.prefer_no_turns_weight = 0
        self._maze_solver.prefer_non_dead_ends_weight = 0
        self._maze_solver.prefer_unvisited_paths_weight = 0


class PreferCloserToFinishWithNoneBlockedTest(InSquareNoneBlockedTest, PreferCloserToAssumedFinishTest):

    def test_should_turn_left_when_in_lower_left_part_and_other_directions_are_farther_from_finish(self):
        self._maze_solver.center_coordinates = [5]
        self._maze_solver.current_square = Square(x = 4, y = 2)
        self._maze_solver.current_direction = Direction.EAST
        self._maze_solver.next_move()
        self.assert_only_turn_left_called()

    def test_should_turn_right_when_in_upper_left_part_and_other_directions_are_farther_from_finish(self):
        self._maze_solver.center_coordinates = [6]
        self._maze_solver.current_square = Square(x = 5, y = 9)
        self._maze_solver.current_direction = Direction.EAST
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()

    def test_should_make_no_turn_when_in_upper_right_part_and_other_directions_are_farther_from_finish(self):
        self._maze_solver.center_coordinates = [7]
        self._maze_solver.current_square = Square(x = 11, y = 7)
        self._maze_solver.current_direction = Direction.WEST
        self._maze_solver.next_move()
        self.assert_only_no_turn_called()

    def test_should_turn_right_when_multiple_finish_squares_and_other_directions_are_farther_from_finish(self):
        self._maze_solver.center_coordinates = [6, 7]
        self._maze_solver.current_square = Square(x = 10, y = 7)
        self._maze_solver.current_direction = Direction.SOUTH
        self._maze_solver.next_move()
        self.assert_only_turn_right_called()


if __name__ == '__main__':
    unittest.main()
