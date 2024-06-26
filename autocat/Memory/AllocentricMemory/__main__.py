import numpy as np
from .AllocentricMemory import AllocentricMemory
from .Geometry import cell_to_point
from .. import CELL_RADIUS

# Testing Allocentric Memory
# py -m autocat.Memory.AllocentricMemory

allocentric_memory = AllocentricMemory(8, 9, CELL_RADIUS)
# Displaying the hexagonal grid in the console.
print(allocentric_memory)

# print("Cell_to_point(1,1)", cell_to_point(1, 1))
# print("Cell_to_point([1, 1], [1, 2])", cell_to_point(np.array([1, 1]), np.array([1, 2])))
i_range = np.arange(1, 4)
j_range = np.arange(1, 3)
I, J = np.meshgrid(i_range, j_range, indexing='ij')
print("Cell_to_point(I, J)")
print(I)
print(J)
R = cell_to_point(I, J)
print(R)
print(R[1, 1])
error = 0
