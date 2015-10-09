'''
Created on Oct 29, 2011

@author: joao
'''

import numpy as np

class AuxCalculator:
    '''
    Contains auxiliary methods
    '''


    def __init__(self,nodeArray):
        '''
        Constructor
        '''
        
        self.nodeArray = nodeArray
        
    
    def nodeDistance(self,node1,node2):
        X1 = self.nodeArray[node1].x
        X2 = self.nodeArray[node2].x
        Y1 = self.nodeArray[node1].y
        Y2 = self.nodeArray[node2].y
            
        return np.sqrt(np.square(X2-X1)+np.square(Y2-Y1))
    
    
    
    def substate2orto(self,substate):
        
        X_node_I = self.nodeArray[substate[0]].x
        Y_node_I = self.nodeArray[substate[0]].y
        
        X_node_F = self.nodeArray[substate[1]].x
        Y_node_F = self.nodeArray[substate[1]].y
        
        dX_percent = (X_node_F - X_node_I)*substate[2]   #expects distance-based percent!!!
        dY_percent = (Y_node_F - Y_node_I)*substate[2]
        
        X = X_node_I + dX_percent
        Y = Y_node_I + dY_percent
        
        return X,Y
        
        
    def convert2tuple(self,state):
        #print ' State Array before conversion to tuple: ' + np.str(state)
        
        state_tup = []
        for substate in state:
            state_tup.append(tuple(substate))
        
        state_tup = tuple(state_tup)
        
        #print ' State Tuple after conversion from array: ' + np.str(state_tup)
        
        return state_tup
        
    def convert2list(self,state):
        
        state_list = []
        for substate in state:
            state_list.append(list(substate))
        
#        print ' State List after conversion is: ' + np.str(state_list)
        
        return state_list
    
    
    def getLastIntKey(self,dict):
        
        last_key = 0
        
        for key in dict.iterkeys():
            if key > last_key:
                last_key = key
            
        return last_key
    
    
    def concatenateDict(self,dict,add_dict):
        
        last_key_in_dict = self.getLastIntKey(dict)
        current_key = last_key_in_dict + 1
        
        for key in add_dict.iterkeys():
            dict[current_key] = add_dict[key]
            current_key = current_key + 1
        
        return dict
    
    def append2Dict(self,dict,object):
        
        last_key_in_dict = self.getLastIntKey(dict)
        current_key = last_key_in_dict + 1
        
        dict[current_key] = object
        
        return dict
        
    
    def getDecidingSubstateIndex(self,state):
        
        index = 0
        
        for substate in state:
            if substate[2] == 1.0:
                return index
            index = index + 1
        
        return -1
    
    
    def containsArray(self,array,container):
        
#        print ' Container is: \n' + np.str(container)
#        print ' Array to check is: \n' + np.str(array)
        
        for subarray in container:
            if (subarray==array):
                return True
        
        return False