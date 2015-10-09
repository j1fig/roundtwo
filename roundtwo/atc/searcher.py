'''
Created on Jun 25, 2011

@author: joao
'''

import numpy as np
from Aircraft import *
from DynamicSimulator import *
from AuxCalculator import *
from Node import *
from ConflictManager import *
from heapq import heappop, heappush
from ubuntuone.syncdaemon.fsm.fsm import hash_dict
from termcolor import colored
import debug
from time import clock


class Searcher:
    '''
    Conducts graph-search algorithms
    '''

    def __init__(self,nodeArray,connectArray,aircraftArray):
        '''
        Constructor
        '''
        self.nodeArray = nodeArray
        self.connectArray = connectArray
        self.aircraftArray = aircraftArray
        
        self.infcost = 100000
        self.nominal_speed = 7.71666667
        self.virtualtime = 30
        self.conflict_tol = 30
        self.warning_tol = 60
        
        self.optimalRoute = np.array([])
        
        self.aux = AuxCalculator(self.nodeArray)
        self.sim = DynamicSimulator(self.nodeArray,self.nominal_speed)
        self.confman = ConflictManager(self.nodeArray,self.infcost)
        
        
        # PERFORMANCE VARIABLES INIT
        self.backtrack_counter = 0
        self.nodes_generated = 0
        self.init_calculations = 0
        self.node_time_estimate = 0.0
        self.avg_expand_time = 0.0
        self.avg_nodefinish_time = 0.0
        self.avg_heurist_calc_time = 0.0
        self.avg_indexSearch_calc_time = 0.0
        self.numberIndexSearch = 0
        
        self.initHeuristic()
        self.initStateSpace()
        
        
    def initHeuristic(self):
        self.constructGraph()
        
        D = dict()
        P = dict()
        self.heuristic = {'vertex':{'neighbor': 'edge_length'}}
        
        for node in self.nodeGraph:
            D,P = self.Dijkstra(self.nodeGraph, node)
            if debug.debug and debug.heuristic_debug:
                print 'for node: ' + np.str(node) + ' heuristic dict is: ' +np.str(D)
            self.heuristic[node] = D
        
        self.heuristic.pop('vertex')
        
        return True
    
    def constructGraph(self):
        #generates nested hash table of nodes and their connections for heuristic
        
        tempGraph = {'vertex':{'neighbor': 'edge_length'}}
        for node in self.nodeArray.itervalues():
            tempNeighbors = dict()
            for connect in self.connectArray:
                if node.number == connect[0]:
                    #if connect[0] == connect[1]: #if it is a virtual node (for hold)
                    #    tempNeighbors[connect[1]] = self.virtualtime
                    #else:
                    tempNeighbors[connect[1]] = self.aux.nodeDistance(connect[0], connect[1])/(self.nominal_speed)  #time-based heuristic
                                                #OPTIMISTIC TIME (MAX SPEED THROUGH SHORTEST DISTANCE
                    #print 'node ' + np.str(node.number) + ' associated with node ' + np.str(connect[1])
            
            tempGraph[node.number] = tempNeighbors
                    
        self.nodeGraph = tempGraph
        
        tempGraph.pop('vertex')
        #print self.nodeGraph
        
        return True
    
    def Dijkstra(self,G,start,end=None):
        """takes as input a graph, coded as nested dicts {vertex: {neighbor: edge length}}"""
        D = {}   # dictionary of final distances
        P = {}   # dictionary of predecessors
        Q = [(0,None,start)]  # heap of (est.dist., pred., vert.)
        while Q:
            dist,pred,v = heappop(Q)
            if v in D:
                continue  # tuple outdated by decrease-key, ignore
            D[v] = dist
            P[v] = pred
            for w in G[v]:
                #print G[v][w]
                heappush(Q, (D[v] + G[v][w], v, w))
        return (D,P)
    
    def initStateSpace(self):
        
        # substate are [node_i,node_f,percent,speed,heading]
        
        self.state = np.array([[0,0,0.0,0.0,0.0,1]])
        #i=0
        for key in self.aircraftArray.iterkeys():
            self.state = np.concatenate((self.state,np.array([[self.aircraftArray[key].node_I,self.aircraftArray[key].node_F,self.aircraftArray[key].percent,self.aircraftArray[key].speed,self.aircraftArray[key].heading,self.aircraftArray[key].command]])),axis=0)
            #i = i+1
        
        self.state = np.delete(self.state, 0, axis=0)
        
        self.initialstate = self.state
        
