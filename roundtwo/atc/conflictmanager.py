'''
Created on Nov 28, 2011

@author: joao
'''

from AuxCalculator import AuxCalculator
import numpy as np

class ConflictManager:
    '''
    Conflict Detection and Handling
    '''


    def __init__(self,nodeArray,infcost):
        '''
        Constructor
        '''
        
        self.nodeArray = nodeArray
        self.infcost = infcost
        
        
        self.aux = AuxCalculator(self.nodeArray)
        
        
    def simpleManage(self,successor_dict, current_state, g_cost_inc_dict, g_cost_dict, came_from):
        #if the current_state has conflict, simply return False successors and g_cost_incs
        # therefore the current_state is closed and has no children
        
        current_state_dict = dict()
        current_state_dict[0] = current_state
        
        hasConflictDict, conflictDict = self.checkConflicts(current_state_dict)
        
        if hasConflictDict[0]:
            return False,False
        
        #if the deciding substate in current_state has a successor whose final node is a hold node
        # it must generate an additional successor in which that substate deaccelerates into that hold
        # and waits for the next aircraft (other substate) to pass at the observed node.
        
        decision_substate_index = self.aux.getDecidingSubstateIndex(current_state)
        
        #if there is no decision (and no conflict) in current_state (for initial state for example)
        # the original states should be returned
        if decision_substate_index < 0:
            return successor_dict, g_cost_inc_dict
        
        for key in successor_dict.iterkeys():
            isHold, holdNodeNumber = self.isHoldType(successor_dict[key], decision_substate_index)
            
            if isHold:
                hold_successor,hold_g_cost_inc = self.generateHoldSuccessor(current_state, holdNodeNumber, decision_substate_index)
                successor_dict = self.aux.append2Dict(successor_dict, hold_successor)
                g_cost_inc_dict = self.aux.append2Dict(g_cost_inc_dict, hold_g_cost_inc)
        
        # if all else fails returns original successors and g_costs_inc, else it returns the modified
        # successors with added holding states
        return successor_dict,g_cost_inc_dict
    
    
    def generateHoldSuccessor(self,current_state,hold_node_number,decision_substate_index,g_costs_dict):
        
        
        return hold_successor, hold_g_cost_inc 
        
    def manage(self,states_dict, current_state, g_cost_inc_dict, g_cost_dict, came_from):
        #manages conflicts with back jumping
        
        hasConflictDict, conflictDict = self.checkConflicts(states_dict)
        
        
        hasConflict = False
        for conflict_test in hasConflictDict.itervalues():
            if conflict_test:
                hasConflict = True
                
        
        if hasConflict:
            new_states_dict, new_g_cost_inc_dict = self.solveConflicts(states_dict, g_cost_inc_dict, hasConflictDict,conflictDict,g_cost_dict,came_from)
            return new_states_dict, new_g_cost_inc_dict
        
        return False,False
        
    
    
    def solveConflicts(self,states_Dict,g_costs_inc_Dict,hasConflict_Dict,conflict_Dict,g_costs_Dict,came_from_Dict):
        # returns the successors, added with new possible solution successors and their g_cost_incs
        
        # gets corresponding holding states for each of the conflicting successors
        for state_key in hasConflict_Dict.iterkeys(): #iterates successors
            if hasConflict_Dict[state_key]:  # if successor has conflict
                g_costs_inc_Dict[state_key] = self.infcost  # its increase in g_cost is huge
                states_Dict, g_costs_inc_Dict = self.getSolveStates(states_Dict,g_costs_inc_Dict,conflict_Dict,g_costs_Dict,came_from_Dict,state_key) # backtracks and finds best hold states for each conflicting substate (at least 2 ofc)
        
        return states_Dict, g_costs_inc_Dict
    
    
    def getSolveStates(self,states_Dict,g_costs_inc_Dict,conflict_array_Dict,g_cost_Dict,came_from_Dict,conflict_state_key):
        # generates new successor states for conflict_state which aim to solve the conflicts within
        # and adds them to current successor and g_costs_inc dict
        
        deep_hold_state_Dict = self.getDeepHoldStates(states_Dict[conflict_state_key],conflict_array_Dict[conflict_state_key],came_from_Dict)
        
        solve_state_Dict, solve_g_costs_inc_Dict = self.generateSolveStates(deep_hold_state_Dict,g_cost_Dict,came_from_Dict,conflict_state_key)
        
        states_Dict, g_costs_inc_Dict = self.addSolveStates(states_Dict,g_costs_inc_Dict,solve_state_Dict,solve_g_costs_inc_Dict)
        
        return states_Dict, g_costs_inc_Dict
        
    def getDeepHoldStates(self,conflict_state,conflict_array,came_from_Dict):
        # returns the deepest hold state for each substate in conflict that is in conflict_state
        
        hold_state_Dict = dict()
        
        conflict_state_key = self.aux.convert2tuple(conflict_state)
        
        substate_index = 0
        
        for substate_has_conflict in conflict_array:
            if substate_has_conflict:
                # the parent state that originated the conflict
                parent_state = self.getConflictParent(conflict_state,substate_index,came_from_Dict)
                parent_state_key = self.aux.convert2tuple(parent_state)
                
                init_parent_state_key = parent_state_key
                
                isHoldType = self.isHoldType(parent_state,substate_index)
                
                while not isHoldType:
                    if not came_from_Dict[parent_state_key] in came_from_Dict.iterkeys(): #if it doesnt find any hold type nodes
                        parent_state = came_from_Dict[init_parent_state_key]  # assumes parent of init_parent as a hold node (dangerous and possibly blocking)
                        break
                    
                    parent_state = self.getConflictParent(parent_state,substate_index,came_from_Dict)
                    parent_state_key = self.aux.convert2tuple(parent_state)
                    
                    isHoldType = self.isHoldType(parent_state,substate_index)
                
                hold_state_Dict[substate_index] = parent_state
            
            substate_index = substate_index + 1
        
        return hold_state_Dict
        
    def isHoldType(self,state,substate_index):
        # checks if conflict substate is on a hold node
        final_node = state[substate_index][1]
        if self.nodeArray[final_node].type == 'hold':
            return True, final_node
        
        return False, -1
    
    def getConflictParent(self,state,substate_index,came_from_Dict):
        # gets previous state to state, so that substate_index has to decide
        
        state_key = self.aux.convert2tuple(state)
        
        previous_state = came_from_Dict[state_key]
        
        while not (previous_state[substate_index][2] == 1.0):
            previous_state_key = self.aux.convert2tuple(previous_state)
            
            if previous_state_key not in came_from_Dict.keys(): #returns False if it couldnt find parent
                return False
            
            previous_state = came_from_Dict[previous_state_key]
        
        return previous_state
        
        
    def generateSolveStates(self,hold_state_Dict,g_costs_Dict,came_from_Dict,conflict_state_key):
        # generates Solve States from hold_state_Dict and generates the corresponding g_costs_inc_Dict
        
        solve_states_Dict = dict()
        solve_g_costs_inc_Dict = dict()
        
        init_state = came_from_Dict[conflict_state_key]
        init_state_key = self.aux.convert2tuple(init_state)
        
        
        for hold_state_key in hold_state_Dict.iterkeys():
            #gets previous decision state to hold (for conflicting substate - index is same as key)
            solve_state = self.getConflictParent(hold_state_Dict[hold_state_key], hold_state_key, came_from_Dict)
            solve_state_key = self.aux.convert2tuple(solve_state)
            
            # state that tries to solve conflict is put in a dict and returned
            solve_states_Dict[hold_state_key] = solve_state
            
            # its g_cost_inc is negative! (its shallower in the search) its simply the difference of g_cost of the solve_state and init_state (that originated the successor with conflict)
            solve_g_costs_inc_Dict[hold_state_key] = g_costs_Dict[solve_state_key] - g_costs_Dict[init_state_key]
            
        return solve_states_Dict, solve_g_costs_inc_Dict
    
    
    def addSolveStates(self,states_Dict,g_costs_inc_Dict,solve_state_Dict,solve_g_costs_inc_Dict):
        
        last_states_Dict_key = self.aux.getLastIntKey(states_Dict)
        
        current_key = last_states_Dict_key + 1
        
        for solve_state_key in solve_state_Dict.iterkeys():
            states_Dict[current_key] = solve_state_Dict[solve_state_key]
            g_costs_inc_Dict[current_key] = solve_g_costs_inc_Dict[solve_state_key]
            
            current_key = current_key + 1
        
        return states_Dict,g_costs_inc_Dict
    
        
    def checkConflicts(self,states):
        
        hasConflict = dict()
        conflictDict = dict()
        
        for state_key in states.iterkeys():
            conflictDict[state_key] = self.violatesTol(states[state_key],self.conflict_tol)
        
        for conflict_state_key in conflictDict.iterkeys():
            if conflictDict[conflict_state_key].any():
                hasConflict[conflict_state_key] = True
                break
        
        return hasConflict, conflictDict
    
    
    def violatesTol(self,state,tol):
        
        state_pos = dict()
        conflictArray = np.array([])
        
        i = 0
        
        for substate in state:
            state_posX,state_posY = self.aux.substate2orto(substate)
            state_pos[i] = np.array([state_posX,state_posY])
            conflictArray = np.append(conflictArray, False)
            i = i+1
        
        j = 0
        
        for key in state_pos:
            for other_key in state_pos:
                if other_key > key:
                    if np.sqrt(np.square(state_pos[key][0]-state_pos[other_key][0])+np.square(state_pos[key][1]-state_pos[other_key][1]))<tol:
                        conflictArray[key] = True
                        conflictArray[other_key] = True
        
        return conflictArray
    
    
    def checkWarnings(self,state):
        warning = self.aux.violatesTol(state,self.warning_tol)
        
        return warning