import unittest
from unittest.mock import MagicMock
from maze_solver.direction import Direction
from simulator.maze_solving_session import MazeSolvingSession, SimulatorMazeSolvingSession
from simulator.maze import MazeSquare


class MazeSolvingSessionTests(unittest.TestCase):

    def setUp(self):
        self._maze = MagicMock()
        self._maze.get_start_square.return_value = MazeSquare(x = 1, y = 1, is_start=True)
        self._maze_solver = MagicMock()
        self._maze_solving_session = MazeSolvingSession(maze = self._maze, maze_solver = self._maze_solver)

    def test_should_place_maze_solver_in_square_x1_y1_before_start(self):
        self.assertEqual(1, self._maze_solving_session.current_square.x)
        self.assertEqual(1, self._maze_solving_session.current_square.x)

    def test_should_place_maze_solver_facing_north_before_start(self):
        self.assertEqual(Direction.NORTH, self._maze_solving_session.current_direction)

    def test_should_zero_move_counter_before_start(self):
        self.assertEqual(0, self._maze_solving_session.move_count)

    def test_should_call_next_move_on_maze_solver_when_started(self):
        self._maze_solving_session.start()
        self._maze_solver.next_move.assert_called()

    def test_should_increment_move_counter_when_started(self):
        self._maze_solving_session.start()
        self.assertEqual(1, self._maze_solving_session.move_count)

    def test_should_call_next_move_five_times_when_previous_not_finished_and_can_move_four_times(self):
        self._maze_solver.next_move.side_effect =[False, False, False, False, True]
        self._maze_solving_session.start()
        self.assertEqual(5, len(self._maze_solver.next_move.call_args_list))

    def test_should_increment_move_counter_five_times_when_previous_not_finished_and_can_move_four_times(self):
        self._maze_solver.next_move.side_effect =[False, False, False, False, True]
        self._maze_solving_session.start()
        self.assertEqual(5, self._maze_solving_session.move_count)

    def test_should_returm_correct_move_count_when_previous_not_finished_and_can_move_four_times(self):
        self._maze_solver.next_move.side_effect =[False, False, False, False, True]
        _count = self._maze_solving_session.start()
        self.assertEqual(5, _count)

    def test_should_call_next_move_three_times_when_max_move_count_is_three_and_can_move_at_least_three_times(self):
        self._maze_solving_session = MazeSolvingSession(maze = self._maze, maze_solver = self._maze_solver, max_moves=3)
        self._maze_solver.next_move.side_effect =[False, False, False, False, True]
        self._maze_solving_session.start()
        self.assertEqual(3, len(self._maze_solver.next_move.call_args_list))

    def test_should_increment_move_counter_three_times_when_max_move_count_is_three_and_can_move_at_least_three_times(self):
        self._maze_solving_session = MazeSolvingSession(maze = self._maze, maze_solver = self._maze_solver, max_moves=3)
        self._maze_solver.next_move.side_effect =[False, False, False, False, True]
        self._maze_solving_session.start()
        self.assertEqual(3, self._maze_solving_session.move_count)

    def test_should_returm_correct_move_count_when_max_move_count_is_three_and_can_move_at_least_three_times(self):
        self._maze_solving_session = MazeSolvingSession(maze = self._maze, maze_solver = self._maze_solver, max_moves=3)
        self._maze_solver.next_move.side_effect =[False, False, False, False, True]
        _count = self._maze_solving_session.start()
        self.assertEqual(3, _count)


class SimulatorMazeSolvingSessionTests(unittest.TestCase):

    def setUp(self):
        self._maze = MagicMock()
        self._maze.get_start_square.return_value = MazeSquare(x = 1, y = 1, is_start=True)
        self._simulator_maze_solving_session = SimulatorMazeSolvingSession(self._maze)

    def test_should_be_directed_east_when_right_turn_performed(self):
        self._simulator_maze_solving_session.turn_right()
        self.assertEqual(Direction.EAST, self._simulator_maze_solving_session.current_direction)

    def test_should_be_directed_west_when_left_turn_performed(self):
        self._simulator_maze_solving_session.turn_left()
        self.assertEqual(Direction.WEST, self._simulator_maze_solving_session.current_direction)

    def test_should_be_directed_south_when_back_turn_performed(self):
        self._simulator_maze_solving_session.turn_back()
        self.assertEqual(Direction.SOUTH, self._simulator_maze_solving_session.current_direction)

    def test_should_be_in_square_x1_y2_when_moving_forward(self):
        self._simulator_maze_solving_session.move_forward()
        self._maze.get_square.assert_called_with(x=1, y=2)

    def test_should_turn_right_when_front_and_left_are_blocked(self):
        self._simulator_maze_solving_session.move_forward()
        self._maze.get_square.assert_called_with(x=1, y=2)
