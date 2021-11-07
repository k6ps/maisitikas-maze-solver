# About

This is the code for my maze solver robot. It includes a simulator and a [LEGO Mindstorms EV3](https://www.lego.com/mindstorms) implementation on [ev3dev](https://www.ev3dev.org/) using [ev3devpython v2](https://sites.google.com/site/ev3devpython/). I had no prior experience in maze solving, and i wrote this from scratch without any significant research on maze solving algorithms (i deliberately chose not to use any existing algorithm, to see if i can come up with a decent one myself). So, it may well be naive and/or inefficient.  Certainly my EV3 robot is too big and too slow. But in any case - i'm going to [Robotex Estonia](https://robotex.international/competitions/maze-solving/) to compete with it :P 

# Status

It won the third place in maze solving at Robotex Estonia 2021!!! However, it was not a good performance - it did not get even close to the finish square, it hit a wall badly and lost direction, it spent too much time trying to recover from hitting wall and correcting turns and position. Just there were far less competitors in this pandemic-time Robotex than usual. Also, most other competitors did not do so well this time.  

It is all work in progress. I am still trying to make it to the finish line of 16x16 maze in the given time with fair probability, using just LEGO original parts.

The  EV3 light sensors are good at measuring short distances from the white walls. Also, gyro sensor seems accurate enough, if it has bee properly reset. However, it is not quite possible to create a robot that has width less than 10cm with LEGO Mindstorms EV3 parts. Thus, i have created an extensive (and overengineered) direction correction and recovery logic. However, my robot is still hitting walls, loosing direction, and is generally too slow.

The maze solving algorithm lacks cycle detection, and is probably not the most efficient. 

Simulator works fine. However, it is tedious and error-prone to add new mazes to it. I should figure out some clever way to do it, e.g. both human and machine readable ASCII art.

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
The ev3dev2 module does not have to be installed for running unit tests - i faked it for unit tests.

# Simulator

Running the simulation application:
```
cd /app
python ./maze_solver_simulator_app.py
```

# EV3 robot

The EV3 robot uses three light sensors, gyro sensor, and two large servo motors.

## Deploying to EV3 brick

1. Connect to the brick in some way, as explained in EV3DEV site. For example, i'm using the "Wi-Pi" USB Wifi dongle.
2. Create a subfolder in home folder, if needed.
3. Copy the maze_solver and ev3 modules via SFTP. Also copy the ```ev3_systemtest_*.py``` files and ```maze_solver_ev3_app.py```
4. Make sure that the systemtests and maze_solver_ev3_app.py have execute permission.

## System tests

I created several system tests to test particular actual behaviours in a real test maze. 

## Running the robot

1. Execute the ```maze_solver_ev3_app.py``` in the EV3 brick.
2. Wait at least 15 seconds. Currently there is no indication when the program is fully loaded and ready to start.
3. Push the center button.
