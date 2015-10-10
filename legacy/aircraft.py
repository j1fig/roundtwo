'''
Created on Jun 15, 2011

@author: joao
'''

import numpy as np
from Estimator import *
from DynamicSimulator import *
from AuxCalculator import *
import debug


class Aircraft:
    """
    Contains aircraft type, flight number, position
    """

    def __init__(self,
                 nodeArray,
                 name,
                 number,
                 nodeI,
                 nodeF,
                 percent,
                 speed,
                 heading,
                 command,
                 destination):
        self.nodeArray = nodeArray
        self.name = name
        self.flightnumber = number
        self.speed = speed
        self.heading = heading
        self.command = command
        self.destination = destination
        self.course = np.array([])
        self.inTransit = False
        self.x = self.nodeArray[nodeI].x + \
            ((self.nodeArray[nodeF].x - self.nodeArray[nodeI].x)*percent)
        self.y = self.nodeArray[nodeI].y + \
            ((self.nodeArray[nodeF].y - self.nodeArray[nodeI].y)*percent)
        self.taxiSpeed = 7.71666667  # 15 knots
        self.acceleration = 0.5  # 1.8 km/h speed increase per second

        self.node_I_index = 0
        self.node_I = nodeI
        self.node_F = nodeF
        self.percent = percent

        self.sim = DynamicSimulator(self.nodeArray, self.taxiSpeed)
        self.aux = AuxCalculator(self.nodeArray)

    def update(self, step):
        # dx = self.speed*np.cos(self.heading)*step
        # dy = self.speed*np.sin(self.heading)*step
        #will present integration results in dx and dy, so it doesnt mess with previous code!

        c_substate = np.array([self.node_I,self.node_F,self.percent,self.speed,self.heading,self.command]) #current substate
        if debug.debug and debug.run_debug:
            print ' current substate is: ' + np.str(c_substate)


        temp_substate = np.array(c_substate)
        temp_substate = self.sim.integrate(step, temp_substate)
        if debug.debug and debug.run_debug:
            print ' temp substate is: ' + np.str(temp_substate)

#        print 'Current heading:' + np.str(self.heading*180/np.pi)
#        print 'Current speed:' + np.str(self.speed)
#        print 'Current X:' + np.str(self.x) + ' Y:' + np.str(self.y)
#        print 'Destination: ' + np.str(self.nodeArray[self.node_F].number)

        if debug.debug and debug.run_debug:
            print ' is there node switch? ' + np.str(self.isThereNodeSwitch(temp_substate))

        if self.isThereNodeSwitch(temp_substate):  #node switch condition!
            #find necessary time step to exactly reach final node
            part_time = self.sim.integrateTime(c_substate)

            if debug.debug and debug.run_debug:
                print ' part time to node switch is: ' + np.str(round(part_time,5))
                print ' substate sent to get part_time:' + np.str(c_substate)

            #update current nodes and course
            self.updateCourse()

            temp_substate = np.array([self.node_I,self.node_F,self.percent,self.speed,self.heading])
            #send the remaining time step to integrator

            if self.inTransit:
                remain_time = step - part_time
            else:
                remain_time = part_time    #course finishing step!


            final_substate = self.sim.integrate(remain_time, temp_substate)

            if self.inTransit:
                self.percent = final_substate[2]
                self.speed = final_substate[3]
                self.heading = final_substate[4]
            else:
                self.percent = 0.0
                self.speed = 0.0
                self.heading = 0.0

            self.x,self.y = self.aux.substate2orto(final_substate)

        else:    #normal path between two nodes
            self.percent = temp_substate[2]
            self.speed = temp_substate[3]
            self.heading = temp_substate[4]

            self.x,self.y = self.aux.substate2orto(temp_substate)
            #print "normal course"



    def updateCourse(self):
        # destination node is the next in course array
        node_F_index = self.node_I_index + 1

        if debug.debug and debug.run_debug:
            print ' Current final node index: ' + np.str(node_F_index)
            print ' Course size is: ' + np.str(np.size(self.course)-1)

        if (node_F_index>=(np.size(self.course)-1)):
            if debug.debug and debug.run_debug:
                print ' Finished course!'
            self.inTransit = False
            return
            # node_F_index = np.size(self.course)

        self.node_I = self.node_F
        self.node_I_index = self.node_I_index + 1
        node_F_index = self.node_I_index + 1
        self.percent = 0.0

        # print 'next destination is node ' + np.str(self.course[node_F_index])
        self.node_F = self.nodeArray[np.int(self.course[node_F_index])].number

    def isThereNodeSwitch(self,substate):
        # Node switch condition calculations
        if substate[2]> 1.0:
            return True
        else:
            return False
