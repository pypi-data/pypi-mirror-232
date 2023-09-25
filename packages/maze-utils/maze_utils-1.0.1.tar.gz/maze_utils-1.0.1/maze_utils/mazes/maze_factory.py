from enum import Enum
from typing import Generator

import numpy as np
import numpy.typing as npt

from .maze_generators import DepthFirstMaze, KruskalMaze, PrimMaze, RandomMaze, WilsonMaze


class MazeTypes(Enum):
    DEPTH_FIRST = DepthFirstMaze
    KRUSKAL = KruskalMaze
    PRIM = PrimMaze
    RANDOM = RandomMaze
    WILSON = WilsonMaze


class MazeFactory:
    def __init__(self, n_x: int, n_y: int, maze_type: MazeTypes) -> None:
        self.n_x = n_x
        self.n_y = n_y
        self.maze_type = maze_type
        self._final_maze = np.zeros([self.n_x, self.n_y], dtype=int)

    def step_by_step(self) -> Generator[npt.NDArray[np.int_], None, npt.NDArray[np.int_]]:
        generator = self.maze_type.value()

        maze: npt.NDArray[np.int_] = np.zeros([self.n_x, self.n_y], dtype=int)
        for maze in generator.generate(self.n_x, self.n_y):
            yield maze

        self._final_maze = maze
        return maze

    def final(self) -> npt.NDArray[np.int_]:
        generator = self.maze_type.value()
        maze: npt.NDArray[np.int_] = np.zeros([self.n_x, self.n_y], dtype=int)
        for maze in generator.generate(self.n_x, self.n_y):
            pass

        self._final_maze = maze
        return maze
