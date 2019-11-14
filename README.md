# Running The Application and Unit Tests

Running a Python runtime in Docker:
```
docker run -i -t --rm --name lehm-madu-uss -v /home/k6ps/windows_user_home/projects/maze-solver-simulator:/app python:3.8-alpine3.10 /bin/bash
```
Running unit tests:
```
cd /app
python -m unittest discover -v
```
Running a single unit test class:
```
cd /app
python -m unittest test.test_curious_maze_solver.PreferredDirectionsTestNoneBlocked
```
Running a single unit test:
```
cd /app
python -m unittest test.test_curious_maze_solver.PreferredDirectionsTestNoneBlocked.test_should_randomly_either_turn_left_or_right_when_front_is_dead_end
```
Running the simulation application:
```
cd /app
python .\maze_solver_simulator_app.py
```

# To Do

1. Add unit test for preferring unexplored paths to explored ones.
2. Add preference to directions that lead to central squares.
3. Add detection of cycles and marking them as dead ends.
