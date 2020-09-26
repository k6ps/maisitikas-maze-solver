import statistics
import sys
import logging
from simulator.maze_solving_session import SimulatorMazeSolvingSession
from simulator.maze import Maze
from simulator.maze_factory import create_robotex_cyprus_2017_maze, create_a_real_16_to_16_beast, create_kasemetsaresortspa_test_maze, create_6_to_6_maze

# TODO: make these parameters
_SAMPLE_SIZE = 1000
_TIME_LIMIT_SEC = 300
_MAX_MOVES_PER_SESSION = 999

def set_up_console_logging():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])

def perform_experiment(maze: Maze, center_coordinates: list) -> dict:
    _total_move_counts = []
    _total_motion_times = []
    _below_max_time_count = 0
    for _ in range(_SAMPLE_SIZE):
        simulator_session = SimulatorMazeSolvingSession(
            maze, 
            prefer_non_dead_ends_weight = 10,
            prefer_unvisited_paths_weight = 3,
            prefer_closer_to_center_weight = 5, 
            prefer_no_turns_weight = 0,
            max_moves=_MAX_MOVES_PER_SESSION,
            center_coordinates=center_coordinates
        )
        _results = simulator_session.start()
        _total_move_counts.append(_results['move_count'])
        _total_motion_times.append(_results['motion_time'])
        if _results['motion_time'] < _TIME_LIMIT_SEC:
            _below_max_time_count += 1
    _probability_of_solving_within_time_limit = _below_max_time_count * 100 / _SAMPLE_SIZE
    return {
        'maze_name': maze.name,
        'move_count_mean': statistics.mean(_total_move_counts),
        'move_count_median': statistics.median(_total_move_counts),
        'move_count_stdev': statistics.stdev(_total_move_counts),
        'move_count_min': min(_total_move_counts),
        'move_count_max': max(_total_move_counts),
        'motion_time_mean': statistics.mean(_total_motion_times),
        'motion_time_median': statistics.median(_total_motion_times),
        'motion_time_stdev': statistics.stdev(_total_motion_times),
        'motion_time_min': min(_total_motion_times),
        'motion_time_max': max(_total_motion_times),
        'probability_of_solving_within_time_limit': _probability_of_solving_within_time_limit
    }

def print_experiment_series_results(results: dict):
    for _result in results:
        print('=================================================================')
        for _key in _result.keys():
            print('{}={}'.format(_key, _result[_key]))
        print('=================================================================')

set_up_console_logging()
experiment_results = []
experiment_results.append(perform_experiment(maze = create_a_real_16_to_16_beast(), center_coordinates = [8, 9]))
experiment_results.append(perform_experiment(maze = create_robotex_cyprus_2017_maze(), center_coordinates = [8, 9]))
experiment_results.append(perform_experiment(maze = create_6_to_6_maze(), center_coordinates = [4]))
experiment_results.append(perform_experiment(maze = create_kasemetsaresortspa_test_maze(), center_coordinates = [4]))
print_experiment_series_results(experiment_results)
