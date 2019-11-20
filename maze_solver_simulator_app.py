from maze_solver.maze_solving_session import SimulatorMazeSolvingSession
from maze_solver.maze_factory import create_robotex_cyprus_2017_maze, create_a_real_16_to_16_beast


_EXPERIMENT_COUNT = 1000

maze = create_a_real_16_to_16_beast()
# maze = create_robotex_cyprus_2017_maze()
_total_count = 0
_total_motion_time = 0
for _ in range(_EXPERIMENT_COUNT):
    simulator_session = SimulatorMazeSolvingSession(
        maze, 
        prefer_non_dead_ends_weight = 10,
        prefer_unvisited_paths_weight = 3,
        prefer_closer_to_center_weight = 5, 
        prefer_no_turns_weight = 0,
        max_moves=999
    )
    _results = simulator_session.start()
    _total_count += _results['move_count']
    _total_motion_time += _results['motion_time']
print('=================================================================')
print('=== maze={}'.format(maze.name))
print('=== avg move count={}, avg motion time={}'.format(_total_count / _EXPERIMENT_COUNT, _total_motion_time / _EXPERIMENT_COUNT))
print('=================================================================')
