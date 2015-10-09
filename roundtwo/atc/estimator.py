'''
Created on Jun 15, 2011

@author: joao
'''

import numpy as np

class Estimator:
        """ Receives departure and arrival node,
        returns estimated time for arrival"""

        def __init__(self,nodeArray):
            self.taxiSpeed = 7.71666667 # 15 knots
            self.nodeArray = nodeArray
            self.sequence = np.array([])
            self.logArray = np.array([])
            self.time = 0.0
            self.timeStep = 1.0
            
#        def findMove(self,cnode):  #finds a sequence for node move, returns false if no new sequence
#            self.previousNode = self.currentNode
#            self.currentNode = cnode
#            
#            connects = self.nodeArray[self.currentNode].connect
#            
#            #removes current and previous node as children
#            connects = np.delete(connects, np.where(connects==self.currentNode))   
#            connects = np.delete(connects, np.where(connects==self.previousNode))
#            
#            if connects != np.array([]):
#                for node in connects:
#                    self.sequence = np.append(self.sequence, node)
#                    if node == self.finalNode:
#                        self.sequence = np.append(self.sequence, node)
#                        return True
#                    else:
#                        self.findMove(node)
#            
#            
#        def optimalMove(self): #finds the optimal sequence for node move
#            self.currentConnections = np.array([])
#            self.currentConnections = self.nodeArray[self.currentNode].connect
#            
#            self.findMove(self.currentNode)
                
                
        def execSequence(self,s_node,seq):
            self.currentNode = s_node
            self.sequence = seq
            
            self.errorStep = 0
            self.totalDistance = 0
            
            for node in self.sequence:    # "node" is next node
                self.errorStep = self.moveTo(node)
                self.currentNode = node
            
            return True
        
        def moveTo(self,node):
            nodeDist = self.nodeDistance(self.currentNode,node)
            self.totalDistance = self.totalDistance + nodeDist
            
            currentX = self.nodeArray[self.currentNode].x
            currentY = self.nodeArray[self.currentNode].y
            
            
            
            
            
        def nodeDistance(self,node1,node2):
            X1 = self.nodeArray[node1].x
            X2 = self.nodeArray[node2].x
            Y1 = self.nodeArray[node1].y
            Y2 = self.nodeArray[node2].y
            
            return np.sqrt(np.square(X2-X1)+np.square(Y2-Y1))

        