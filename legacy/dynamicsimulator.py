'''
Created on Oct 29, 2011

@author: joao
'''

import numpy as np
from AuxCalculator import *
import debug

class DynamicSimulator:
    '''
    This module simulates aircraft dynamics
    '''


    def __init__(self,nodeArray,nominal_speed):
        '''
        Constructor
        '''
        self.nodeArray = nodeArray
        
        self.nominal_speed = nominal_speed
        self.nominal_acceleration = 0.5
        self.deacceleration = 0.0
        
        
        self.hold_speed = 1.0
        
        self.integration_step = 0.1
        self.inftime = 1000000
        
        self.aux = AuxCalculator(self.nodeArray)
    
    def integrate(self,stime,substate):
        # computes and returns the integrated substate over stime
        
        if debug.debug and debug.dynamics_debug:
            print '\n Entering integrate!'
            print ' integrating substate: '
            print np.str(substate)

        init_command = substate[5]
        
        step_dist = 0.0  #total distance (result of time integration)
        ttime = 0.0      #integration variable
        
        init_speed = substate[3]
        tot_dist = self.aux.nodeDistance(substate[0],substate[1])
        remain_dist = tot_dist*(1.0-substate[2])
        
        timeToTargetSpeed = self.getTimeToTargetSpeed(init_speed, remain_dist, init_command)
        
        if init_command==-2: # if command to stop
                self.updateDeacceleration(timeToTargetSpeed,init_speed)
        
        if init_speed==self.nominal_speed and init_command==1: # if also commanded to move
            #print 'integrate at full speed'
            step_dist = self.nominal_speed*stime
            inc_percent = (step_dist/tot_dist)
            
            substate[2] = substate[2] + inc_percent
            substate[3] = self.speedControl(init_speed, stime, init_command)
            substate[4] = self.headingControl(substate, stime)
            
            return substate
        elif timeToTargetSpeed>=stime:
            #print 'integrate accelerating'
            acceleration = self.nominal_acceleration
            
            if init_command==-2:  # if command is stop
                acceleration = self.deacceleration
            
            step_dist = self.getAcceleratedDist(init_speed, stime, acceleration)
            inc_percent = (step_dist/tot_dist)
            
            substate[2] = substate[2] + inc_percent
            if substate[2]<0:
                if debug.debug and debug.warning:
                    print ' WARNING: INTEGRATION FAILURE, PERCENT = ' + np.str(substate[2]) + ' - TRIMMED AT 0.0 FOR SAFETY'
                substate[2] = 0.0
            if substate[2]>1.0:
                if debug.debug and debug.warning:
                    print ' WARNING: INTEGRATION FAILURE, PERCENT = ' + np.str(substate[2]) + ' - TRIMMED AT 1.0 FOR SAFETY'
                substate[2] = 1.0
                
            substate[3] = self.speedControl(init_speed, stime,init_command)
            substate[4] = self.headingControl(substate, stime)
            
            return substate
        elif timeToTargetSpeed<stime:
            #print 'integrate reaching target speed'
            
            if init_command==1: #command to move - moving and reaching full speed
                step_distToMaxSpeed = self.getAcceleratedDist(init_speed, timeToTargetSpeed,self.nominal_acceleration)
                step_distRemaining = self.nominal_speed*(stime-timeToTargetSpeed)
                step_dist = step_distToMaxSpeed + step_distRemaining
                inc_percent = (step_dist/tot_dist)
                substate[2] = substate[2] + inc_percent
            
            if init_command==-2: # command to stop - stopping and reaching hold_speed (0) also reaching final_node
                substate[2] = 1.0
                substate[5] = -1  #sets hold command state until next passing aircraft
            
            substate[3] = self.speedControl(init_speed, stime,init_command)
            substate[4] = self.headingControl(substate, stime)
            
            return substate
        
        print ' integrate failed!'
    
    
    
    def integrateState(self,sstate_index,stime,state):
        
        for substate in state:
            if substate[0]!=substate[1]: #if substate has reached its subgoal, no integration is done
                if not (substate[5]==-1 or substate[5]==0): # doesnt integrate for hold and wait states
                    substate = self.integrate(stime,substate)
        #forces percent for select integration state at 1.0, so it is next in queue for decision
        if not state[sstate_index][0]==state[sstate_index][1]:
            #if state[sstate_index][2] < 1.0 or state[sstate_index][2] > 1.0:
                #print 'integration curiosity: ' + np.str(state[sstate_index][2])
            state[sstate_index][2] = 1.0
        
        return state
        
        
    def integrateTime(self,substate):
        # This is a test that returns the realistic (dynamic modeled) time to decision
        
        if debug.debug and debug.dynamics_debug:
            print '\n Entering integrate time!'
            print ' integrating state: '
            print np.str(substate)
            
        distance = self.aux.nodeDistance(substate[0], substate[1])
        
        distance = distance*(1.0-substate[2])  #assumes linear time-distance relation
        
        if debug.debug and debug.dynamics_debug:
            print ' remaining distance: ' + np.str(round(distance,5))
        
        init_speed = substate[3]   #this is a test, so it should save the modified values 
        init_heading = substate[4] #so that they can be later reinstated
        init_command = substate[5]
        
        timeToDecision = 0.0
        
        timeToTargetSpeed = self.getTimeToTargetSpeed(init_speed, distance, init_command)
        if debug.debug and debug.dynamics_debug:
            print ' time to target speed: ' + np.str(round(timeToTargetSpeed,5))
        distToTargetSpeed = self.getDistToTargetSpeed(init_speed,distance,timeToTargetSpeed,init_command)
        if debug.debug and debug.dynamics_debug:
            print ' dist to target speed: ' + np.str(round(distToTargetSpeed,5))
        
        if init_command==-2: # if command to stop
            if debug.debug and debug.dynamics_debug:
                print ' Command to stop... updating deacceleration.'
            self.updateDeacceleration(timeToTargetSpeed,init_speed)
        
        if init_speed==self.nominal_speed and init_command==1:  #if it is already at max speed and command to move
            if debug.debug and debug.dynamics_debug:
                print ' moving at max speed... '
            #print 'integrateTime at full speed'
            timeToDecision = distance/self.nominal_speed
            return timeToDecision
        elif distToTargetSpeed==distance:
            timeToDecision = timeToTargetSpeed
            return timeToDecision
        elif distToTargetSpeed>distance:    # if it is still accelerating
            if debug.debug and debug.dynamics_debug:
                print ' accelerating to target speed... '
            acceleration = self.nominal_acceleration
            if init_command==-2: # if command to stop
                acceleration = self.deacceleration
            
            timeToDecision = self.getTimeLeft(distance, init_speed, acceleration)
            return timeToDecision
        elif distToTargetSpeed<distance:   #  if it reaches target speed in current integration
            if debug.debug and debug.dynamics_debug:
                print ' reaching target speed... '
            if init_command==1: # if command to move
                remain_timeToDecision = (distance-distToTargetSpeed)/self.nominal_speed  #figures remaining time (at max speed)
                timeToDecision = timeToTargetSpeed + remain_timeToDecision   #sums both for total time spent
            elif init_command==-2: # if command to stop
                timeToDecision = timeToTargetSpeed # time to reach speed is the same time to reach decision!
            
            return timeToDecision
        
        if debug.debug and debug.dynamics_debug:
                print ' integrate Time failed to return a controlled value!!!'
    
    
    def speedControl(self,current_speed,step,command):
        
        acceleration = self.nominal_acceleration
        
        if command==-2: # if command to stop
            acceleration = self.deacceleration
        
        next_speed = current_speed + acceleration*step
        
        
        # speed trimming
        if next_speed > self.nominal_speed:
            next_speed = self.nominal_speed
        elif next_speed < self.hold_speed:
            next_speed = self.hold_speed
        
        return next_speed
    
    def headingControl(self,substate,step):
        
        current_heading = substate[4]
        
        dX = self.nodeArray[substate[1]].x - self.nodeArray[substate[0]].x
        dY = self.nodeArray[substate[1]].y - self.nodeArray[substate[0]].y
        
        next_heading = np.arctan(dY/dX)
        
        if dX<0:   #heading no 2 ou 3 quadrantes
            next_heading = next_heading + np.pi
        
        return next_heading
    
    def getTimeLeft(self,dist,init_speed,acceleration):
        
        t1 = (-init_speed + np.sqrt(np.square(init_speed) + (4*acceleration*dist)))/(2*acceleration)
        t2 = (-init_speed - np.sqrt(np.square(init_speed) + (4*acceleration*dist)))/(2*acceleration)
        
        if t2<0 and t1>0:
            return t1
        
        if t1<0 and t2>0:
            return t2
        
        if t2>0 and t1>0:
            if t1 < t2:
                return t1
            else:
                return t2
        
        return False
    
    def getDistToTargetSpeed(self,init_speed,tot_dist,timeToTargetSpeed,command):
        if command == 1: # if command to move
            distToMaxSpeed = self.getAcceleratedDist(init_speed, timeToTargetSpeed,self.nominal_acceleration)
        elif command == -2: # if command to stop
            distToMaxSpeed = tot_dist
        
        return distToMaxSpeed
    
    
    def getTimeToTargetSpeed(self,init_speed,dist,command):
        time = 0.0
        
        if command == 1: # if command to move
            time = (self.nominal_speed-init_speed)/self.nominal_acceleration
        elif command == -2: # if command to stop
            time = 2*dist/(init_speed-self.hold_speed)
        
        return time
        
    def getAcceleratedDist(self,init_speed,time,acceleration):
        dist_covered = (acceleration*np.square(time)) + (init_speed*time)
        return dist_covered
    
    def updateDeacceleration(self,time_to_stop,init_speed):
        
        deacceleration = (self.hold_speed - init_speed)/time_to_stop
        
        self.deacceleration = deacceleration
    