#        print '\n      Normal state is \n'
#        print self.state
#        
#        print '\n      Hashable state is  \n'
#        print self.state_hashable
        
        self.goalstate = np.array([[0,0,0.0,0.0,0.0,-1]])
        
        #i=0
        for key in self.aircraftArray.iterkeys():
            self.goalstate = np.concatenate((self.goalstate,np.array([[self.aircraftArray[key].destination,self.aircraftArray[key].destination,0.0,0.0,0.0,-1]])),axis=0)
            #i = i+1
        
        self.goalstate = np.delete(self.goalstate, 0, axis=0)
        
        self.solution = dict()
        
        for key in self.aircraftArray.iterkeys():
            self.solution[key]=np.array([])
        
        
    
    def optimizeMultiRoutes(self,algorithm_sel=0):
        routes = dict()
        
        if debug.debug and debug.performance_debug:
            start_time = clock()
            self.node_start_time = start_time
        
        
        if algorithm_sel == 0:
            self.AStar()
        elif algorithm_sel == 1:
            self.recursiveBestFirst_M()
        
        if debug.debug and debug.performance_debug:
            search_time = clock()
        
        if debug.debug and debug.performance_debug:
            if algorithm_sel == 0:
                print '\n              A-STAR SEARCH PERFORMANCE\n'
            elif algorithm_sel == 1:
                print '\n        RECURSIVE BEST-FIRST SEARCH PERFORMANCE\n'
            
            print ' Number of backtrackings: ' + np.str(self.backtrack_counter)
            print ' Number of nodes generated: ' + np.str(self.nodes_generated)
            print '\n Search took ' + np.str(search_time-start_time) + ' seconds'
            print ' Average time per node: ' + np.str(round((search_time-start_time)/self.nodes_generated,5))
            print ' Estimated time per node: ' + np.str(round(self.node_time_estimate,5))
            
            print '\n Average node expansion time: ' + np.str(round(self.avg_expand_time,5))
            print ' Average heuristic calc time: ' + np.str(round(self.avg_heurist_calc_time,5))
            print ' Average index search time (contained in heuristic calc): ' + np.str(round(self.avg_indexSearch_calc_time*(self.numberIndexSearch/self.nodes_generated),5))
            print ' Average expansion time percent: ' + np.str(round((self.avg_expand_time/self.node_time_estimate)*100,2)) + ' %'
            print ' Average heuristic calc time percent: ' + np.str(round((self.avg_heurist_calc_time/self.node_time_estimate)*100,2)) + ' %'
            print ' Average index search time percent (contained in heuristic percent): ' + np.str(round((self.avg_indexSearch_calc_time/self.node_time_estimate)*100*(self.numberIndexSearch/self.nodes_generated),2)) + ' % \n'
        
        
        #code for removal of extra nodes in solution
        for key in self.solution.iterkeys():
            #print "For aircraft " + np.str(key) + " solution was " + np.str(self.solution[key])
            
            route = np.array([])
            i=1
            route = np.insert(route, 0, self.aircraftArray[key].node_I)  #gets route start node
            for sol_node in self.solution[key]:
                if not sol_node==route[-1]:  #only puts in route new nodes
                    route = np.append(route, sol_node)
                i = i+1
            
            #print route
            routes[self.aircraftArray[key]] = route
        
        print ' route solution is: '
        for route in routes.itervalues():
            print route
        #for sol_node in sol_states:
        #    for aircraft in self.aircraftArray.itervalues():
        
        return routes
    
    def AStar(self):
        self.A_Star(self.state, self.goalstate)
    
    
    def A_Star(self,start_node,goal):
        #===========================================================================================
        #     Performs A-Star search
        #===========================================================================================
        # for the dicts a universal way of distinguishing nodes had to be developed so the keys for
        # the dicts correspond to the tuple conversion of the np.arrays (since these are non-hashable)
        
        
        if debug.debug and debug.performance_debug:
            self.nodes_generated = 1
        
        start_node = self.aux.convert2list(start_node)
        goal = self.aux.convert2list(goal)
        
        start_node_h = self.aux.convert2tuple(start_node)
        goal_h = self.aux.convert2tuple(goal)
        
        closed = []
        open = [start_node]
        
        
        came_from = dict()
        
        g_cost = dict()
        h_cost = dict()
        f_cost = dict()
        
        g_cost[start_node_h] = 0.0
        h_cost[start_node_h] = self.state_heuristic(start_node, goal)
        f_cost[start_node_h] = g_cost[start_node_h] + h_cost[start_node_h]
        
