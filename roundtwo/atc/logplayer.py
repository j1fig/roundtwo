'''
Created on Jun 12, 2011

@author: joao
'''

from Tkinter import *
import numpy as np
from Node import *
import tkMessageBox
import random as rn


class LogPlayer:
    def __init__(self):
        
        def initLog(flight,time_0,x_0,y_0):
            self.logArray[flight] = np.array([[time_0,x_0,y_0]])
        
        def addLog(flight,time,x,y):
            self.logArray[flight] =np.concatenate((self.logArray[flight], np.array([[time,x,y]])),axis=0)
        
        #NODE DATA PARSE
        #gets node info from file
        tempNodeArray = np.loadtxt('nodes2.txt',dtype={'names':['type','Xpos','Ypos'],
                                                       'formats':['S10',np.float32,np.float32]})
        
        i=0  #node number
        j=0  #node column number
        
        dictArray = dict()
        
        for x in tempNodeArray:
            dictArray[i]= Node(x[0], i, x[1], x[2])
            i = i+1
        
        self.nodeArray = dictArray
        
        #LOG PARSE
        tempLogArray = np.loadtxt('log.txt',dtype={'names':['time','flight','x','y'],
                                                       'formats':[np.float32,'S10',np.float32,np.float32]}, skiprows=1)
        
        #print tempLogArray
        
        self.logArray = dict()
        
        for x in tempLogArray:
            if x[0]==0.0:
                initLog(x[1], x[0], x[2], x[3])
        
        for x in tempLogArray:
            addLog(x[1], x[0], x[2], x[3])
            
        
        self.colorArray = dict()
        
        for aircraft in self.logArray.iterkeys():
            self.colorArray[aircraft] = '#' + "".join("%02x"%rn.randrange(256) for x in range(3))
        
        
        #for log in self.logArray.itervalues():
        #    print log
        
        
        #TKINTER INIT
        self.root = Tk()
        
        self.root.protocol("WM_DELETE_WINDOW", self.deleteCallback)
    
        self.width = 640
        self.height = 480
        
        self.canvas = Canvas(self.root, width= self.width, height=self.height, bg='black')
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        
        self.canvas.bind("<Button-1>", self.callbackmouse1)
        
        
        textpos_x = 600
        textpos_y = 460
        textpos = self.point(textpos_x, textpos_y)
        textpos = self.win2canvas(textpos)
        for aircraft in self.logArray.iterkeys():
            self.canvas.create_text(textpos[0],textpos[1],fill=self.colorArray[aircraft],text=aircraft)
            textpos[1] = textpos[1] + 15
        
        
        timepos_x = 40
        timepos_y = 460
        timepos = self.point(timepos_x, timepos_y)
        timepos = self.win2canvas(timepos)
        
        
        self.time = 0.0
        
        self.timelabel = self.canvas.create_text(timepos[0],timepos[1],fill='white',text=self.time)
        

    def deleteCallback(self):
        if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
            self.root.destroy()
            
    def callbackmouse1(self,event):
        print "click at", event.x, event.y
            
    def win2canvas(self,pos):
        pos[1] = self.height - pos[1]
        return pos
    
    def point(self,x,y):
        botvertex = []
        botvertex.append(x)
        botvertex.append(y)
        return botvertex
    
    def createNode(self,x,y):
        diameter = 2
        
        botvertex = self.point(x-diameter,y-diameter)
        topvertex = self.point(x+diameter,y+diameter)
        
        botvertex = self.win2canvas(botvertex)
        topvertex = self.win2canvas(topvertex)
        
        
        xy = botvertex[0], botvertex[1], topvertex[0], topvertex[1]
        self.canvas.create_arc(xy, start=0, extent=359, fill="white")
        
    def createAircraft(self,x,y,color,aircrafttag):
        size = 4
        
        vertex1 = self.point(x, y + size)
        vertex2 = self.point(x-size, y-size)
        vertex3 = self.point(x+size, y-size)
        
        vertex1 = self.win2canvas(vertex1)
        vertex2 = self.win2canvas(vertex2)
        vertex3 = self.win2canvas(vertex3)
        
        xy = vertex1[0],vertex1[1],vertex2[0],vertex2[1],vertex3[0],vertex3[1]
        
        self.canvas.create_polygon(xy,fill=color,tag=aircrafttag)
    
    def drawAircraft(self):
        for aircraft in self.logArray.iterkeys():
            self.createAircraft(self.logArray[aircraft][0][1],self.logArray[aircraft][0][2], self.colorArray[aircraft], aircraft)
        
        
    def drawNodes(self):
        for node in self.nodeArray.itervalues():
            self.createNode(node.x, node.y)
        
        
    def drawPath(self):
        points = np.array([])
        for aircraft in self.logArray.itervalues():
            for logLine in aircraft:
                currentPoint = self.point(logLine[1], logLine[2])
                currentPoint = self.win2canvas(currentPoint)
                points = np.append(points, currentPoint)
            
            #print points
            #print np.size(points)
            self.canvas.create_line(list(points),fill=self.colorArray[aircraft])
            points = np.array([])
    
    def play(self):
        
        self.drawNodes()
        self.drawAircraft()
        
        self.canvas.pack()
        time_size = 0
        
        
        for aircraft in self.logArray.itervalues():
            for logline in aircraft:
                time_size = time_size + 1
            break
        
        for i_time in range(2,time_size-1):
            time_step = 0
            for aircraft in self.logArray.iterkeys():
                points = np.array([])
                currentPoint = self.point(self.logArray[aircraft][i_time-1][1], self.logArray[aircraft][i_time-1][2])
                currentPoint = self.win2canvas(currentPoint)
                points = np.append(points, currentPoint)
                nextPoint = self.point(self.logArray[aircraft][i_time][1], self.logArray[aircraft][i_time][2])
                nextPoint = self.win2canvas(nextPoint)
                points = np.append(points, nextPoint)
                self.canvas.create_line(list(points),fill=self.colorArray[aircraft])
                self.canvas.move(aircraft,nextPoint[0]-currentPoint[0],nextPoint[1]-currentPoint[1])
                #print aircraft
                #print 'previous time ' + np.str(aircraft[i_time-1][0]) + ' next time ' + np.str(aircraft[i_time][0])
                time_step = self.logArray[aircraft][i_time][0] - self.logArray[aircraft][i_time-1][0]
                #print time_step
            
            self.time = self.time + time_step
            
            self.time = round(self.time,2)
            
            self.canvas.itemconfigure(self.timelabel, text=self.time)
            
            self.canvas.after(np.int(time_step*1000))
            self.canvas.update()
        
        self.root.mainloop()
        
        
    def update(self):
        self.canvas.pack()
        
        self.root.mainloop()
    
    
#    canvas.create_arc(xy, start=270, extent=60, fill="blue")
#    canvas.create_arc(xy, start=330, extent=30, fill="green")
#    canvas.create_rectangle(100,100,175,125)
#    canvas.pack()
#    
#    root.mainloop()