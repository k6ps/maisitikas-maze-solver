# Running The Application and Unit Tests

Running a Python runtime in Docker:
```
docker run -i -t --rm --name my-python-box -v /home/me/my-projects/maze-solver-simulator:/app python:3.8-alpine3.10 /bin/bash
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

1. Add unit tests for preference to directions that lead to central squares.
2. Fix and add unit tests for preference to making no turn over turning left or right.
3. Add proper logging
4. Add memorzing the path taken.
5. Figure out some less tedious and error-prone way to create new mazes. Maybe machine-readable ASCII art?
6. Add detection and avoidance of cycles.