#        print 'best node is : ' + np.str(open[0])
#        print 'np array of goal is: ' + np.str(np.array(goal_h))
        
        while open:
            #the best node is always is always in the first position of open (sorted by f-costs)
            if debug.debug and debug.performance_debug:
                start_time = clock()
                self.nodes_generated = self.nodes_generated + 1
                self.node_time_estimate = (((self.nodes_generated-1)*self.node_time_estimate) + (start_time - self.node_start_time))/self.nodes_generated
                self.node_start_time = start_time
            
            if debug.debug and debug.search_iter_debug:
                print '   New iteration '
                print ' Open Set Size: ' + np.str(np.size(open, axis=0))
                print ' Closed Set Size: ' + np.str(np.size(closed, axis=0))
            
            
            if debug.debug and debug.search_debug:
                print '.......................................................'
                print '                   NODE STARTED \n'
                print '\n      Open Set is     :\n'
                for state in open:
                    for substate in state:
                        print substate
                    state_key = self.aux.convert2tuple(state)
                    print ' f-cost:   ' + np.str(f_cost[state_key])
                    print '\n'
                
                        
            best_node = open[0]
            best_node_h = self.aux.convert2tuple(open[0])
            
            if debug.debug and (debug.search_debug or debug.search_iter_debug):
                print '\n Best node is : \n'
                for substate in best_node:
                    print substate
            
            if (best_node_h==goal_h):
                i=0
                for key in self.aircraftArray.iterkeys():
                    #print " Inserting map node " + np.str(successors[bestnode_index][i][1]) + " into aircraft " + np.str(key) + " solution"
                    self.solution[key] = np.insert(self.solution[key], 0, best_node[i][1])
                    i = i+1
                    
                return self.reconstructPath(came_from,came_from[goal_h])
            
            # deletes node to expand (best_node) from open set - which is in the first position (0)
            if debug.debug and debug.search_debug:
                print ' deleting current node from Open Set...'
            del open[0]
            
            # inserts it into closed set
            if debug.debug and debug.search_debug:
                print ' inserting current node in Closed Set...'
            closed.append(best_node)
            
            
            if debug.debug and debug.search_debug:
                print ' expanding current node for successors...'
            node_to_expand = np.array(best_node)
            
            if debug.debug and debug.performance_debug:
                expandI_time = clock()
            
            #expands best node
            successors, g_cost_inc = self.expand_M(node_to_expand)
            
            if debug.debug and debug.performance_debug:
                expandF_time = clock()
                self.init_calculations = self.init_calculations + 1
                self.avg_expand_time = (((self.init_calculations-1)*self.avg_expand_time) + (expandF_time - expandI_time))/self.init_calculations
            
            if debug.debug and debug.search_debug:
                print '\n Successors are: \n'
                for successor in successors.itervalues():
                    for substate in successor:
                        print substate
                    print '\n'
            
            #successors, g_cost_inc = self.confman.simpleManage(successors, node_to_expand, g_cost_inc, g_cost, came_from)
            
            current_g_cost = g_cost[best_node_h]
            
            if debug.debug and debug.performance_debug:
                heuristI_time = clock()
            
            for key in successors.iterkeys():
                successor_h = self.aux.convert2tuple(successors[key])
                
                curr_successor = self.aux.convert2list(successors[key])
                
                if debug.debug and debug.search_debug:
                    print ' Successor being processed: \n'
                    for substate in curr_successor:
                        print substate
