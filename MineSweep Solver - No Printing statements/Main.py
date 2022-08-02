# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 22:51:17 2022

@author: JEQ
"""

import Solver as MineSweepSolver

def returnFlaggedMines(flaggedMines):
    return flaggedMines

'''
Input: width (columns), height (rows), number of bombs, subarrayLength (default at 8)
higher subarrayLength should lead to better results, but is more computational --> Backtracking along a 
longer array.

flaggedMines contains the coordinates (row,col) in a tuple.
solved is a boolen whether the puzzle is solved
'''

width = 30
height = 16
number_of_mines = 99

solverObject = MineSweepSolver.Solver(width,height,number_of_mines)


try:
    solverObject.solve()
    solved = solverObject.solved
    flaggedMines = solverObject.flaggedMineArray
except Exception:
    flaggedMines = solverObject.flaggedMineArray
    solved = solverObject.solved
    #print('puzzle not solved')

    


## -- Various ways of displaying/returning results (not sure what is required) -- ##

# print FlaggedMines
print(flaggedMines)

# return FlaggedMines
# returnFlaggedMines()


# print final grid, you can turn this on
#solverObject.printGrid()