'''
Created on Jun 15, 2011

@author: joao
'''

class Node:
    """ Contains node info and connections """
    
    def __init__(self,type,number,xpos,ypos):
        self.type = type
        self.number = number
        self.x = xpos
        self.y = ypos
        