#                    print '\n Closed Set is: \n'
#                    for state in closed:
#                        for substate in state:
#                            print substate
#                        state_key = self.aux.convert2tuple(state)
#                        print ' f-cost:   ' + np.str(f_cost[state_key])
#                        print '\n'
                
                if curr_successor in closed:
                    if debug.debug and debug.search_debug:
                        print '\n Successor in Closed Set. Continuing...'
                    continue
                
                tentative_g_cost = current_g_cost + g_cost_inc[key]
                
                # If successor is not yet open, add it to open
                if not curr_successor in open:
                    tentative_is_better = True
                elif tentative_g_cost < g_cost[successor_h]:
                    tentative_is_better = True
                else:
                    tentative_is_better = False
                
                if tentative_is_better:
                    # gets successor current Open index, in case its necessary to delete it
                    if debug.debug and debug.performance_debug:
                        indexSearchI_time = clock()
                        self.numberIndexSearch = self.numberIndexSearch + 1
                    if debug.debug and debug.search_debug:
                        print '\n getting delete Open Set Index in case its needed...'
                    open_delete_index = self.getOpenIndex(open,f_cost,successor_h)
                    if debug.debug and debug.search_debug:
                        print ' Open Set Delete Index was: ' + np.str(open_delete_index)
                    if debug.debug and debug.performance_debug:
                        indexSearchF_time = clock() 
                        self.avg_indexSearch_calc_time = (((self.numberIndexSearch-1)*self.avg_indexSearch_calc_time) + (indexSearchF_time - indexSearchI_time))/self.numberIndexSearch
                    
                    came_from[successor_h] = best_node_h
                    
                    g_cost[successor_h] = tentative_g_cost
                    h_cost[successor_h] = self.state_heuristic(successors[key], goal)
                    f_cost[successor_h] = g_cost[successor_h] + h_cost[successor_h]
                    
                    # gets what should be the new position in Open, due to the change in f-cost
                    if debug.debug and debug.performance_debug:
                        indexSearchI_time = clock()
                        self.numberIndexSearch = self.numberIndexSearch + 1
                    if debug.debug and debug.search_debug:
                        print '\n getting insert Open Set Index...'
                    open_insert_index = self.getOpenIndex(open,f_cost,successor_h)
                    if debug.debug and debug.search_debug:
                        print ' Open Set Insert Index was: ' + np.str(open_insert_index)
                    if debug.debug and debug.performance_debug:
                        indexSearchF_time = clock()
                        self.avg_indexSearch_calc_time = (((self.numberIndexSearch-1)*self.avg_indexSearch_calc_time) + (indexSearchF_time - indexSearchI_time))/self.numberIndexSearch
                    
                    if not curr_successor in open: # if successor is not in open, it simply adds it
                        if debug.debug and debug.search_debug:
                            print '\n Successor not yet in Open Set. Adding now...'
                        open.insert(open_insert_index,curr_successor)
                        
                        if debug.debug and debug.search_debug:
                            print '\n      New Open Set is     :\n'
                            for state in open:
                                for substate in state:
                                    print substate
                                state_key = self.aux.convert2tuple(state)
                                print ' f-cost:   ' + np.str(f_cost[state_key])
                                print '\n'
                    else: # else it updates its position in Open (had worse f-cost)
                        if debug.debug and debug.search_debug:
                            print '\n Successor already in Open Set. Updating it now...'
                        
                        if open_delete_index <0:
                            print ' WARNING OPEN INDEX DELETE ERROR! NEEDS BETTER HANDLING!'
                        del open[open_delete_index]
                        open.insert(open_insert_index,curr_successor)
            
            if debug.debug and debug.performance_debug:
                heuristF_time = clock() 
                self.avg_heurist_calc_time = (((self.init_calculations-1)*self.avg_heurist_calc_time) + (heuristF_time - heuristI_time))/self.init_calculations
            
            
            if debug.debug and debug.search_debug:
                f_cost_i = 0
                bad_sorts = 0
                open_size = 0
                for open_state in open:
                    open_state_key = self.aux.convert2tuple(open_state)
                    f_cost_f = f_cost[open_state_key]
                    if f_cost_f < f_cost_i:
                        bad_sorts = bad_sorts + 1
                        print ' THE FOLLOWING F-COST IS UNORDERED!!!'
                        
                    f_cost_i = f_cost_f
                    print ' f:  ' + np.str(f_cost_i)
                    open_size = open_size + 1
                
                print '\n  Open size is: ' + np.str(open_size)
                print '\n  Bad sortings made: ' + np.str(bad_sorts)
            
            if debug.debug and debug.search_debug:
                print '\n  ...node finished!'
                print '.......................................................\n'
                
        return False
        
    def getOpenIndex(self,open,f_cost,node_key):
        # returns the index in Open in which the node should be placed, using f-cost sort
        
        open_size = np.size(open, axis=0)
        
        if debug.debug and debug.search_debug:
            print ' last_index for openIndex is ' + np.str(open_size)
        
        if open_size == 0: # if Open Set is empty
            if debug.debug and debug.search_debug:
                print ' Open Set empty! Returning first position...'
            return 0
        
        if open_size == 1: # if Open Set only has one node
            open_key = self.aux.convert2tuple(open[0])
            
            if not f_cost.__contains__(node_key):
                if debug.debug and debug.search_debug:
                    print ' f_cost does not contain present key. open_delete_index will be -1'
                    print ' warning: if called for Inserting Index something is wrong!'
                return -1
            
            if f_cost[node_key] < f_cost[open_key]:
                return 0
            else:
                return 1
        
        for index in range(open_size):
            open_key_for_index = self.aux.convert2tuple(open[index])
            
            if not f_cost.__contains__(node_key):
                if debug.debug and debug.search_debug:
                    print ' f_cost does not contain present key. open_delete_index will be -1'
                    print ' warning: if called for Inserting Index something is wrong!'
                return -1
            
            if debug.debug and debug.search_debug:
                print ' successor f- cost is: ' + np.str(f_cost[node_key])
                print ' open node f-cost for comparison is: ' + np.str(f_cost[open_key_for_index])
            
            if f_cost[node_key] < f_cost[open_key_for_index]:
                if debug.debug and debug.search_debug:
                    print ' openIndex returned index: ' + np.str(index)
                return index
        if debug.debug and debug.search_debug:
            print ' returning the last position!'
        return (open_size)
    
    def reconstructPath(self,came_from,current_node):
        
        #print np.str(came_from)
        
        if current_node in came_from.iterkeys():
            i=0
            for key in self.aircraftArray.iterkeys():
                #print " Inserting map node " + np.str(successors[bestnode_index][i][1]) + " into aircraft " + np.str(key) + " solution"
                self.solution[key] = np.insert(self.solution[key], 0, current_node[i][1])
                i = i+1
            
            return self.reconstructPath(came_from, came_from[current_node])
        else:
            i=0
            for key in self.aircraftArray.iterkeys():
                #print " Inserting map node " + np.str(successors[bestnode_index][i][1]) + " into aircraft " + np.str(key) + " solution"
                self.solution[key] = np.insert(self.solution[key], 0, current_node[i][1])
                i = i+1
            
            return True
    
    
    def recursiveBestFirst_M(self):
        return self.RBFS_M(self.goalstate,self.state,0.0,self.infcost)
    
    def RBFS_M(self,goal,cnode,g_cnode,f_limit):
        
        if debug.debug and debug.performance_debug:
            start_time = clock()
            self.nodes_generated = self.nodes_generated + 1
            self.node_time_estimate = (((self.nodes_generated-1)*self.node_time_estimate) + (start_time - self.node_start_time))/self.nodes_generated
            self.node_start_time = start_time
        
        if debug.debug and debug.search_debug:
            print '\n\nCURRENT F-LIMIT: ' + np.str(f_limit)
            print 'CURRENT STATE:'
            print cnode
        if (cnode==goal).all():
            #print ' Reached the goal!'
            #print 'Current node is: ' + np.str(cnode)
            #print 'Goal node was: ' + np.str(goal) + '\n'
            i=0
            for key in self.aircraftArray.iterkeys():
                self.solution[key] = np.insert(self.solution[key], 0, cnode[i][1])
                i = i+1
            return [True,-1]
        
        successors = dict()
        f_cost = dict()
        g_cost_inc = dict()
        g_cost = dict()
        
        if debug.debug and debug.performance_debug:
            expandI_time = clock()
        
        successors,g_cost_inc = self.expand_M(cnode)
        
        if debug.debug and debug.performance_debug:
            expandF_time = clock()
            self.init_calculations = self.init_calculations + 1
            self.avg_expand_time = (((self.init_calculations-1)*self.avg_expand_time) + (expandF_time - expandI_time))/self.init_calculations
            
        
        #print ' g_cnode is: ' + np.str(g_cnode)
        #print 'successors are: '
        #print successors
        
        if not successors:
            print 'no successors for node' + np.str(cnode)
            return [False, self.infcost]
        
        if debug.debug and debug.performance_debug:
            heuristI_time = clock()
        
        #print 'current goal is: ' + np.str(goal)
        h_cnode = self.state_heuristic(cnode,goal)
        f_cnode = g_cnode + h_cnode
        
        for s in successors.iterkeys():
            g_cost[s] = g_cnode + g_cost_inc[s]
            h_cost = self.state_heuristic(successors[s],goal)
            
            f_cost[s] = np.max([(g_cost[s]+h_cost),f_cnode])   #this was commented while numeric error isnt solved!
            
            
            #f_cost[s] = (g_cost[s]+h_cost)               #these were error-testing lines
            #print 'difference is: ' + np.str(round((g_cost[s]+h_cost)-f_cnode,4))
            
            if (g_cost[s]+h_cost) < f_cnode and debug.debug and debug.search_debug:
                print '\n probably made a poor choice:'
                print ' g(s) + h(s) was: ' + np.str(round(g_cost[s],4)) + ' + ' + np.str(round(h_cost, 4)) + ' = ' + np.str(round((g_cost[s]+h_cost), 4))
                print '   f_cnode was: ' + np.str(round(f_cnode,4))
            
            #conflict = self.checkConflicts(successors[s])
            
            #if conflict:
                #f_cost[s] = self.infcost
                #print '\n                   CONFLICT!!!  THOU HAVE BEEN WARNED\n'
            
            if debug.debug and debug.search_debug:
                print '\n     FOR SUCCESSOR STATE    \n' + np.str(successors[s]) + '\n f-cost is: ' + np.str(round(f_cost[s],4))
                print ' g(s) + h(s) was: ' + np.str(round(g_cost[s],4)) + ' + ' + np.str(round(h_cost, 4)) + ' = ' + np.str(round((g_cost[s]+h_cost), 4)) + '   f_cnode was: ' + np.str(round(f_cnode,4))
                print ' used g_cost_inc of: ' + np.str(g_cost_inc[s])
        #print 'reached the loop'
        
        if debug.debug and debug.performance_debug:
            heuristF_time = clock() 
            self.avg_heurist_calc_time = (((self.init_calculations-1)*self.avg_heurist_calc_time) + (heuristF_time - heuristI_time))/self.init_calculations
        
        while True:
            bestnode_index = self.getBestNode(successors,f_cost)
            
            if f_cost[bestnode_index] > f_limit:
                if debug.debug and debug.search_debug:
                    print colored('Found better solution. Unwinding...','red')
                if debug.debug and debug.performance_debug:
                    self.backtrack_counter = self.backtrack_counter + 1 
                return [False, f_cost[bestnode_index]]
            
            altnode_index = self.getAltNode(successors,f_cost)
            
            if debug.debug and debug.search_debug:
                print 'current best node is: \n' + np.str(successors[bestnode_index])
                if altnode_index>=0:
                    print 'current alternative node is: \n' + np.str(successors[altnode_index])
            
            returned = []
            
            #code in case there is no alternative node
            altcost = self.infcost
            if altnode_index >= 0:
                altcost = f_cost[altnode_index]
                if debug.debug and debug.search_debug:
                    print 'altcost used: ' + np.str(altcost)
            else:
                if debug.debug and debug.search_debug:
                    print 'altcost not being passed or no alternate node!!!'
            
            returned = self.RBFS_M(goal, successors[bestnode_index], g_cost[bestnode_index], np.min([f_limit,altcost]))
            
            if returned[1] > 0:
                f_cost[bestnode_index] = returned[1]
            
            if returned[0] != False:
                #print ' inserted in solution : ' + np.str(successors[bestnode_index])
                i=0
                for key in self.aircraftArray.iterkeys():
                    #print " Inserting map node " + np.str(successors[bestnode_index][i][1]) + " into aircraft " + np.str(key) + " solution"
                    self.solution[key] = np.insert(self.solution[key], 0, successors[bestnode_index][i][1])
                    i = i+1
                return [True,-1]
            
    
    def state_heuristic(self,state,goal):
        h_cost = 0
        i = 0
        for substate in state:
            if debug.debug and debug.heuristic_debug:
                print ' Fetching heuristic from node ' + np.str(substate[0]) + ' to ' + np.str(substate[1]) + ' at percent ' + np.str(substate[2]) + ' to reach goal ' + np.str(goal[i][1])

            if not (self.heuristic[substate[1]].has_key(goal[i][1]) and self.heuristic[substate[1]].has_key(goal[i][1])):
                if debug.debug and debug.warning:
                    print ' WARNING: Failed to fetch heuristic from node ' + np.str(substate[0]) + ' to ' + np.str(substate[1]) + ' at percent ' + np.str(substate[2]) + ' to reach goal ' + np.str(goal[i][1])
                    print ' Returning infinite h-cost for decision!'
                return self.infcost
                
            h_cost_current = self.heuristic[substate[1]][goal[i][1]] + ((self.heuristic[substate[0]][goal[i][1]] - self.heuristic[substate[1]][goal[i][1]])*(1-substate[2]))
            h_cost = h_cost + h_cost_current
            #if (substate[1]==37) or (substate[1]==18) or (substate[1]==12):
            #    print ' for substate: ' + np.str(substate) + ' h-cost is: ' + np.str(h_cost_current)
            #    print ' start node h-cost: ' + np.str(self.heuristic[substate[0]][goal[i][1]]) + ' final node h-cost: ' + np.str(self.heuristic[substate[1]][goal[i][1]])
            i = i+1
        
        return h_cost
    
    
    def getBestNode(self,successors,f_cost):
        #returns node with best f-value
        #print ' entered getBestNode'
        bestcost = self.infcost
        bestnode = -1
        
        #finds best f-value
        for s in successors.iterkeys():
            temp = f_cost[s]
            #print ' best successor cost so far: ' + np.str(bestcost)
            #print ' current successor cost: ' + np.str(temp)
            
            if temp < bestcost:
                bestcost = temp
                bestnode = s
        
        #print ' best node found index: ' + np.str(bestnode)
        return bestnode
    
    def getAltNode(self,successors,f_cost):
        #gets the second-best f-value node
        #print ' entered getAltNode'
        
        #gets the best node
        bestnode = self.getBestNode(successors, f_cost)
        
        #removes the best node from the successors
        #print 'Successors before removal of best node: ' + np.str(successors)
        alt_successors = dict()
        
        for keys in successors.iterkeys():
            if keys != bestnode:
                alt_successors[keys] = successors[keys]
                
        #print 'Successors after removal of best node: ' + np.str(alt_successors)
        #gets the best node, without the original best node in successors
        altnode = self.getBestNode(alt_successors, f_cost)
        #print ' altnode is: ' + np.str(altnode)
        #print successors
        return altnode
    
    
                      
    def expand_S(self,node):
        #returns array with all possible nodes from current node
        tempnodes = self.nodeGraph[node]
        #print tempnodes
        return tempnodes
    
    def expand_M(self,node):
        #returns array with all possible nodes from current node
        
        substate2expand_array = self.isThereDecision(node)
        
        #initial and finishing scenarios
        if (substate2expand_array == -1).all():
            #print 'initial expand'
            time, substate_index = self.selIntegration(node)
            #print 'state before integration:'
            #print node
            #print 'integrating until substate ' + np.str(substate_index) + ' is finished'
            intnode = self.sim.integrateState(substate_index,time,node)
            
            g_cost_inc = 0.0
            for substate in node:
                if substate[0]!=substate[1]:  #if goal reached, aircraft has no movement and no cost
                    g_cost_inc = g_cost_inc + time  #time-based cost is simply the the integrated time!
            
            successor_dict = dict()
            g_cost_inc_dict = dict()
            
            successor_dict[0] = intnode
            g_cost_inc_dict[0] = g_cost_inc
            
            #print 'init g-cost inc: ' + np.str(g_cost_inc)
            
            return successor_dict,g_cost_inc_dict
        
        #SUCCESSOR HASH TABLE INIT
        successors = np.array([[[0,0,0.0,0.0,0.0,1]]])
        for index in substate2expand_array: #just so the first successor is of compatible dimension with number of substates (aircrafts)
            successors = np.concatenate((successors,np.array([[[0,0,0.0,0.0,0.0,1]]])),axis=1)
        
        successors = np.delete(successors, 0, axis=1)
        
        #print 'init successors = ' + np.str(successors)
        
        for substate2expand_index in substate2expand_array:
            if substate2expand_index!=-1:
                #gets successors to that node if there is a decision to be made
                # else, integrates to the next decision - should only happen for initial state
                #print 'enter decision IF'
                #print 'expanding substate number: ' + np.str(substate2expand_index)
                
                substate2expand = node[substate2expand_index]
                
                #print substate2expand
                
                #does single expansion of the final node of the substate to be expanded!
                #then it simply gets the fastest decision, and integrates that successor until then, that obtains the successors
                
                substate_successors = self.expand_S(substate2expand[1])
                
