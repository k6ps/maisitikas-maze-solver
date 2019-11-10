from maze_solver.maze_solver import MazeSolver
from maze_solver.maze_solving_session import SimulatorMazeSolvingSession
from maze_solver.maze import MazeSquare, Maze

def create_simple_2_to_2_maze() -> Maze:
    _squares = [
        MazeSquare(x = 1, y = 1, x_plus = True, y_plus = True, is_start = True),
        MazeSquare(x = 1, y = 2, y_minus = True),
        MazeSquare(x = 2, y = 1, y_plus = True, x_minus = True),
        MazeSquare(x = 2, y = 2, y_minus = True, is_finish = True)
    ]
    return Maze(_squares)

def create_simple_3_to_3_maze() -> Maze:
    _squares = [
        MazeSquare(x = 1, y = 1, x_plus = True, is_start = True),
        MazeSquare(x = 1, y = 2, y_plus = True),
        MazeSquare(x = 1, y = 3, x_plus = True, y_minus = True),
        MazeSquare(x = 2, y = 1, y_plus = True, x_minus = True),
        MazeSquare(x = 2, y = 2, x_plus = True, y_plus = True, y_minus = True),
        MazeSquare(x = 2, y = 3, x_minus = True, y_minus = True),
        MazeSquare(x = 3, y = 1, y_plus = True),
        MazeSquare(x = 3, y = 2, y_plus = True, x_minus = True, y_minus = True),
        MazeSquare(x = 3, y = 3, y_minus = True, is_finish = True)
    ]
    return Maze(_squares)

def create_6_to_6_maze() -> Maze:
    _squares = [
        MazeSquare(x = 1, y = 1, x_plus = True, is_start = True),
        MazeSquare(x = 1, y = 2, y_plus = True, y_minus = True),
        MazeSquare(x = 1, y = 3, x_plus = True, y_minus = True),
        MazeSquare(x = 1, y = 4, x_plus = True),
        MazeSquare(x = 1, y = 5, y_plus = True),
        MazeSquare(x = 1, y = 6, x_plus = True, y_minus = True),
        MazeSquare(x = 2, y = 1, x_plus = True, y_plus = True),
        MazeSquare(x = 2, y = 2, y_plus = True, y_minus = True),
        MazeSquare(x = 2, y = 3, x_minus = True, y_minus = True),
        MazeSquare(x = 2, y = 4, x_plus = True, y_plus = True, x_minus = True),
        MazeSquare(x = 2, y = 5, y_minus = True),
        MazeSquare(x = 2, y = 6, x_plus = True, x_minus = True),
        MazeSquare(x = 3, y = 1, x_plus = True, x_minus = True),
        MazeSquare(x = 3, y = 2, x_plus = True, y_plus = True),
        MazeSquare(x = 3, y = 3, y_plus = True, y_minus = True),
        MazeSquare(x = 3, y = 4, y_plus = True, x_minus = True, y_minus = True),
        MazeSquare(x = 3, y = 5, y_plus = True, y_minus = True),
        MazeSquare(x = 3, y = 6, x_plus = True, x_minus = True, y_minus = True),
        MazeSquare(x = 4, y = 1, y_plus = True, x_minus = True),
        MazeSquare(x = 4, y = 2, x_minus = True, y_minus = True),
        MazeSquare(x = 4, y = 3, x_plus = True, y_plus = True),
        MazeSquare(x = 4, y = 4, y_minus = True, is_finish = True),
        MazeSquare(x = 4, y = 5, y_plus = True),
        MazeSquare(x = 4, y = 6, x_plus = True, x_minus = True, y_minus = True),
        MazeSquare(x = 5, y = 1, y_plus = True),
        MazeSquare(x = 5, y = 2, y_plus = True, y_minus = True),
        MazeSquare(x = 5, y = 3, x_plus = True, x_minus = True, y_minus = True),
        MazeSquare(x = 5, y = 4, x_plus = True, y_plus = True),
        MazeSquare(x = 5, y = 5, y_plus = True, y_minus = True),
        MazeSquare(x = 5, y = 6, x_minus = True, y_minus = True),
        MazeSquare(x = 6, y = 1, y_plus = True),
        MazeSquare(x = 6, y = 2, y_plus = True, y_minus = True),
        MazeSquare(x = 6, y = 3, y_plus = True, x_minus = True, y_minus = True),
        MazeSquare(x = 6, y = 4, y_plus = True, x_minus = True, y_minus = True),
        MazeSquare(x = 6, y = 5, y_plus = True, y_minus = True),
        MazeSquare(x = 6, y = 6, y_minus = True),
    ]
    return Maze(_squares)

# maze = create_simple_2_to_2_maze()
# maze = create_simple_3_to_3_maze()
maze = create_6_to_6_maze()
simulator_session = SimulatorMazeSolvingSession(maze)
simulator_session.start()