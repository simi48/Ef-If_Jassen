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
        
        trump (int):
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
            ps = js.ChooseTrump(GlobalCards, stage)
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


def TrainTable(model_list, epochs = 1000, batch = 10, mutations = [0.03], verbose = True):
    '''
    TrainTable entertains one table of players (rnn models) while slowly mutating and improving them (at random so it will take a while)
    Parameters:
        model_list (Array[tf.keras.model.sequential]):
            An array of models. This array will be extended (at random) or diminished to the length of 4
        epochs (int):
            Determines for how many epochs is to be trained (models are updated/learn once every epoch).
            Defaults to 1000, but it is recommended to do upwards of 10000
        batch (int):
            Determines how many games are played to determine which RNN is the best.
        mutations (Array[float]):
            Indicates how much RNNs are mutated.
            Defaults to 0.03
        verbose (boolean):
            Determines whether a progressbar is displayed (shows for True)
    '''
    
    
    '''apparently, numpy is not compatible with MPing tf models. so, I guess remove numpy from this part? (or sneak around it by using evaluate instead of np.argmax()
    this might backfire though, because evaluate is lietarylla armgax. eh. will see tmrw, define queue in parameters 
    and define queue in SingleGame you lazy shit!
    '''
    
    
    #setup
    #right length
    if(len(model_list) != 4):
        if(verbose):
            print("len(model_list) = ",len(model_list),"    :: !=4\nmodel_list will be corrected")
        while(len(model_list) < 4):
            model_list.append(rnn.GetModel())
        while(len(model_list) > 4):
            model_list.pop()
            
    #just in case of None
    for i in model_list:
        if(i == None):
            i = rnn.GetModel()
    #setting mutationfactors, if they weren't specified
    while(len(mutations) < 3):
        mutations.append(0.03)
    while(len(mutations) > 3):
        mutations.pop()
    for i in mutations:
        if(i == None):
            i = 0.03
        elif(i < 0):
            i = 0.03
        elif(i > 1):
             i = 0.03
    
    #at this point, model_list should be ready for use.
    #models are mutated once every epoch
    for epoch in (tqdm(range(epochs)) if verbose else range(epochs)):
        points = [0,0,0,0] #each epoch resets everything
        for batch in range(batch):
            score = SingleGame(model_list)
            for i in range(4):
                points[i] += score[i]
        best = np.argmax(points)
        #mutate models for them to improve
        if(epoch != epochs-1):
            model_list[0] = model_list[best]
            for z in range(1,4):
                model_list[i] = model_list[0]
                rnn.Mutate(model_list[i], mutations[i-1])
        #if last epoch, dont mutate models, but sort them and return.
        else:
            tmp = []
            for i in range(4):
                tmp.append(model_list[np.argmax(points)])
#                print("got here")
#                print(points)
#                points[np.argmax(points)] = -99999999999999999999
                model_list.pop(np.argmax(points))
                points.pop(np.argmax(points))
            model_list = tmp
            print(model_list)
    
    return model_list

def TFSessMP(name,epochs,batch,mutations,verbose,queue):
#    Ret = []
    model_list = []
#    print("1")
#    for i in range(len(modelweights)):
    for i in range(4):
        model_list.append(rnn.GetModel())
#        print("2 (",i,")")
#        model_list[i].load_weights(modelweights[i])
        nametmp = name+str(i)
        print(nametmp)
        print(name)
        rnn.LoadWeights(model_list[i],(name+str(i)))
#        print("3 (",i,")")
#    print("got here")
#    model_list = TrainTable(model_list,epochs,batch,mutations,verbose)
    model_list = TrainTable(model_list,epochs,batch,mutations,verbose)
    for i in range(len(model_list)):
        rnn.SaveWeights(model_list[i],(name+str(i)))
#    queue.put(None)
    '''make Ret var from RAM and not VRAM, or save to harddisk?'''

def MPTrain(model_list, generations = 100, epochs = 10000, batch = 10, mutations = 0.03,name = "MPTDefault"):
    '''
    '''
    #Basics of MP
#    processes = multiprocessing.cpu_count() ##I tend to run out of ram this way
    processes = 8
    queue = multiprocessing.Queue()
#    processes = 2
    
            #amount of required RNNs
    while(len(model_list)<processes*4):
        model_list.append(rnn.GetModel())
    for generation in tqdm(range(generations)):
        
        #4RNNs for each table
#        weights = []
#        for i in model_list:
#            weights.append(i)
        model_list = np.reshape(model_list,[processes,4])
        
#        print("\n"*100)
#        print(model_list)
#        print(model_list[0][0])
        
        #########
        #save weights
        for r in range(len(model_list)):
            for c in range(len(model_list[r])):
                tmpName = (""+name+"_"+str(r)+"-"+str(c))
                print(tmpName)
                rnn.SaveWeights(model_list[r][c],tmpName)
        #########
        
        process_list = []
#        model_list = [] #clear up some (v)ram? not sure if it helps though. if required, be sure to add another model_list below with RNNs inside it.
        for i in range(processes):
            
            #########
            MPname = name+"_"+str(i)+"-" ##as in line244 (ish) where the model was saved. the c) will be added in TFSESSMP()
            #if not required remove `name` from prcs_list.append(process)
            #########
            process_list.append(multiprocessing.Process(target=TFSessMP, args=(MPname, epochs, batch, [mutations], True, queue)))#define process (hope it works... because there are some syntax cabbages I dislike here...)
        for prcs in process_list:
#            print("before prcs ",prcs)
            prcs.start() #start processes
#            print("prcs",prcs,"started")
        print(process_list)
#        for i in range(processes):
##            model_list[i].set_weights(queue.get())     needs to get fixed   maybe
#            pass
        for prcs in process_list:
            prcs.join()
            print(prcs)
        
        
        #########
        #get weights
        for r in range(len(model_list)):
            for c in range(len(model_list[r])):
                rnn.LoadWeights(model_list[r][c],(""+name+"_"+str(r)+"-"+str(c)))
        #########
        
        #Now we have a list of several models; gotta find the best one I guess? or just breed and relocate them...
        #for now ill just breed and relocate...
        
        for modelout in range(processes):
            pass
    
    
    
    
    return model_list

# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    print("\n"*100)  ##cls
    MPTrain([],epochs = 500)
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
# =============================================================================
#     print("test start")
#     modellist = TrainTable([],epochs = 10000,verbose = True)
#     print("test complete")
#     
#     print("starting...")
# #    print(SingleGame(modellist))
#     points = [0]*4
#     for i in tqdm(range(100)):
#         score = SingleGame(modellist)
#         for i in range(4):
#             points[i] += score[i]
#     print("Points:\n", points)
# =============================================================================
#    
#    for i in range(15):
#        cards = js.Shuffle()
#        cards.append(np.random.randint(6))
#        print(rnn.Evaluate(modellist[0].predict(rnn.PrepareInput(cards))))
#    
    cards = js.Shuffle() #Testing ChooseTrump
#    tmp = iChooseTrump(cards, 0) 
    print(tmp) 
        