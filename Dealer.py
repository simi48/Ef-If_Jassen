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



def SingleGame(ModelArray, trump = None):
    '''
    SingleGame allows for 4 AIs to play one full game of cards (4 rounds, so everyone can go first once)
    
    Parameters:
        ModelArray (Array[tf.keras.model.sequential]):
            An array of len(Array)=4 of tf models.
        
        limited (int):
            A boolean signifying what trump the game will use. If trump = None (default) a random playstyle will be selected.\n
            - 0=ace;
            - 1=6;
            - 2=rose;
            - 3=acorn;
            - 4=bell;
            - 5=shield;
    
    Returns:
        Array[int]:
            An Array of the points each AI made during this game.
            
    '''
    called = None
    points = [0,0,0,0]
    for stage in range(4): #everyone gets to begin once.
        GlobalCards = js.Shuffle()
        if(trump!=None):
            GlobalCards.append(trump)
        else:
            GlobalCards.append(np.random.randint(6))
        startingplayer = stage
        for turn in range(9): #everyone has 9 cards
            called = None
            playedcards = []*37
            for player in range(4): #4 players playing one card at a time.
                activeplayer = (player + startingplayer) %4 #offset to different players
#                print(player," ",activeplayer)
                local = js.LocalPov(GlobalCards,activeplayer)
                suggested_move = rnn.Evaluate(ModelArray[activeplayer].predict(rnn.PrepareInput(local)))
                tmp = suggested_move
                if(not js.LegalMove(local,suggested_move,called,player = 1)): #player 1 meaning that cards with value 1 are abailable for play (as is the case in local pov)
                    for i in range(36):
                        if(js.LegalMove(local,local[i],called, player = 1)):
                            suggested_move = i
                    if(tmp==suggested_move):
                        suggested_move = local.index(1)
                
                #malus
                if(tmp!=suggested_move):
                    points[activeplayer]-=10000
                    print("nay")
                else:
                    print("yay")
                
                #set the called colour
                if(player==0):
                    called = js.Colour([suggested_move])
                    called = called[0]
                GlobalCards[suggested_move] = 8+activeplayer
                playedcards[suggested_move] = activeplayer
            startingplayer = js.RoundWinner(playedcards,GlobalCards[36],startingplayer)
        
        #screwing up globalcards, but wont need them after anyway:
        for i in range(36):
            GlobalCards[i] -= 8
        print(js.CountPoints(GlobalCards))
        test = points + js.CountPoints(GlobalCards)
        if(test == points):
            print(GlobalCards)
        else:
            points = test
        
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
    modellist = []
    for i in range(4):
        modellist.append(rnn.GetModel())
        rnn.LoadWeights(modellist[i],"Basic")
        rnn.Mutate(modellist[i],0.3*i)
    print(SingleGame(modellist))
    
    Cards = js.Shuffle()
    print(Cards)
    Round = 0
    
    style = np.random.randint(6) #subject to change
    Cards.append(style) #add trump
    
    
    Round += 1
    Round %= 4
    
    

        