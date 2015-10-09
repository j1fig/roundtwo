'''
Created on Jun 15, 2011

@author: joao
'''

from ATC import *

system = ATC('nodes2.txt','connect2.csv','aircrafts2.txt')
#system.aircraft()
#system.nodes()
#system.setCourse('TAP1234', [1,7,13,19,40,41,42,43,44,45,46,47,48,49,50,51,52,53,58,54,55,56,57,61])
system.setBestMultiRoute()

#system.run()
#system.play()

# custo someatrio dos tempos de espera
# heuristica - procura sem conflitos - relaxed problem
#