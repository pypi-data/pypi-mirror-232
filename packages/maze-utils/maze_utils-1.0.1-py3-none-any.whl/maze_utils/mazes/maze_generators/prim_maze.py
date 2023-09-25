import random
from typing import List, Generator

import numpy as np
import numpy.typing as npt
from scipy.spatial import cKDTree

from .base import MazeBase


class PrimMaze(MazeBase):
    def __init__(self):
        super().__init__()
        self.loop: bool = True
        self.walls: List[List[int]] = []
        self.passage: List[List[int]] = []
        self.maze: npt.NDArray[np.int_] = np.array([], dtype=int)

    def make_maze(self, n_x: int, n_y: int) -> Generator[npt.NDArray[np.int_], None, npt.NDArray[np.int_]]:
        self.maze = np.full([n_x + 1, n_y + 1], 1, dtype=int)
        x, y = random.randint(1, n_x - 1), 1
        self.passage.append([x, y])
        self.maze[x, y] = 0
        self._add_walls(x, y)

        for i in range(n_x * n_y * 10):
            pos, wall = self._pick_wall()
            if pos is None:
                break
            x, y = pos
            self.maze[x, y] = 0
            self.walls.pop(wall)
            self._add_walls(x, y)
            self.passage.append([x, y])

            if len(self.passage) > (n_x * n_y):
                break  # prevents weird mazes with only a few squares
            yield self.maze
        return self.maze

    @staticmethod
    def _prepare_final(maze: npt.NDArray[np.int_]) -> npt.NDArray[np.int_]:
        maze_temp = np.ones([maze.shape[0] + 1, maze.shape[1] + 1], dtype=int)
        maze_temp[1:-1, 1:-1] = maze[:-1, :-1]
        return maze_temp

    def _add_walls(self, x: int, y: int) -> None:
        ghost_maze = np.zeros([self.maze.shape[0] + 2, self.maze.shape[1] + 2], dtype=int)
        ghost_maze[1:-1, 1:-1] = self.maze

        if ghost_maze[x + 1, y + 2]:
            self.walls.append([x, y + 1])
        if ghost_maze[x + 1, y]:
            self.walls.append([x, y - 1])
        if ghost_maze[x + 2, y + 1]:
            self.walls.append([x + 1, y])
        if ghost_maze[x, y + 1]:
            self.walls.append([x - 1, y])

    def _pick_wall(self):
        iterations = 0
        while True:
            high = len(self.walls)
            iterations += 1
            if iterations > high * 2:
                return None, None
            rand_wall = random.randint(0, high - 1)

            x_wall, y_wall = self.walls[rand_wall]
            x, y = self._find_nearest_passage([x_wall, y_wall])
            diff_x = x - x_wall
            diff_y = y - y_wall

            try:
                next_over = self.maze[x_wall - diff_x, y_wall - diff_y]
                if diff_x != 0:
                    next_right = self.maze[x_wall, y_wall - 1]
                    next_left = self.maze[x_wall, y_wall + 1]
                    next_right_over = self.maze[x_wall - diff_x, y_wall - 1]
                    next_left_over = self.maze[x_wall - diff_x, y_wall + 1]
                else:
                    next_right = self.maze[x_wall + 1, y_wall]
                    next_left = self.maze[x_wall - 1, y_wall]
                    next_right_over = self.maze[x_wall + 1, y_wall - diff_y]
                    next_left_over = self.maze[x_wall - 1, y_wall - diff_y]

            except IndexError:
                continue

            if not (next_over and next_right and next_left and next_left_over and next_right_over):
                self.walls.pop(rand_wall)
            else:
                return self.walls[rand_wall], rand_wall

    def _find_nearest_passage(self, pos: List[int]) -> List[int]:
        _, index = cKDTree(self.passage).query(pos)
        return self.passage[int(index)]