#                print 'possible destinations are: ' + np.str(substate_successors)
                
                tempsuccessor = np.array(node)
                
#                print 'original tempsuccessor: ' + np.str(tempsuccessor)
                #deletes the substate that originates the expansion
                tempsuccessor = np.delete(tempsuccessor, substate2expand_index, axis=0)
#                print 'tempsuccessor after substate2expand deleted: ' + np.str(tempsuccessor)
                
                for subsuccessor in substate_successors.iterkeys():
                    # if the subsuccessor final node is the same as the starting node previous to the decision
                    # the aircraft is going back the way it came! this is not a valid solution!
                    if subsuccessor==substate2expand[0]:
                        continue
                    
#                    print 'successor ' + np.str(subsuccessor)+ ' of substate ' +   np.str(substate2expand) + ' is being inserted at index ' + np.str(substate2expand_index)
                    #then it updates the previous/next nodes for the substate for each successor, and puts percent at 0.0
                    # if the dest node is a gate/depart type AND is the substate goal, the command subsuccessor is stop!
                    previous_command = substate2expand[5]
                    command = previous_command
                    dest_node_type = self.nodeArray[subsuccessor].type
                    if (dest_node_type == 'gate' or dest_node_type == 'depart') and (self.goalstate[substate2expand_index][1]==subsuccessor):
                        command = -2  #issues stop command!
                    
                    tempsuccessor = np.insert(tempsuccessor, np.int(substate2expand_index), [substate2expand[1],subsuccessor,0.0,substate2expand[3],substate2expand[4],command], axis=0)
                    #SPEED AND HEADING ARE CONTINUOUS!! THUS RECEIVE THE SAME VALUES JUST BEFORE REACHING DECISION
                    
