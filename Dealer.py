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



def SingleGame(ModelArray, trump = None, queue = None):
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
#        print("stage ",stage)
        GlobalCards = js.Shuffle()
        if(trump!=None):
            GlobalCards.append(trump)
        else:
            GlobalCards.append(np.random.randint(6))
        startingplayer = stage
        controllarray = []
        for turn in range(9): #everyone has 9 cards
#            print("turn ",turn)
            called = None
#            playedcards = []*36
            playedcards = [None]*4
            for player in range(4): #4 players playing one card at a time.
#                print("player ",player)
                activeplayer = (player + startingplayer) %4 #offset to different players
#                print(player," ",activeplayer)
                local = js.LocalPov(GlobalCards,activeplayer)
                suggested_move = rnn.Evaluate(ModelArray[activeplayer].predict(rnn.PrepareInput(local)))
                tmp = suggested_move
#                DebugVar = []
#                for i in range(36):
#                    DebugVar.append(js.LegalMove(local,i,called,trump = GlobalCards[36],player = 1))
                if(not js.LegalMove(local,suggested_move,called,trump = GlobalCards[36],player = 1)): #player 1 meaning that cards with value 1 are available for play (as is the case in local pov)
                    for i in range(36):
                        if(js.LegalMove(local,i,called,trump = GlobalCards[36],player = 1)):
                            suggested_move = i
                    #just to make sure it doesnt play the "playstyle"
                    if(tmp==suggested_move):
                        intermediate = local.index(1)
                        if(js.LegalMove(local,suggested_move,None,trump=GlobalCards[36],player=1)):
                            pass #yes I know it aint pretty, but im tired, its 01:19 27:04:2019
#                            print("Won't win but not incorrect (more of a test fuck off)\nalso, if this happens randomly, let me know it worked (ST) thx.\n\n")
                        elif(intermediate != 36):
                            suggested_move = intermediate
                            tmp = suggested_move
                
                #malus
                if(tmp!=suggested_move):
                    points[activeplayer]-=10000
#                    print("nay")
#                else:
#                    print("Praise the sun")
                
                #set the called colour
                if(player==0):
                    called = js.Colour([suggested_move])
                    called = called[0]
                GlobalCards[suggested_move] = 4+activeplayer
                controllarray.append(suggested_move)
                playedcards[activeplayer] = suggested_move
#                print(playedcards)
#            print(playedcards)
#            print("\ncontrollarray\n",controllarray,"\n")
            for i in range(4):
                GlobalCards[playedcards[i]] = i+8
            startingplayer = js.RoundWinner(playedcards,GlobalCards[36],startingplayer)
        
        #screwing up globalcards, but wont need them after anyway:
        for i in range(36):
            GlobalCards[i] -= 8
        score = js.CountPoints(GlobalCards)
#        print(len(score))
#        print(score)
        for i in range(4):
            points[i] += score[i]
        
    if(queue==None):
        return points
    else:
        queue.put(points)



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
#    model = rnn.GetModel()
#    for i in range(150):
#        cards = js.Shuffle()
#        cards.append(np.random.randint(6))
#        print(rnn.Evaluate(model.predict(rnn.PrepareInput(js.LocalPov(cards)))))
    modellist = []          
    m = rnn.GetModel()
    print("__innit__ & mutating")
    for i in tqdm(range(4)):
#        print("iteration: ",i)
        modellist.append(m)
#        print("loaded")
#        rnn.LoadWeights(modellist[i],"TESTSAVE")
#        print("loaded weights")
        rnn.Mutate(modellist[i],0.3*i+0.1)
#        print("mutated")
    print("starting...")
#    print(SingleGame(modellist))
    points = [0]*4
    for i in tqdm(range(100)):
        score = SingleGame(modellist)
        for i in range(4):
            points[i] += score[i]
    print("Points:\n",points)
#    
#    for i in range(15):
#        cards = js.Shuffle()
#        cards.append(np.random.randint(6))
#        print(rnn.Evaluate(modellist[0].predict(rnn.PrepareInput(cards))))
#    
    

        