from enum import Enum
from typing import Generator

import numpy.typing as npt
from numpy import int_, zeros

from .solver_generators import AStarSolver, BidirectionalDijkstraSolver, DijkstraSolver


class SolverTypes(Enum):
    A_STAR = AStarSolver
    BIDIRECTIONAL_DIJKSTRA = BidirectionalDijkstraSolver
    DIJKSTRA = DijkstraSolver


class SolverFactory:
    def __init__(self, solver_type: SolverTypes) -> None:
        self.solver_type = solver_type

    def step_by_step(self, maze: npt.NDArray[int_]) -> Generator[npt.NDArray[int_], None, npt.NDArray[int_]]:
        generator = self.solver_type.value()
        solution: npt.NDArray[int_] = zeros([], dtype=int)
        for solution in generator.solve(maze):
            yield solution
        return solution

    def final(self, maze: npt.NDArray[int_]) -> npt.NDArray[int_]:
        generator = self.solver_type.value()
        solution: npt.NDArray[int_] = zeros([], dtype=int)
        for solution in generator.solve(maze):
            pass
        return solution
