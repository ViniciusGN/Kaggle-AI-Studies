#
# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1
#

#
# @file agents.py
#
# @author Régis Clouard.
#

from __future__ import print_function
import random
import copy
import sys
import utils
import numpy as np

class Agent:
    """
    The base class for various flavors of the agent.
    This an implementation of the Strategy design pattern.
    """
    isLearningAgent = False

    def init( self, gridSize ):
        raise Exception("Invalid Agent class, init() not implemented")

    def think( self, percept, action, score, isTraining = False ):
        raise Exception("Invalid Agent class, think() not implemented")

def pause( text):
    if sys.version_info.major >= 3:
        input(text)
    else:
        raw_input(text)

class DummyAgent( Agent ):
    """
    An example of simple Wumpus hunter brain: acts randomly...
    """

    def init( self, gridSize ):
        pass

    def think( self, percept, action, score, isTraining = False ):
        return random.choice(['shoot', 'grab', 'left', 'right', 'forward', 'forward'])


class HumanAgent( Agent ):
    """
    Game version using keyboard to control the agent
    """
 
    def init( self, gridSize ):
        self.state = State(gridSize)
        self.isStarted = False

    def think( self, percept, action, score ):
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """
        if not self.isStarted:
            self.isStarted = True
            return GRAB
        else:
            self.state.updateStateFromPercepts(percept, score)
            self.state.printWorld()
            key = input("Choose action (l, r, f, s, g, c) ? ")
            if key=='r': action = RIGHT
            elif key=='f': action = FORWARD
            elif key=='c': action = CLIMB
            elif key=='s': action = SHOOT
            elif key=='g': action = GRAB
            else: action = LEFT
            self.state.updateStateFromAction(action)
            return action

#######
####### Exercise: Rational Agent
#######
class RationalAgent( Agent ):
    """
    Your smartest Wumpus hunter brain. Uses as a reference for our real work with the learning agent. do not consider
    """

    def init( self, gridSize ):
        self.state = State(gridSize)
        self.goldhasbeenfound = False
        " *** YOUR CODE HERE ***"
        
    def search(self, cell):
        x = cell[0]
        y = cell[1]
        takeAction = True
        for i in range(1,11):
            for j in range(1,11):
                if self.state.getCell(i,j) == SAFE:
                    takeAction = False
        print("Take action ? ", takeAction)
        
        for cell in self.state.getCellNeighbors(x, y):
            if self.state.getCell(cell[0], cell[1]) == SAFE:
                return cell
        
        visitedCells = []
        dangerousCell = []
        
        for cell in self.state.getCellNeighbors(x, y):
            if self.state.getCell(cell[0], cell[1]) == VISITED:
                visitedCells.append(cell)
            if self.state.getCell(cell[0],cell[1]) in [PITP, WUMPUSP, WUMPUSPITP]:
                dangerousCell.append(cell)
        
        print("Visited cells : ", visitedCells)
        print("Dangerous cells : ", dangerousCell)
        
        # Random actions
        if takeAction and dangerousCell:
            return random.choice(dangerousCell)
        if visitedCells:
            return random.choice(visitedCells)
        
    # Here to go back to 1,1. Problem I had it could be stuck in a loop
    def goToStart(self):
        current_position = (self.state.posx, self.state.posy)
        if current_position == (1, 1):
            return CLIMB
        
        # Needed this for a cycle check, this checks if the attribute already exists so it only initializes once
        if not hasattr(self, "visit_count"):
            self.visit_count = {}   
        
        self.visit_count[current_position] = self.visit_count.get(current_position, 0) + 1

        neighbors = self.state.getCellNeighbors(self.state.posx, self.state.posy)
        
        visited_neighbors = [
            neighbor for neighbor in neighbors
            if self.state.getCell(neighbor[0], neighbor[1]) == VISITED
        ]
        
        if visited_neighbors:
            visited_neighbors.sort(
                key=lambda cell: abs(cell[0] - 1) + abs(cell[1] - 1)
            )

            if self.visit_count[current_position] > 3:
                alternative_neighbors = [
                    neighbor for neighbor in visited_neighbors
                    if self.visit_count.get(neighbor, 0) <= 3
                ]

                if alternative_neighbors:
                    visited_neighbors = alternative_neighbors

            return visited_neighbors[0]
        
        return current_position

    def choose_best_action(self):
        print("initial state : ",self.state.posx, self.state.posy)
        availableCell = self.search((self.state.posx, self.state.posy))

        print("availables cells: ",availableCell)
        x = availableCell[0] - self.state.posx
        y = availableCell[1] - self.state.posy
        for i in range(len(DIRECTION_TABLE)):
            if (x,y) == DIRECTION_TABLE[i]:
                direction = i
        print(x,y,direction)
        return self.state.fromDirectionToAction(direction)
    
    def evaluation(self, x, y):
        if (self.state.getCell(x, y) == GOLD):
            return 1000
        elif (self.state.getCell(x, y) == VISITED):
            return -5 #self.cpt
        elif (self.state.getCell(x, y) == WUMPUS or self.state.getCell(x, y) == PIT):
            return -1000
        elif (self.state.getCell(x, y) == WUMPUSP or self.state.getCell(x, y) == PITP):
            return -10
        elif (self.state.getCell(x, y) == WALL):
            return -1000000
        self.cpt = -2
        return -1
        
    def think(self, percept, action, score):
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """
        self.state.updateStateFromPercepts(percept, score)

        self.state.printWorld()
        if not self.goldhasbeenfound:
            if self.state.getCell(self.state.posx, self.state.posy) == GOLD:
                self.goldhasbeenfound = True
                self.state.setCell(self.state.posx, self.state.posy, SAFE)
                return GRAB

            action = self.choose_best_action()
        else:
            if (self.state.posx, self.state.posy) != (1, 1):
                cell = self.goToStart()
                x = cell[0] - self.state.posx
                y = cell[1] - self.state.posy
                for i in range(len(DIRECTION_TABLE)):
                    if (x, y) == DIRECTION_TABLE[i]:
                        direction = i
                        break
                action = self.state.fromDirectionToAction(direction)
            else:
                action = CLIMB

        if action == RIGHT:
            self.state.direction = (self.state.direction + 1) % 4
        elif action == LEFT:
            self.state.direction = (self.state.direction - 1) % 4

        if action == FORWARD:
            self.state.posx = self.state.getForwardPosition(self.state.posx, self.state.posy, self.state.direction)[0]
            self.state.posy = self.state.getForwardPosition(self.state.posx, self.state.posy, self.state.direction)[1]

        return action
        

