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


def TrainTable(model_list,epochs=1000,batch=10, mutations = [0.03],verbose=True,queue = None):
    '''
    TrainTable entertains one table of players (rnn models) while slowly mutating and improving them (at random so it will take a while)
    Parameters:
        model_list (Array[tf.keras.model.sequential]):
            an array of models. this array will be extended (at random) or diminished to the length of 4
        epochs (int):
            determines for how many epochs is to be trained (models are updated/learn once every epoch).
            defaults to 1000, but it is recommended to do upwards of 10000
        batch (int):
            determines how many games are played to determine which RNN is the best.
        mutations (Array[float]):
            indicates how much RNNs are mutated.
            defaults to 0.03
        verbose (boolean):
            determines whether a progressbar is displayed (shows for True)
    '''
    
    
    '''apparently, numpy is not compatible with MPing tf models. so, I guess remove numpy from this part? (or sneak around it by using evaluate instead of np.argmax()
    this might backfire though, because evaluate is lietarylla armgax. eh. will see tmrw
    '''
    
    
    #setup
    #right length
    if(len(model_list) != 4):
        print("len(model_list) = ",len(model_list),"    :: !=4\nmodel_list will be corrected")
        while(len(model_list)<4):
            model_list.append(rnn.GetModel())
        while(len(model_list)>4):
            model_list.pop()
            
    #just in case of None
    for i in model_list:
        if(i==None):
            i = rnn.GetModel()
    #setting mutationfactors, if they weren't specified
    while(len(mutations)<3):
        mutations.append(0.03)
    while(len(mutations)<3):
        mutations.pop()
    for i in mutations:
        if(i==None):
            i = 0.03
        elif(i<0):
            i = 0.03
        elif(i>1):
             i = 0.03
    
    #at this point, model_list should be ready for use.
    #models are mutated once every epoch
    for epoch in (tqdm(range(epochs)) if verbose else range(epochs)):
        points = [0,0,0,0] #each epoch resets everything
        for batch in range(batch):
            score = SingleGame(model_list)
            for i in range(4):
                points[i] +=score[i]
        best = np.argmax(points)
        #mutate models for them to improve
        if(epoch != epochs-1):
            model_list[0] = model_list[best]
            for z in range(1,4):
                model_list[i] = model_list[0]
                rnn.Mutate(model_list[i],mutations[i-1])
        #if last epoch, dont mutate models, but sort them and return.
        else:
            tmp=[]
            for i in range(4):
                tmp.append(model_list[np.argmax(points)])
                print("got here")
                points.pop(np.argmax(points))
            model_list = tmp
    if(queue==None):
        return model_list
    else:
        queue.put(model_list)

def MPTrain(model_list,generations = 100, epochs = 10000, batch = 10,mutations = 0.03):
    '''
    '''
    #Basics of MP
    processes = multiprocessing.cpu_count()
    queue = multiprocessing.Queue()
    
    #amount of required RNNs
    while(len(model_list)<processes*4):
        model_list.append(rnn.GetModel())
    #4RNNs for each table
    np.reshape(model_list,[processes,4])
    process_list = []
    for i in range(processes):
        process_list.append(multiprocessing.Process(target=TrainTable, args=(model_list[i], epochs, batch, [mutations], False, queue)))#define process (hope it works... because there are some syntax cabbages I dislike here...)
    for prcs in process_list:
        prcs.start() #start processes
    for i in range(processes):
        model_list[i] = queue.get()
    for prcs in process_list:
        prcs.join()
    
    return process_list

# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    MPTrain([])
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
    print("test start")
    modellist = TrainTable([],epochs = 10000,verbose = True)
    print("test complete")
    
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
    
        