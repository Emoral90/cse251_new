'''
Requirements
1. Create a recursive program that finds the solution path for each of the provided mazes.
2. COMMENT every line that you write yourself.
'''

import math
from screen import Screen
from maze import Maze
import cv2
import sys
from cse251functions import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)


# TODO add any functions


def solve(maze):
    """ Solve the maze. The path object should be a list (x, y) of the positions 
        that solves the maze, from the start position to the end position. """

    # TODO add code here
    def dfs(path, row, col):
        # Base case: return true if the end/solution is reached
        if maze.at_end(row, col):
            path.append((row, col))  # Add the final position to the path
            return True
        
        # Mark the current position as visited by changing its color to red
        maze.move(row, col, COLOR)
        
        # Retrieve possible moves
        for next_row, next_col in maze.get_possible_moves(row, col):
            if dfs(path, next_row, next_col):  # Perform recursion with new position
                path.append((row, col))  # Append the position if part of solution
                return True
        
        # If no valid move is found, backtrack and restore the position
        maze.restore(row, col)
        return False

    solution_path = []
    start_row, start_col = maze.get_start_pos()
    dfs(solution_path, start_row, start_col)
    
    # Remember that an object is passed by reference, so you can pass in the 
    # solution_path object, modify it, and you won't need to return it from 
    # your recursion function
    
    return solution_path


def get_solution_path(filename):
    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename)

    solution_path = solve(maze)

    print(f'Number of drawing commands for = {screen.get_command_count()}')

    done = False
    speed = 1
    while not done:
        if screen.play_commands(speed):
            key = cv2.waitKey(0)
            if key == ord('+'):
                speed = max(0, speed - 1)
            elif key == ord('-'):
                speed += 1
            elif key != ord('p'):
                done = True
        else:
            done = True

    return solution_path


def find_paths():
    files = ('verysmall.bmp',
             'verysmall-loops.bmp',
             'small.bmp', 'small-loops.bmp',
             'small-odd.bmp', 'small-open.bmp', 'large.bmp', 'large-loops.bmp')

    print('*' * 40)
    print('Part 1')
    for filename in files:
        print()
        print(f'File: {filename}')
        solution_path = get_solution_path(filename)
        print(f'Found path has length          = {len(solution_path)}')
    print('*' * 40)


def main():
    # prevent crashing in case of infinite recursion
    sys.setrecursionlimit(5000)
    find_paths()


if __name__ == "__main__":
    main()
    create_signature_file("CSE251W25")