import statistics
from maze_solver.maze_solving_session import SimulatorMazeSolvingSession
from maze_solver.maze_factory import create_robotex_cyprus_2017_maze, create_a_real_16_to_16_beast


_EXPERIMENT_COUNT = 1000

maze = create_a_real_16_to_16_beast()
# maze = create_robotex_cyprus_2017_maze()
_total_move_counts = []
_total_motion_times = []
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
    _total_move_counts.append(_results['move_count'])
    _total_motion_times.append(_results['motion_time'])
print('=================================================================')
print('=== maze={}'.format(maze.name))
print('=== move count mean={}'.format(statistics.mean(_total_move_counts)))
print('=== move count median={}'.format(statistics.median(_total_move_counts)))
print('=== move count stdev={}'.format(statistics.stdev(_total_move_counts)))
print('=== move count min={}'.format(min(_total_move_counts)))
print('=== move count max={}'.format(max(_total_move_counts)))
print('=== motion time mean={}'.format(statistics.mean(_total_motion_times)))
print('=== motion time median={}'.format(statistics.median(_total_motion_times)))
print('=== motion time stdev={}'.format(statistics.stdev(_total_motion_times)))
print('=== motion time min={}'.format(min(_total_motion_times)))
print('=== motion time max={}'.format(max(_total_motion_times)))
print('=================================================================')