#                    print 'successors: ' + np.str(successors)
#                    print 'tempsuccessor: ' + np.str(np.array([tempsuccessor]))
                    successors = np.concatenate((successors,np.array([tempsuccessor])),axis=0)
                    #removes the substate, so it can be reinserted in next iteration
                    tempsuccessor = np.delete(tempsuccessor, substate2expand_index, axis=0)
                    
                    
                #successors should now be correctly updated, but not integrated until decision-time
                
                #print 'successors before trimming 1st pos:'
                #print successors
        
        #removes the first element used for concatenation
        successors = np.delete(successors, 0, axis=0)
        
        #print 'successors after trimming 1st pos:'
        #print successors
        
        i=0
        
        successor_dict = dict()
        g_cost_inc_dict = dict()
        
        
        for successor in successors:
            g_cost_inc = 0.0
            #print 'SUCCESSOR TO BE INTEGRATED: ' + np.str(successor)
            time, substate_index = self.selIntegration(successor)
            #print 'integrating until substate ' + np.str(substate_index) + ' is finished'
            intsuccessor = self.sim.integrateState(substate_index,time,successor)
            
            for substate in successor:
                if substate[0]!=substate[1]: #if goal reached aircraft has no movement and no cost 
                    g_cost_inc = g_cost_inc + time  #time-based cost is simply the the integrated time!
            
            #print 'g_cost_inc was:' + np.str(g_cost_inc)
            
            #successor = np.delete(successor, i, axis=0)
            #successor = np.insert(successor, i, intsuccessor, axis=0)
            
            successor_dict[i] = intsuccessor
            g_cost_inc_dict[i] = g_cost_inc
            
            i = i+1
        
        return successor_dict, g_cost_inc_dict
        
        
    
    def isThereDecision(self,node):
        i=0
        #print 'checking if there is decision'
        expand_array = np.array([])
        for substates in node:
            if not (substates[5]==-1 or substates[5]==0): #when in hold or wait they dont decide first
                if substates[2] == 1.0:
                    #print 'checking if final node ' + np.str(substates[1]) + ' is the goal node ' + np.str(self.goalstate[i][1])
                    if substates[1]==self.goalstate[i][1]: #goal reached formatting
                        expand_array = np.append(expand_array, -1)
                        substates = self.formatGoal(substates)
                    else:
                        expand_array = np.append(expand_array, i)
                else:
                    expand_array = np.append(expand_array, -1)
                i = i+1
            else:  #this should be directed at states in hold/wait and depend on node observation completion
                if substates[2] == 1.0:
                    #print 'checking if final node ' + np.str(substates[1]) + ' is the goal node ' + np.str(self.goalstate[i][1])
                    if substates[1]==self.goalstate[i][1]: #goal reached formatting
                        expand_array = np.append(expand_array, -1)
                        substates = self.formatGoal(substates)
                    else:
                        expand_array = np.append(expand_array, i)
                else:
                    expand_array = np.append(expand_array, -1)
                i = i+1
                
        
        #print 'decision check result:' + np.str(expand_array)
        
        return expand_array
    
    def formatGoal(self,substate):
        substate[0] = substate[1]
        substate[2] = 0.0
        substate[3] = 0.0  #goal speed
        substate[4] = 0.0  #goal heading
        substate[5] = -1
        
        return substate
    
    def selIntegration(self,node):
        i=0
        shortest_time = 1000000
        sel_aircraft = -1
        for aircraft_state in node:
            if aircraft_state[0]==aircraft_state[1]:  #if has reached goal, return a huge time, 
                if aircraft_state[5]==-1 or aircraft_state[5]==0:  #also for hold and wait states,
                    temp = self.infcost               #so substate doesnt get selected for integration
            else:
                temp = self.sim.integrateTime(aircraft_state)
            if temp < shortest_time:
                shortest_time = temp
                sel_aircraft = i
            i = i+1
        
        return shortest_time, sel_aircraft
    
    