'''
Requirements
1. Create a recursive, multithreaded program that finds the exit of each maze.
2. COMMENT every line that you write yourself.
   
Questions:
1. It is not required to save the solution path of each maze, but what would
   be your strategy if you needed to do so?
   > 
   I would have to save the solution path as a list to each thread, update it recursively, and store it in a shared variable when the goal is found like in last week's reading
   >
2. Is using threads to solve the maze a depth-first search (DFS) or breadth-first search (BFS)?
   Which search is "better" in your opinion? You might need to define better. 
   (see https://stackoverflow.com/questions/20192445/which-procedure-we-can-use-for-maze-exploration-bfs-or-dfs)
   >
   This multithreaded solution behaves like DFS since each thread explores a single path deeply before backtracking, but with a concurrent twist
   >
'''

import math
import threading
from screen import Screen
from maze import Maze
import sys
import cv2
from cse251functions import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)
COLORS = (
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (128, 0, 0),
    (128, 128, 0),
    (0, 128, 0),
    (128, 0, 128),
    (0, 128, 128),
    (0, 0, 128),
    (72, 61, 139),
    (143, 143, 188),
    (226, 138, 43),
    (128, 114, 250)
)

# Globals
current_color_index = 0
thread_count = 0
stop = False


def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color

def thread_solve(maze, row, col, lock, color):
    """ Recursive function to explore maze using threads """
    global thread_count, stop
    
    # Stop if another thread found the exit
    if stop:
        return
    
    # Mark the current position as visited with the initial color
    maze.move(row, col, color)
    
    # If we reached the end, signal all threads to stop no matter where they are
    if maze.at_end(row, col):
        with lock:
            stop = True
        return
    
    # Get possible moves
    moves = maze.get_possible_moves(row, col)
    
    # Spawn new threads at each new fork in the road
    threads = []
    for i in range(1, len(moves)):  # Start from 1 to reserve first move for this thread
        next_row, next_col = moves[i]
        new_color = get_color()  # Assign a unique color
        # Guard the thread_count with your life
        with lock:
            thread_count += 1
        # Create thread, append it to the list, and start it
        new_thread = threading.Thread(target=thread_solve, args=(maze, next_row, next_col, lock, new_color))
        threads.append(new_thread)
        new_thread.start()

    # The current thread takes the first move in the list (if available)
    if moves:
        next_row, next_col = moves[0]
        thread_solve(maze, next_row, next_col, lock, color)  # Current thread continues

    # Wait for all newly spawned threads to complete before backtracking
    for t in threads:
        t.join()

    # Go back to initial position to indicate backtracking only if the maze has not been solved yet
    if not stop:
        maze.restore(row, col)
    
    # for t in threads:
    #     t.join()
    # 
    # maze.restore(row, col)

def solve_find_end(maze):
    """ finds the end position using threads.  Nothing is returned """
    # When one of the threads finds the end position, stop all of them
    # TODO - add code here
    global thread_count, stop
    stop = False
    thread_count = 1
    # Create lock and initial color for the recursive threads in thread_solve()
    t_lock = threading.Lock()
    init_color = get_color()
    
    # Get the starting position and launch the first thread
    start_row, start_col = maze.get_start_pos()
    thread_solve(maze, start_row, start_col, t_lock, init_color)


def find_end(filename, delay):

    global thread_count

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    print(f'Number of drawing commands = {screen.get_command_count()}')
    print(f'Number of threads created  = {thread_count}')

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


def find_ends():
    files = (
        ('verysmall.bmp', True),
        ('verysmall-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False)
    )

    print('*' * 40)
    print('Part 2')
    for filename, delay in files:
        print()
        print(f'File: {filename}')
        find_end(filename, delay)
    print('*' * 40)


def main():
    # prevent crashing in case of infinite recursion
    sys.setrecursionlimit(5000)
    find_ends()


if __name__ == "__main__":
    main()
    create_signature_file("CSE251W25")
