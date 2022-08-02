# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 13:06:06 2022

@author: JEQ
"""

import operator
from enum import Enum
import MineField as obj


class ExplosionException(Exception):
    pass



class Status(Enum):
    CLOSED = 0
    OPEN = 1
    ADJACENT = 2
    ADJACENTCLOSED = 3
    FLAGGED = 'X'
    


class Cell:
    def __init__(self, row, col):
        self.__coordinates = (row,col)
        self.__status = Status.CLOSED
        self.__adjacentMines = 9
        self.__totalTimesUsed = 0
        self.__timesFlagged = 0
        self.__probability =  0 #Or None??
        
        
        
        
        # Reference to next cells (used for doubly linked list)
        self.N = None
        self.E = None
        self.S = None
        self.W = None
        self.NE = None
        self.SE = None
        self.SW = None
        self.NW = None
    
    def setNeighbours(self):
        self.NESW = [self.N, self.E, self.S, self.W]
        self.neighbours = [self.N,self.E,self.S,self.W,self.NE,self.SE,self.SW,self.NW]
        
    def setStatus(self, status):
        self.__status = status
        
    def setProbability(self, probability):
        self.__probability = probability
    
    def setAdjacentMines(self, adjacentMines):
        self.__adjacentMines = adjacentMines
        
    def resetProbabilities(self):
        self.__totalTimesUsed = 0
        self.__timesFlagged = 0
        
    def calculateProbability(self):
        if (self.__totalTimesUsed == 0):
            #print('division by zero; Not correct')
            return
        self.__probability = self.__timesFlagged/self.__totalTimesUsed
    
    def increaseTotalTimesUsed(self):
        self.__totalTimesUsed += 1
        
    def increaseTimesFlagged(self):
        self.__timesFlagged += 1
        
    def getProbability(self):
        return self.__probability
    
    def getStatus(self):
        return self.__status
    
    def getAdjacentMines(self):
        return self.__adjacentMines
    
    def getCoordinates(self):
        return self.__coordinates
        
    
    
    
    
class Solver:
    def __init__(self, width, height, number_of_mines, preferredSubArrayLength = 8):
        self.__width = width
        self.__height = height
        self.__total_cells = width*height
        self.__field = obj.MineField(width = width, height = height , number_of_mines = number_of_mines)
        self.__grid = self.__createGrid()
        
        self.flaggedMineArray = []
        
        self.solved = False
        
        self.__closed = [Status.CLOSED, Status.ADJACENTCLOSED]
        
        self.__number_of_cells_opened = 0
        self.__number_of_cells_flagged = 0
        self.__number_of_cells_closed = self.__width*self.__height
        self.__number_of_mines = number_of_mines 
        
        self.__preferredSubArrayLength = preferredSubArrayLength
        
        
        self.__adjacentOpenedCells = []
        self.__adjacentClosedCells = []
        

    # Create grid and doubly linked list
    def __createGrid(self):
        grid = []
        for row in range(self.__height):
            grid.append([])
            for col in range(self.__width):
                grid[row].append(Cell(row,col))
                
        for row in range(self.__height):
            for col in range(self.__width):
                # East and West
                if(col < self.__width-1):
                    grid[row][col].E = grid[row][col+1]
                    grid[row][col].E.W = grid[row][col]
                
                # South and North
                if(row < self.__height - 1):
                    grid[row][col].S = grid[row+1][col]
                    grid[row][col].S.N = grid[row][col]
                    
                # South East and North West
                if(col < self.__width - 1) and (row < self.__height - 1):
                    grid[row][col].SE = grid[row + 1][col + 1]
                    grid[row][col].SE.NW = grid[row][col]
                 
                # North East and South West
                if(row > 0) and (col < self.__width - 1):
                    grid[row][col].NE = grid[row - 1][col + 1]
                    grid[row][col].NE.SW = grid[row][col]
                
    
        #Set neighbours
        for row in range(self.__height):
            for col in range(self.__width):
                grid[row][col].setNeighbours()
        
        return grid
    
    
    
    def checkIfSolved(self):
        if (self.__number_of_cells_flagged + self.__number_of_cells_opened == self.__total_cells):
                #print("puzzle is solved!! :)")
                self.solved = True
                return True
        elif(self.__number_of_cells_flagged == self.__number_of_mines):
            #print('opening remaining cells')
            self.__openRemainingCells()
            #print("puzzle is solved!! :)")
            self.solved = True
            return True
        return False
                
    ''' Main Solver:
        Consist of:
            - initial guesses at the corners
            - basic solver
            - advanced solver
            - statistical solver       
        '''
    def solve(self):
        # first guesses
        self.__firstGuesses()
  
        # Main solver
        
        totalLoops = 0
        
        while True and totalLoops < 1000:
            totalLoops += 1
            while True:
                if not self.basicSolver():
                    break
            
            if self.checkIfSolved():
                break
            
            if not self.AdvancedSolver():
                self.statisticalSolver()
                
            if self.checkIfSolved():
                break

        if totalLoops >= 1000:
            print('solver probably got stuck')

        return self.flaggedMineArray
        
        
    def __firstGuesses(self):
        starting_coor = [(0,0),(self.__height-1,0), (0,self.__width-1), (self.__height-1,self.__width-1)]
        for coor in starting_coor:
            #print('First guess(es)')
            row = coor[0]
            col = coor[1]
            current_opened_cells = self.__number_of_cells_opened
            self.openCell(self.__grid[row][col])
            if(self.__number_of_cells_opened - current_opened_cells > 1):
                #print('large area opened')
                break
        

    
    def basicSolver(self):
        #print('basic solver')
        solvedCells = False
        for cell in self.__adjacentOpenedCells:
            closedCells = 0
            flaggedCells = 0
            closedCellsArray = []
            
            for i in cell.neighbours:
                if i:
                    if(i.getStatus() in self.__closed):
                        closedCells += 1
                        closedCellsArray.append(i)
                    elif(i.getStatus() == Status.FLAGGED):
                        flaggedCells += 1
                        
                
            #check if number of adjacentmines == flagged --> Open surrounding cells
            if (cell.getAdjacentMines() == flaggedCells):
                solvedCells = True
                for i in closedCellsArray:
                    self.openCell(i)
                self.__adjacentOpenedCells.remove(cell)
            #check if number of closedcells and flagged celsl are equal --> flag closed cells
            elif(cell.getAdjacentMines() == (closedCells + flaggedCells)):
                solvedCells = True
                for i in closedCellsArray:
                    self.flagCell(i)
                self.__adjacentOpenedCells.remove(cell)
            # no closed cells --> Cell is solved
            
            
            elif(closedCells == 0):
                solvedCells = True
                self.__adjacentOpenedCells.remove(cell)
            
                
        return solvedCells


    '''
    Advanced solver: 
        Creates arrays of closed cells that are connected and adjacent
        to opened adjacent cells --> totalOrderedPaths
        These paths are 'traveled' using a subarray of default length of 8.
        On this subarray or subpath backtracking is applied to discover the possibilities
        of flagging cells. The total number of possibilities are tracked and if a cell
        is ALWAYS flagged, it is flagged for real. If it is NEVER flagged, the cell is opened.   
    
    '''
    def AdvancedSolver(self):
        cellsSolved = False
        #print('Advanced Solver')
        
        #Create array with all ADJACENTCLOSED CELLS
        self.__adjacentClosedCells = []
        for row in self.__grid:
            for cell in row:
                if cell.getStatus() == Status.ADJACENTCLOSED:
                    self.__adjacentClosedCells.append(cell)
         
        
        self.__totalOrderedPaths = self.__createOrderedPaths()
        
        
        # Loop through the paths with a smaller array of length X and backtrack these
        for path in self.__totalOrderedPaths:
            self.__walkThrougPathAndBacktrack(path)
        
        # Calculate probability of a cell being a bomb
        for path in self.__totalOrderedPaths:
            for cell in path:
                cell.calculateProbability()
                
        # Opening all cells with 0 probability of being a bomb, and Flag with 100% being bomb
        for path in self.__totalOrderedPaths:
            for cell in path:
                if (cell.getProbability() == 0):
                    if cell.getStatus() in self.__closed:
                        self.openCell(cell)
                        cellsSolved = True
                
                elif (cell.getProbability() == 1):
                    if cell.getStatus() in self.__closed:
                        self.flagCell(cell)
                        cellsSolved = True
         
                
         
        # Reset probabilities if solution is found
        if cellsSolved:
            for path in self.__totalOrderedPaths:
                for cell in path:
                    cell.resetProbabilities()
        
        return cellsSolved
        
    
    
    '''
    Statistical solver:
        When advanced sovler fails, the cell with the greatest/smallest possibility is 
        flagged/opened.
    '''
    def statisticalSolver(self):    
        #print('Statistical Solver')
        
        #Probability of CLOSEDADJACENT cells
        closedAdjacentCell_low_probability = 1
        closedAdjacentCell_high_probability = 0     
        
        closedAdjacentCell_high = None
        closedAdjacentCell_low = None
               
        for path in self.__totalOrderedPaths:
            for cell in path:
                if cell.getStatus() in self.__closed:
                    if(cell.getProbability() > closedAdjacentCell_high_probability):
                        closedAdjacentCell_high_probability = cell.getProbability()
                        closedAdjacentCell_high = cell
                        
                    elif(cell.getProbability() < closedAdjacentCell_low_probability):
                        closedAdjacentCell_low_probability = cell.getProbability()
                        closedAdjacentCell_low = cell
        
        

        # Open cell with lowest possibility as: Low closer to 0 than high closer to 1
    
        if(closedAdjacentCell_low_probability < (1-closedAdjacentCell_high_probability)):
            if closedAdjacentCell_low:
                #print('open cell with a probability of: ' + str(closedAdjacentCell_low_probability))
                self.openCell(closedAdjacentCell_low)
                cellsSolved = True
            
            
        # Flag cell with highest possibility as: high closer to 1 than low closer to 0
        else:
            if closedAdjacentCell_high:            
                #print('flag cell with a probability of: ' + str(closedAdjacentCell_high_probability))
                self.flagCell(closedAdjacentCell_high)
                cellsSolved = True
                

        # Reset probabilities if solution is found
        if cellsSolved:
            for path in self.__totalOrderedPaths:
                for cell in path:
                    cell.resetProbabilities()
                    
            

    def __openRemainingCells(self):
        for row in self.__grid:
            for cell in row:
                if cell.getStatus() in self.__closed:
                    self.openCell(cell)
    
    
    def __walkThrougPathAndBacktrack(self, path):
        
        self.__subArrayLength = self.__preferredSubArrayLength if len(path) > self.__preferredSubArrayLength else len(path)
        
        for i in range(len(path) - self.__subArrayLength + 1):
            self.__subArray = path[i:i + self.__subArrayLength]
            self.__backtrack(0)
    
    
    def __backtrack(self, index):
        options = [Status.FLAGGED, Status.ADJACENTCLOSED]
        
        #Ensure index not out of range
        if(index == len(self.__subArray)):
            return
        
        cell = self.__subArray[index]
        
        for i in options:
            #Check if option is valid
            if(self.__possibleToFlag(cell, i)):
                cell.setStatus(i)
                self.__backtrack(index + 1)
                
                #Final check when last index is filled (to see if all are ok)
                if(index == len(self.__subArray) - 1):
                    
                    if(self.__finalCheck()):                        
                        #Increase times used and times flagged
                        for j in self.__subArray:
                            j.increaseTotalTimesUsed()
                            if (j.getStatus() == Status.FLAGGED):
                                j.increaseTimesFlagged()
        return
                            
                
    
    def __finalCheck(self):      
        for cell in self.__subArray:
            for i in cell.neighbours:
                if i and (i.getStatus() == Status.ADJACENT):
                    
                    # If: All cells are in subarray and adjacent cells MUST equal flagged cells
                    if(self.__useStrictControl(i)):
                        if not (self.__CompareFlaggedCellsToAdjacentMines(i, operator.eq)):
                            return False
                    else:
                        if not (self.__CompareFlaggedCellsToAdjacentMines(i, operator.le)):
                            return False
        return True
    
    '''
    A strict Control is used for the subarray if the cell is surrounded by adjacent closed cells
    It is possible that these cells are simply subarray[1:-1], did not check this.
    '''
    def __useStrictControl(self, cell):
        for i in cell.neighbours:
            if i and (i.getStatus() == Status.ADJACENTCLOSED):
                if (i not in self.__subArray):
                    return False
        return True
    
    def __possibleToFlag(self, cell, status):
        if (status == Status.ADJACENTCLOSED):
            return True
        
        for i in cell.neighbours:
            if i and (i.getStatus() == Status.ADJACENT):
                if not (self.__CompareFlaggedCellsToAdjacentMines(i, operator.lt)):
                    return False
        return True
    
    def __CompareFlaggedCellsToAdjacentMines(self, cell, comparison):
        adjacentMines = cell.getAdjacentMines()
        totalFlagged = 0
        
        for i in cell.neighbours:
            if i and i.getStatus() == Status.FLAGGED:
                totalFlagged += 1
        
        return comparison(totalFlagged,adjacentMines)
    
    
    def __createOrderedPaths(self):
        #Create single path: !! Only use cell with two neighbours --> Easier
        totalOrderedPaths = []
        for startCell in self.__adjacentClosedCells:
            if (self.__getNumberOfNeighboursNESW(startCell) <= 2 and self.__getNumberOfNeighboursNESW(startCell) > 0):
                
                # Create paths from startCell
                totalPaths = []
                for i in startCell.NESW:
                    if i and i.getStatus() == Status.ADJACENTCLOSED:
                        self.__subPath = [startCell] # Start with startCell to ensure the path is created away from the startCell
                        self.__createSubPath(i)
                        totalPaths.append(self.__subPath)
                
                
                if len(totalPaths) == 0:
                    return []
                
                # Create one, unidirectional, totalPaths should consist of 2 arrays.
                if len(totalPaths) > 1:
                    orderedpath = totalPaths[0]
                    totalPaths[1].remove(startCell)
                    for i in totalPaths[1]:
                        if i not in orderedpath:
                            orderedpath.append(i)
                else:
                    orderedpath = totalPaths[0]
                            
                totalOrderedPaths.append(orderedpath)
        return totalOrderedPaths
    
    
    def __getNumberOfNeighboursNESW(self,cell):
        neighbours = 0
        for i in cell.NESW:
            if i and i.getStatus() == Status.ADJACENTCLOSED:
                neighbours += 1
        return neighbours


    def __createSubPath(self, cell):
        if cell in self.__subPath:
            return
        elif cell not in self.__adjacentClosedCells:
            return
        
        self.__subPath.append(cell)
        self.__adjacentClosedCells.remove(cell)
        
        for i in cell.NESW:
            if i and i.getStatus() == Status.ADJACENTCLOSED:
                self.__createSubPath(i)
        return


    def openCell(self, cell):
            row = cell.getCoordinates()[0]
            col = cell.getCoordinates()[1]
            
            if not (cell.getStatus() in self.__closed):
                return
            
            cell.setAdjacentMines(self.__field.sweep_cell(col,row))
            cell.setStatus(Status.OPEN)
            self.__number_of_cells_opened += 1
            self.__number_of_cells_closed -= 1
            
            if(cell.getAdjacentMines() == 0):
                for i in cell.neighbours:
                    if i and (i.getStatus() in self.__closed):
                        self.openCell(i)
            else:
                cell.setStatus(Status.ADJACENT)
                for i in cell.neighbours:
                    if i and(i.getStatus() == Status.CLOSED):
                        i.setStatus(Status.ADJACENTCLOSED)
                self.__adjacentOpenedCells.append(cell)

    def openCellRowCol(self, row, col):
        cell = self.__grid[row][col]
        self.openCell(cell)

    def flagCell(self, cell):
        cell.setStatus(Status.FLAGGED)
        self.__number_of_cells_flagged += 1
        self.__number_of_cells_closed -= 1
        
        self.flaggedMineArray.append(cell.getCoordinates())
        return
    
    
    #--- print functions ---
    def printGrid(self):
        for row in range(self.__height):
            print()
            for col in range(self.__width):
                if(self.__grid[row][col].getStatus() == Status.OPEN):
                    print (' ', end = ' ')
                elif(self.__grid[row][col].getStatus() == Status.ADJACENT):
                    print(self.__grid[row][col].getAdjacentMines(), end = ' ')
                elif(self.__grid[row][col].getStatus() == Status.FLAGGED):
                    print(self.__grid[row][col].getStatus().value, end = ' ')
                else:
                    print(Status.CLOSED.value, end = ' ')
        print()


    def printGridStatus(self):
        for row in range(self.__height):
            print()
            for col in range(self.__width):
                print(self.__grid[row][col].getStatus().value, end = ' ')
        print()