#######
####### Exercise: Learning Agent
#######
class LearningAgent( Agent ):
    """
    Your smartest Wumpus hunter brain.
    """
    isLearningAgent = True
    goldhasbeenfound = False
    visited_cells_counter = 0
    
    def init( self, gridSize ):
        self.state = State(gridSize)
        self.isTraining = False
        self.alpha = 0.9             # Learning rate
        self.gamma = 0.975           # Discount factor
        self.epsilon = 0.1           # Exploration rate
        self.epsilon_decay = 0.95    # Exploration rate decay
        self.min_epsilon = 0.1       # Minimum exploration rate
        self.q_table = np.zeros((gridSize, gridSize, 4, 6))      # gridSize states (positions) and directions, 6 actions
        self.visitedCells = np.zeros((gridSize, gridSize))
        self.dangerousCells = []
                
    def choose_action( self, state, q_table, epsilon ):
        if random.uniform(a=0, b=1) < epsilon:                              # Exploration
                return random.choice(range(6))
        else:
            return np.argmax(q_table[state[0], state[1], state[2], :])  # Exploitation
    
    def evaluation(self, x, y):
        """
        Evaluates cell (x, y) and returns the reward.
        """
        # Phase 1: Before you find the gold
        if not self.goldhasbeenfound:
            if self.state.getCell(x, y) == GOLD:
                return 1000
            elif self.state.getCell(x, y) == VISITED:
                return -5
            elif self.state.getCell(x, y) == WUMPUS or self.state.getCell(x, y) == PIT:
                return -1000
            elif self.state.getCell(x, y) == WUMPUSP or self.state.getCell(x, y) == PITP:
                return -10 
            elif self.state.getCell(x, y) == WALL:
                return -1000000
            return -1

        else:
            if (x, y) == (1, 1):
                return 10000
            if self.visitedCells[x, y] == 0:
                return -100
            if self.state.getCell(x, y) in [WUMPUS, PIT, WALL]:
                return -1000
            return -5
        
    def navigate_to_initial_position(self):
        """
        Navigates to the starting position (1, 1) considering safe and visited cells.
        """
        target = (1, 1)
        current_position = (self.state.posx, self.state.posy)

        # Heuristic: prioritize safe and visited cells
        def is_safe_and_visited(x, y):
            if 0 <= x < len(self.visitedCells) and 0 <= y < len(self.visitedCells):
                return self.visitedCells[x, y] == 1 and (x, y) not in self.dangerousCells
            return False

        # Check possible actions
        if current_position[0] > target[0] and is_safe_and_visited(current_position[0] - 1, current_position[1]):
            return LEFT
        if current_position[0] < target[0] and is_safe_and_visited(current_position[0] + 1, current_position[1]):
            return RIGHT
        if current_position[1] > target[1] and is_safe_and_visited(current_position[0], current_position[1] - 1):
            return FORWARD
        if current_position[1] < target[1] and is_safe_and_visited(current_position[0], current_position[1] + 1):
            return FORWARD

        # If there is no direct path, explore safe and visited cells
        for x_offset, y_offset, action in [(-1, 0, LEFT), (1, 0, RIGHT), (0, -1, FORWARD), (0, 1, FORWARD)]:
            next_x, next_y = current_position[0] + x_offset, current_position[1] + y_offset
            if is_safe_and_visited(next_x, next_y):
                return action

        # If there are no valid actions, stay still or make a default decision
        return CLIMB if current_position == target else None

    def think(self, percept, action, score, isTraining):
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """
        ACTIONS = [RIGHT, LEFT, FORWARD, CLIMB, SHOOT, GRAB]
        if not self.isTraining:
            self.isTraining = True
        else:
            self.state.updateStateFromPercepts(percept, score)
            current_state = (self.state.posx, self.state.posy, self.state.direction)
            action_index = self.choose_action(current_state, self.q_table, self.epsilon)
            reward = self.evaluation(self.state.posx, self.state.posy)
            
            next_state = self.state.posx, self.state.posy, self.state.direction
            old_q_value = self.q_table[self.state.posx, self.state.posy, self.state.direction, action_index]
            
            max_future_q = np.max(self.q_table[next_state[0], next_state[1], next_state[2], :])
            
            # Q-table update (Q-learning formula)
            new_q_value = old_q_value + self.alpha * (reward + self.gamma * max_future_q - old_q_value)
            self.q_table[self.state.posx, self.state.posy, self.state.direction, action_index] = new_q_value
            
            # Updates the exploration rate (epsilon) for the next step
            if self.epsilon > self.min_epsilon:
                self.epsilon *= self.epsilon_decay
            
            # Mark gold as found
            if self.state.getCell(self.state.posx, self.state.posy) == GOLD:
                self.goldhasbeenfound = True
                return GRAB

            # Update visited cells
            if self.visitedCells[self.state.posx, self.state.posy] == 0:
                self.visitedCells[self.state.posx, self.state.posy] = 1
            else:
                self.visited_cells_counter += 1

            # Register dangerous cells
            if self.state.getCell(self.state.posx, self.state.posy) in [WUMPUS, PIT]:
                self.dangerousCells.append((self.state.posx, self.state.posy))
                
            return ACTIONS[action_index]
            
#######
####### Exercise: Environment
#######

WALL='#'
UNKNOWN='?'
WUMPUSP='w'
WUMPUS='W'
PITP='p'
PIT='P'
WUMPUSPITP='x'
SAFE=' '
VISITED='.'
GOLD='G'

RIGHT  ='right'
LEFT = 'left'
FORWARD = 'forward'
CLIMB = 'climb'
SHOOT = 'shoot'
GRAB = 'grab'

DIRECTION_TABLE = [(0, -1), (1, 0), (0, 1), (-1, 0)] # North, East, South, West

class State():
    def __init__( self, gridSize ):
        self.size = gridSize
        self.worldmap = [[((y in [0, gridSize - 1] or  x in [0, gridSize - 1]) and WALL) or UNKNOWN
                          for x in range(gridSize) ] for y in range(gridSize)]
        self.direction = 1
        self.posx = 1
        self.posy = 1
        self.action = 'left'
        self.setCell(self.posx, self.posy, self.agentAvatar())
        self.wumpusIsKilled = False
        self.goldIsGrabbed = False
        self.wumpusLocation = None
        self.arrowInventory = 1
        self.score = 0
        " *** YOUR CODE HERE ***"

    def printWorld( self ):
        """
        For debugging purpose.
        """
        for y in range(self.size):
            for x in range(self.size):
                print(self.getCell(x, y) + " ", end=' ')
            print()

    def getCell( self, x, y ):
        return self.worldmap[x][y]

    def setCell( self, x, y, value ):
        self.worldmap[x][y] = value

    def getCellNeighbors( self, x, y ):
        return [(x + dx, y + dy) for (dx,dy) in DIRECTION_TABLE]
    
    def getForwardPosition( self, x, y, direction ):
        (dx, dy) = DIRECTION_TABLE[direction]
        return (x + dx, y + dy)

    def fromDirectionToAction( self, direction ):
        if direction == self.direction:
            return FORWARD
        elif direction == (self.direction + 1) % 4:
            return RIGHT
        elif direction == (self.direction + 2) % 4:
            return RIGHT
        else:
            return LEFT

    def canGoForward(self):
        x1, y1 = self.getForwardPosition(self.posx, self.posy, self.direction)
        square = self.getCell(x1, y1)
        return square == VISITED

    def isGoal(self):
        return (self.posx, self.posy) == (1,1) and self.arrowInventory == 0 and self.goldIsGrabbed

    def updateStateFromPercepts( self, percept, score ):
        """
        Updates the current environment with regards to the percept information.
        """
        self.score = score
        #  Update neighbours
        self.setCell(self.posx, self.posy, VISITED)
        for (x, y) in self.getCellNeighbors(self.posx, self.posy):
            square = self.getCell(x, y)
            if square == WALL or square == VISITED or square == SAFE:
                continue
            if percept.stench and percept.breeze:
                if square == UNKNOWN and self.wumpusLocation == None:
                    self.setCell(x,y, WUMPUSPITP)
                else:
                    self.setCell(x,y, PITP)
            elif percept.stench and not percept.breeze:
                if square == UNKNOWN or square == WUMPUSPITP:
                    if  self.wumpusLocation == None:
                        self.setCell(x, y, WUMPUSP)
                    else:
                        self.setCell(x, y, SAFE)
                elif square == PITP:
                    self.setCell(x, y, SAFE)
            elif not percept.stench and percept.breeze:
                if square == UNKNOWN  or square == WUMPUSPITP:
                    self.setCell(x, y, PITP)
                elif square == WUMPUSP:
                    self.setCell(x, y, SAFE)
            else:
                self.setCell(x, y, SAFE)

        # Gold
        if percept.glitter:
            self.setCell(self.posx, self.posy, GOLD)

        # Kill Wumpus?
        if percept.scream:
            if self.wumpusLocation is not None:
                self.setCell(self.wumpusLocation[0], self.wumpusLocation[1], SAFE)
            self.wumpusIsKilled = True
        
        # Confirm Wumpus or Pit.
        for y in range(self.size):
            for x in range(self.size):
                if self.getCell(x, y) == VISITED:
                    wumpusCount = 0
                    for (px, py) in self.getCellNeighbors(x, y):
                        if self.getCell(px, py) in [WUMPUSP, WUMPUSPITP]:
                            wumpusCount += 1
                    if wumpusCount == 1: # Confirmer WUMPI+USP et supprimer les autres WUMPUSP (il n'ya qu'un WUMPUS).
                        for (px, py) in self.getCellNeighbors(x, y):
                            if self.getCell(px, py) in [WUMPUSP, WUMPUSPITP]:
                                self.setCell(px, py, WUMPUS)
                                self.wumpusLocation = (px, py)
                                for y1 in range(self.size):
                                    for x1 in range(self.size):
                                        if self.getCell(x1, y1) == WUMPUSP:
                                            self.setCell(x1, y1, SAFE)
                                        if self.getCell(x1, y1) == WUMPUSPITP:
                                            self.setCell(x1, y1, PITP)
                                break
                    pitCount = 0
                    for (px, py) in self.getCellNeighbors(x, y):
                        if self.getCell(px, py) in [PIT, PITP, WUMPUSPITP]:
                            pitCount += 1
                    if pitCount == 1:
                        for (px, py) in self.getCellNeighbors(x, y):
                            if self.getCell(px, py) in [PIT, PITP, WUMPUSPITP]:
                                self.setCell(px, py, PIT)
                                break
        return self
    
    def updateStateFromAction( self, action ):
        self.action = action
        if self.action == GRAB:
            self.goldIsGrabbed = True
            self.setCell(self.posx, self.posy, VISITED)
        elif self.action == LEFT:
            self.direction = (self.direction + 3) % 4
        elif self.action == RIGHT:
            self.direction = (self.direction + 1) % 4
        elif self.action == FORWARD:
            self.setCell(self.posx, self.posy, VISITED)
            self.posx, self.posy = self.getForwardPosition(self.posx, self.posy, self.direction)
        self.setCell(self.posx, self.posy, self.agentAvatar())

    def agentAvatar( self ):
        if self.direction == 0:
            return "^"
        elif self.direction == 1:
            return ">"
        elif self.direction == 2:
            return "v"
        else:
            return "<"

    def getWumpusPlace( self ):
        return self.wumpusLocation

    def isShootingPositionFor( self, x, y ):
        if self.direction == 0 and self.posx == x and self.posy > y:
            return True
        if self.direction == 1 and self.posy == y and self.posx < x:
            return True
        if self.direction == 2 and self.posx == x and self.posy < y:
            return True
        if self.direction == 3 and self.posy == y and self.posx > x:
            return True
        return False
