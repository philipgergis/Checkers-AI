from BoardClasses import Move
from BoardClasses import Board
from copy import deepcopy
from math import log, sqrt, inf
from random import randint
import time
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():
    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        self.tree = None
        self.time = 0
    
    class Node:
        def __init__(self, turn, wins=0, simulations=0, parent=None, moveMade = None):
            self.wins = wins
            self.simulations = simulations
            self.children = []
            self.parent = parent
            self.moveMade = moveMade
            self.turn = turn
        
        # Calculates UCT value for node. If simulations are 0 returns infinity.
        def calculateUCT(self):
            return inf if self.simulations == 0 else (self.wins/self.simulations) + sqrt(2)*sqrt(log(self.parent.simulations)/self.simulations)
    
    def applyMoves(self, node, board):
        moves = []
        while(node.parent!=None):
            moves.append(node.moveMade)
            node = node.parent
        moves = moves[::-1]
        turn = node.turn
        for move in moves:
            board.make_move(move, turn)
            turn = self.opponent[turn]
        return board
        

    def simulate(self, node, boardSimulation):
        currentTurn = node.turn
        while(boardSimulation.is_win(currentTurn)==0):
            moves = boardSimulation.get_all_possible_moves(currentTurn)
            if(len(moves)!=0):
                index = randint(0,len(moves)-1)
                inner_index =  randint(0,len(moves[index])-1)
                move = moves[index][inner_index]
                boardSimulation.make_move(move,currentTurn)
            currentTurn = self.opponent[currentTurn]
        return boardSimulation.is_win(currentTurn)
        
    
    def backPropogate(self, node, outcome):
        while(node.parent!=None):
            node.simulations+=1
            if outcome == node.turn or (self.color == node.turn and outcome == -1):
                node.wins+=1
            node = node.parent
        node.simulations+=1
        if outcome == node.turn or (self.color == node.turn and outcome == -1):
            node.wins+=1
    
    def output(self, number):
        f = open("text.txt", "a")
        f.write(str(number) +  "\n")
        f.close()

    def get_move(self,move):
        # start time for move
        start = time.time()

        # Determines what color you are by whether or not you made the first move
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1

        # Check for one move
        if len(self.board.get_all_possible_moves(self.color)) == 1 and len(self.board.get_all_possible_moves(self.color)[0]) == 1:
            move = self.board.get_all_possible_moves(self.color)[0][0]
            self.board.make_move(move, self.color)
            return move

        
        # Initial state of the board.
        startingState = self.Node(turn=self.color)
        if self.tree != None:
            for child in self.tree.children:
                if child.moveMade == move:
                    startingState = child
                    break

        # Iterates n times.
        time_gap = 8 if self.col*self.row > 70 or self.time > 390 else 20
        iteration = 0
        while(iteration < 700 and time.time() - start < time_gap):
            targetNode = startingState
            newBoard = deepcopy(self.board)
            
            # Selection
            # Iterate down the tree until you reach a leaf node (a targetNode with no children).
            while(len(targetNode.children) != 0):
                # Get all children and their corresponding UCT valiues of the targetNode.
                childAndUCTList = [(childNode, childNode.calculateUCT()) for childNode in targetNode.children]
                maxNode = childAndUCTList[0][0]
                maxUCT = childAndUCTList[0][1]
                for child, uct in childAndUCTList:
                    # Unexplored node (nodes with 0 simulations) prioritized.
                    if uct == inf:
                        maxNode = child
                        break
                    elif uct > maxUCT:
                        maxNode = child
                        maxUCT = uct
                        
                # Make the targetNode the node with the largest UCT value.
                targetNode = maxNode
                

            # Expansion
            newBoard = self.applyMoves(targetNode, newBoard)
            moves = newBoard.get_all_possible_moves(targetNode.turn)
            for i in range(0, len(moves)):
                for j in range(0, len(moves[i])):
                    targetNode.children.append(self.Node(turn=self.opponent[targetNode.turn], parent = targetNode, moveMade = moves[i][j]))
            # Simulate
            if len(targetNode.children) > 0:
                randomIndex = randint(0, len(targetNode.children)-1)
                child = targetNode.children[randomIndex]
                targetNode = child
                outcome = self.simulate(targetNode, newBoard)
            else:
                outcome = newBoard.is_win(targetNode.turn)
            self.backPropogate(targetNode, outcome)
            iteration+=1



        bestState = startingState.children[0]
        maxWinRate = bestState.wins/bestState.simulations
        for child in startingState.children:
            newWinRate = child.wins/child.simulations
            if newWinRate > maxWinRate:
                maxWinRate = newWinRate
                bestState = child
        move = bestState.moveMade
        self.board.make_move(move, self.color)
        self.tree = bestState
        self.time += time.time() - start
        return move


