# About

This is the code for my maze solver robot. It includes a simulator and a [LEGO Mindstorms EV3](https://www.lego.com/mindstorms) implementation on [ev3dev](https://www.ev3dev.org/) using [ev3devpython v2](https://sites.google.com/site/ev3devpython/). I had no prior experience in maze solving, and i wrote this from scratch without any significant research on maze solving algorithms (just for the fun of it). So, it may well be naive and/or inefficient.  Certainly my EV3 robot is too big and too slow. But in any case - i'm going to [Robotex Estonia](https://robotex.international/competitions/maze-solving/) to compete with it :P 

# Status

This is currently work in progress. The algorithm lacks cycle detection - but i'm working on it. 

The EV3 part does not fully work yet. I'm not sure if i get it to working at all - seems like the EV3 ultrasound distance sensors are not accurate enough in distances less than 5 cm. Also it is not quite possible to create a robot that has width less than 10cm with LEGO parts. Thus, i have a hard time getting it to not hit any wall.

Simulator works fine.

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
python -m unittest test.maze_solver.test_curious_maze_solver.PreferredDirectionsTestNoneBlocked
```
Running a single unit test:
```
cd /app
python -m unittest test.maze_solver.test_curious_maze_solver.PreferredDirectionsTestNoneBlocked.test_should_randomly_either_turn_left_or_right_when_front_is_dead_end
```

# Simulator

Running the simulation application:
```
cd /app
python .\maze_solver_simulator_app.py
```
