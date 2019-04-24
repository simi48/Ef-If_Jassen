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
    Round = 0
    
    style = np.random.randint(6) #subject to change
    Cards.append(style) #add trump
    
    
    Round += 1
    Round %= 4
    
    

        