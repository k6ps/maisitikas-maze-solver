# About

This is the code for my maze solver robot. It includes a simulator and a [LEGO Mindstorms EV3](https://www.lego.com/mindstorms) implementation on [ev3dev](https://www.ev3dev.org/) using [ev3devpython v2](https://sites.google.com/site/ev3devpython/). I had no prior experience in maze solving, and i wrote this from scratch without any significant research on maze solving algorithms (just for the fun of it). So, it may well be naive and/or inefficient.  Certainly my EV3 robot is too big and too slow. But in any case - i'm going to [Robotex Estonia](https://robotex.international/competitions/maze-solving/) to compete with it :P 

# Status

This is currently work in progress. I may not publish some best parts of code before the competition - just in case :D. The algorithm lacks cycle detetion - but i'm working on it. Also, the EV3 part does not work yet. Simulator works fine.

# Running Unit Tests

I run unit tests and simulator in Docker. Running a Python runtime in Docker:
```
docker run -i -t --rm --name my-python-box -v /home/me/my-projects/maze-solver-simulator:/app python:3.8-alpine3.10 /bin/bash
```
Running unit tests:
```
cd /app
python -m unittest discover -v
```
If not running in Docker then just cd to project dir instead of the /app, of course.
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

# Simulator

Running the simulation application:
```
cd /app
python .\maze_solver_simulator_app.py
```
