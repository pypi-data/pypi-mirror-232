from random import randint, random
from typing import Generator

import numpy.typing as npt
from numpy import full, arange, reshape, ravel, ones, int_

from .base import MazeBase


class KruskalMaze(MazeBase):
    def __init__(self):
        super().__init__()
        self.num_cells_last: int = 0
        self.maze: npt.NDArray[int_] = full([], 1, dtype=int)
        self._repeat_iterations: int = 0

    def make_maze(self, n_x: int, n_y: int) -> Generator[npt.NDArray[int_], None, npt.NDArray[int_]]:
        self.num_cells_last = -1
        len_x = n_x + 4
        len_y = n_y + 4
        self.maze = full([len_x, len_y], 1, dtype=int)
        self._make_walls()
        self._make_sets()
        self._repeat_iterations = 0
        while True:
            self._join_cells()
            if self._check_final():
                break
            yield self.maze
        return self.maze

    def _make_walls(self):
        self.walls = arange(0, self.maze.size, dtype=int)
        self.walls = reshape(self.walls, self.maze.shape)
        for i in range(self.maze.shape[0]):
            if (i % 2) == 1:
                self.walls[i, :] = -1
        for j in range(self.maze.shape[1]):
            if (j % 2) == 1:
                self.walls[:, j] = -1
        self.walls[:, 0] = self.walls[:, -1] = -1
        self.walls[0, :] = self.walls[-1, :] = -1

    def _make_sets(self):
        self.sets = []
        for i in range(self.walls.shape[0]):
            for j in range(self.walls.shape[1]):
                wall_id = self.walls[i, j]
                self.sets.append({wall_id})

    def _pick_wall(self):
        while True:
            i = randint(2, self.walls.shape[0] - 3)
            j = randint(2, self.walls.shape[1] - 3)
            wall_id = self.walls[i, j]
            if (
                (self.walls[i + 1, j] == -1)
                and (self.walls[i - 1, j] == -1)
                and (self.walls[i, j + 1] == -1)
                and (self.walls[i, j - 1] == -1)
            ):
                continue
            if wall_id == -1:
                return i, j

    def _check_wall(self):
        id_1 = None
        id_2 = None
        i_1 = None
        i_2 = None
        j_1 = None
        j_2 = None

        for i in range(5):
            i, j = self._pick_wall()
            set_id_left = self.walls[i - 1, j]
            set_id_right = self.walls[i + 1, j]
            set_id_up = self.walls[i, j + 1]
            set_id_down = self.walls[i, j - 1]

            set_left = self.sets[set_id_left]
            set_right = self.sets[set_id_right]
            set_up = self.sets[set_id_up]
            set_down = self.sets[set_id_down]

            rand_flt = random()
            if rand_flt <= 0.5:
                sym_diff = set_left ^ set_right
                if (set_id_left in sym_diff) and (set_id_right in sym_diff):
                    id_1 = set_id_left
                    id_2 = set_id_right
                    i_1, j_1 = i - 1, j
                    i_2, j_2 = i + 1, j

            else:
                sym_diff = set_up ^ set_down
                if (set_id_up in sym_diff) and (set_id_down in sym_diff):
                    id_1 = set_id_up
                    id_2 = set_id_down
                    i_1, j_1 = i, j + 1
                    i_2, j_2 = i, j - 1

            if id_1 is None:
                continue
            self.walls[i, j] = -2

            self.maze[i, j] = 0
            self.maze[i_1, j_1] = 0
            self.maze[i_2, j_2] = 0

            return id_1, id_2

        return None, None

    def _check_final(self) -> bool:
        flat = ravel(self.maze)
        num_cells: int = len(flat[flat == 0])
        if num_cells == self.num_cells_last:
            self._repeat_iterations += 1
        if self._repeat_iterations > 20:
            return True
        if num_cells != self.num_cells_last:
            self._repeat_iterations = 0
            self.num_cells_last = num_cells
        return False

    def _join_cells(self) -> None:
        id_1, id_2 = self._check_wall()
        if id_1 is None:
            return

        for i in range(self.maze.shape[0]):
            for j in range(self.maze.shape[1]):
                if self.maze[i, j] == 0:
                    if self.maze[i + 1, j] == 0:
                        self.sets[self.walls[i, j]].update(self.sets[self.walls[i + 2, j]])
                        self.sets[self.walls[i + 2, j]].update(self.sets[self.walls[i, j]])
                    if self.maze[i - 1, j] == 0:
                        self.sets[self.walls[i, j]].update(self.sets[self.walls[i - 2, j]])
                        self.sets[self.walls[i - 2, j]].update(self.sets[self.walls[i, j]])
                    if self.maze[i, j + 1] == 0:
                        self.sets[self.walls[i, j]].update(self.sets[self.walls[i, j + 2]])
                        self.sets[self.walls[i, j + 2]].update(self.sets[self.walls[i, j]])
                    if self.maze[i, j - 1] == 0:
                        self.sets[self.walls[i, j]].update(self.sets[self.walls[i, j - 2]])
                        self.sets[self.walls[i, j - 2]].update(self.sets[self.walls[i, j]])

    @staticmethod
    def _prepare_final(maze: npt.NDArray[int_]) -> npt.NDArray[int_]:
        maze_temp = ones([maze.shape[0] - 2, maze.shape[1] - 2], dtype=int)
        maze_temp[1:-1, 1:-1] = maze[2:-2, 2:-2]
        return maze_temp
