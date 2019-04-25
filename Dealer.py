# -*- coding: utf-8 -*-
"""
Project:       Deep Jass

File:           Dealer.py

Purpose:        Recurring Neural Network to learn how to play cards.

Created on:     24.04.2019 11:02:27
Author:         Simon Thür; Marc Matter

Copyright © 2019 Marc Matter, Michael Siebenmann, Ramon Heeb, Simon Thür. All rights reserved.
"""


import numpy as np
import multiprocessing #*NOTE Multiprocessing ?usually? does not work in iPython (Spyder). To use MP, run file through Anaconda: navigate to folder and type: `python Dealer.py`
from tqdm import tqdm  #using anaconda/pip: pip install tqdm
import JassRNN as rnn
import Jassen as js



def SingleGame(ModelArray, limited = False):
    called = None
    points = [0,0,0,0]
    for stage in range(4): #everyone gets to begin once.
        GlobalCards = js.Shuffle()
        if(limited):
            GlobalCards.append(0)
        else:
            GlobalCards.append(np.random.randint(6))
        for turn in range(9): #everyone has 9 cards
            called = None
            for player in range(4): #4 players playing one card at a time.
                local = js.LocalPov(GlobalCards,player)
                suggested_move = rnn.Evaluate(ModelArray[player].predict(rnn.PrepareInput(local)))
                if(not js.LegalMove(local,suggested_move,called,player = 1)): #player 1 meaning that cards with value 1 are abailable for play (as is the case in local pov)
                    for i in range(36):
                        if(js.LegalMove(local,local[i],called, player = 1)):
                            suggested_move = i
                '''left off here:
                    next:: play card'''
                
        
        
    return points



# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    Players = []
# =============================================================================
#     for i in range(4):
#         name = 'p' + str(i)
#         Players.append(rnn.GetModel())
#         rnn.LoadWeights(Players[i], name)
# =============================================================================
        
    Cards = js.Shuffle()
    print(Cards)
    Round = 0
    
    style = np.random.randint(6) #subject to change
    Cards.append(style) #add trump
    
    
    Round += 1
    Round %= 4
    
    

        