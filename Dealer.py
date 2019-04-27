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


def ChooseTrump(Cards, StartingPlayer):
    '''
    ChooseTrump allows the AI to choose the best possible playstyle (At least I hope so, it's not like I'm a pro at Jass)
    depending on the cards in their possesion.
    
    Parameters:
        Cards (array[int]):
            An array with the standard 36-cards layout.

        StartingPlayer(int):
            Defines which player gets to select the playstyle.
            
    Returns:
        Trump(int):
            The suggested playstyle for the next round.
    '''
    
    myCards = js.LocalPov(Cards, StartingPlayer)
    colInput = []
    colOutput = []
    points = []
    roses = 0
    acorn = 0
    bell = 0
    shield = 0
    ace = 0
    checkAce = 8
# =============================================================================
#     six = 0
#     checkSix = 0
#     buur = 0
#     checkBuur = 5
#     nell = 0
#     checkNell = 3
# =============================================================================
    ret = None
    
    for i in range(36): #prepare Input for Colour()
        if(myCards[i] == 1):
            colInput.append(i)
        if(i == checkAce):
            if(myCards[i] == 1): #count special cards
                ace += 1
                checkAce += 9
# ============================================================================= in case further precision for the playstyle selection is needed
#         elif(i == checkSix): 
#             if(myCards[i] == 1):
#                 six += 1
#                 checkSix += 9
#         elif(i == checkNell):
#             if(myCards[i] == 1):
#                 nell += 1
#                 checkNell += 9
#         elif(i == checkBuur):
#             if(myCards[i] == 1):
#                 buur += 1
#                 checkBuur += 9
# =============================================================================
                
    colours = js.Colour(colInput)
    
    checkBuur = 5
    checkNell = 3
    checkAce = 8
    for b in range(len(colours)): #Count how many cards of each colour the player has
        if(colours[b] == 0):
            roses += 1
        elif(colours[b] == 1):
            acorn += 1
        elif(colours[b] == 2):
            bell += 1
        elif(colours[b] == 3):
            shield += 1
    colOutput.append(roses)
    colOutput.append(acorn)
    colOutput.append(bell)
    colOutput.append(shield)
    
    for i in range(4): #check for special card combinations
        if((myCards[checkBuur] == 1) and (myCards[checkNell] == 1) and (myCards[checkAce] == 1)):
            ret = i + 2
#            print('1')
            break
        elif((myCards[checkNell] == 1) and (myCards[checkAce] == 1) and ((colOutput[i] - 2) > 2)):
            ret = i + 2
#            print('2')
            break
        elif((myCards[checkBuur] == 1) and (myCards[checkNell] == 1) and (ace > 1) and ((colOutput[i] - 3) > 0)):
            ret = i + 2
#            print('3')
            break
        elif((myCards[checkBuur] == 1) and ((colOutput[i] - 1) > 2)):
            ret = i + 2
#            print('4')
            break
        elif((colOutput[i] > 4)):
            ret = i + 2
#            print('5')
            break
        checkBuur += 9
        checkNell += 9
        checkAce += 9
    
    if(ret == None): #in case the player has no special combinations, select the playstyle whith which the player can get the most points regardless of whether he wins the round
        for i in range(6):
            tmp = js.CountPoints(Cards, trump = i)
            points.append(tmp[StartingPlayer])
        tmp = np.argmax(points)
        ret = tmp
     
    return ret
    



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
        if(trump != None):
            GlobalCards.append(trump)
        else:
            ps = ChooseTrump(GlobalCards, stage)
            GlobalCards.append(ps)
        startingplayer = stage
        controllarray = []
        for turn in range(9): #everyone has 9 cards
#            print("turn ",turn)
            called = None
            playedcards = [None]*4
            for player in range(4): #4 players playing one card at a time.
#                print("player ",player)
                activeplayer = (player + startingplayer) %4 #offset to different players
#                print(player," ",activeplayer)
                local = js.LocalPov(GlobalCards, activeplayer)
                suggested_move = rnn.Evaluate(ModelArray[activeplayer].predict(rnn.PrepareInput(local)))
                tmp = suggested_move
#                DebugVar = []
#                for i in range(36):
#                    DebugVar.append(js.LegalMove(local,i,called,trump = GlobalCards[36],player = 1))
                if(not js.LegalMove(local, suggested_move, called,trump = GlobalCards[36], player = 1)): #player 1 meaning that cards with value 1 are available for play (as is the case in local pov)
                    for i in range(36):
                        if(js.LegalMove(local, i, called, trump = GlobalCards[36], player = 1)):
                            suggested_move = i
                    #just to make sure it doesnt play the "playstyle"
                    if(tmp==suggested_move):
                        intermediate = local.index(1)
                        if(js.LegalMove(local,suggested_move, None, trump = GlobalCards[36], player = 1)):
                            pass #yes I know it aint pretty, but im tired, its 01:19 27:04:2019
#                            print("Won't win but not incorrect (more of a test fuck off)\nalso, if this happens randomly, let me know it worked (ST) thx.\n\n")
                        elif(intermediate != 36):
                            suggested_move = intermediate
                            tmp = suggested_move
                
                #malus
                if(tmp != suggested_move):
                    points[activeplayer] -= 10000
#                    print("nay")
#                else:
#                    print("Praise the sun")
                
                #set the called colour
                if(player == 0):
                    called = js.Colour([suggested_move])
                    called = called[0]
                GlobalCards[suggested_move] = 4 + activeplayer
                controllarray.append(suggested_move)
                playedcards[activeplayer] = suggested_move
#                print(playedcards)
#            print(playedcards)
#            print("\ncontrollarray\n",controllarray,"\n")
            for i in range(4):
                GlobalCards[playedcards[i]] = i + 8
            startingplayer = js.RoundWinner(playedcards, GlobalCards[36], startingplayer)
        
        #screwing up globalcards, but wont need them after anyway:
        for i in range(36):
            GlobalCards[i] -= 8
        score = js.CountPoints(GlobalCards)
#        print(len(score))
#        print(score)
        for i in range(4):
            points[i] += score[i]
        
    if(queue == None):
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
        rnn.Mutate(modellist[i], 0.3*i+0.1)
#        print("mutated")
    print("starting...")
#    print(SingleGame(modellist))
    points = [0]*4
    for i in tqdm(range(100)):
        score = SingleGame(modellist)
        for i in range(4):
            points[i] += score[i]
    print("Points:\n", points)
#    
#    for i in range(15):
#        cards = js.Shuffle()
#        cards.append(np.random.randint(6))
#        print(rnn.Evaluate(modellist[0].predict(rnn.PrepareInput(cards))))
#    
    
        