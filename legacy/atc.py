'''
Created on May 4, 2011

@author: joao
'''

import numpy as np

from aircraft import Aircraft
from node import node
from estimator import Estimator
from logplayer import LogPlayer
from searcher import Searcher
import settings


class ATC(object):
    """
    Automatic Air Traffic Control Class
    """

    def __init__(self, nodefile, connectfile, aircraftfile):
        """
        reads node and aircrafts file
        """

        if settings.debug:
            print " Initializing Automatic ATC System...\n"

        self.time = 0
        self.logTimeStep = 0.1

        self.logArray = np.array([[0.0, 'None', 0.0, 0.0]])

        # NODE DATA PARSE
        # gets node info from file
        tempNodeArray = np.loadtxt(
            nodefile,
            dtype={'names': ['type', 'Xpos', 'Ypos'],
                   'formats': ['S10', np.float32, np.float32]}
        )

        # generates hash table from read node data
        node_number = 0
        dictArray = dict()

        for x in tempNodeArray:
            dictArray[node_number] = Node(x[0], node_number, x[1], x[2])
            node_number = node_number + 1

        self.nodeArray = dictArray

        # NODE CONNECT DATA PARSE
        # gets node connection info from csv file and puts in in a hash table
        gen_args = dict(delimiter=",",
                        dtype=int,
                        missing_values={0: ""},
                        filling_values={0: -1})
        self.connectArray = np.genfromtxt(connectfile, **gen_args)

        # Implementacao de nos virtuais para hold
        # for node in self.nodeArray.itervalues():
        #     if node.type=='hold':
        #         self.connectArray = np.concatenate(
        #             (self.connectArray, np.array([[node.number, node.number]])),
        #             axis=0
        #         )

        # AIRCRAFT DATA PARSE
        # gets aircraft info from file
        tempArray = np.loadtxt(
            aircraftfile,
            dtype={
                'names': ['type', 'number', 'last_node', 'next_node', 'percent',
                          'speed', 'heading', 'command', 'destination'],
                'formats': ['S10', 'S10', np.int8, np.int8, np.float32,
                            np.float32, np.float32, np.int8, np.int8]
            }
        )

        # stores it in an hash table,
        # each element being an object of Aircraft type
        dictArray = dict()

        for x in tempArray:
            dictArray[x[1]] = Aircraft(
                self.nodeArray,
                x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8]
            )

        self.aircraftArray = dictArray

        # print ' Node Array is: \n' + np.array2string(self.nodeArray)

        if settings.debug:
            print "\n Finished initializing Automatic ATC System."

    def aircraft(self):
        """
        returns current aircraft
        """
        print '\n Current aircraft: \n'
        for x in self.aircraftArray.itervalues():
            print ' Type: ' + np.str(x.name)
            print ' Flight Number: ' + np.str(x.flightnumber)
            print ' Node: ' + np.str(x.node_I)
            print ' Linear speed: ' + np.str(x.speed) + '\n'

        return self.aircraftArray

    def nodes(self):
        """
        returns current nodes
        """
        print '\n Current nodes: \n'
        for x in self.nodeArray.itervalues():
            print ' Node number: ' + np.str(x.number) + \
                  '   type: ' + np.str(x.type)
            print ' X:' + np.str(x.x) + ' Y:' + np.str(x.y)

        return self.nodeArray

    def setCourse(self, flightnumber, course):
        """
        executes move sequence for the selected flight
        """
        course = np.array(course)

        self.aircraftArray[flightnumber].course = course
        self.aircraftArray[flightnumber].node_F = course[1]
        self.aircraftArray[flightnumber].inTransit = True

        return True

    def bestMultiRoute(self):
        if settings.debug:
            print " Calculating optimal aircraft routing..."

        # INIT SEARCHER OBJECT
        searcher = Searcher(self.nodeArray,
                            self.connectArray,
                            self.aircraftArray)

        routes = searcher.optimizeMultiRoutes()
        # routes is a Dict with the route for each flightnumber

        if settings.debug:
            print " Finished calculating optimal aircraft routing."

        return routes

    def setBestMultiRoute(self):
        """
        returns a hash table with the route for each aircraft,
        based on best global solution
        """
        routes = self.bestMultiRoute()

        for aircraft in self.aircraftArray.itervalues():
            self.setCourse(aircraft.flightnumber, list(routes[aircraft]))

    def run(self):
        # assumes movement
        traffic = True

        while traffic:
            # guardar no log array dados do timestep actual
            for aircraft in self.aircraftArray.itervalues():
                logLine = np.array(
                    [self.time, aircraft.flightnumber, aircraft.x, aircraft.y]
                )
                # print np.str(np.array([logLine]))
                self.logArray = np.concatenate(
                    (self.logArray, np.array([logLine])),
                    axis=0
                )
            # incrementar time de logTimeStep
            self.time = self.time + self.logTimeStep

            # update all aircraft except those with inTransit=False
            # assumes no movement unless told otherwise
            traffic = False
            for aircraft in self.aircraftArray.itervalues():
                if aircraft.inTransit:
                    aircraft.update(self.logTimeStep)
                    traffic = True

        # save log array to log file
        # print self.logArray

        # self.logArray = np.vsplit(self.logArray, 4)

        # print self.logArray

        np.savetxt('log.txt', self.logArray, fmt='%s %s %s %s')

        return True

    def display(self):
        player = LogPlayer()

        player.drawNodes()
        player.drawPath()
        player.update()

    def play(self):
        player = LogPlayer()

        player.play()
