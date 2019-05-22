# -*- coding: utf-8 -*-
"""
Project:       Deep Jass

File:           Dealer.py

Purpose:        Assortment of functions required to train the Recurrent Neural Network to play against other Networks (Simulate a game)

Created on:     24.04.2019 11:02:27
Author:         Simon Thür; Marc Matter

Copyright © 2019 Marc Matter, Michael Siebenmann, Ramon Heeb, Simon Thür. All rights reserved.
"""


import numpy as np
import multiprocessing #*NOTE Multiprocessing ?usually? does not work in iPython (Spyder). To use MP, run file through Anaconda: navigate to folder and type: `python Dealer.py`
from tqdm import tqdm  #using anaconda/pip: pip install tqdm
import JassRNN as rnn
import Jassen as js
from time import ctime
from os import system
from time import sleep
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
    Raises:
        SystemExit:
            If this function is faulty in a vital part, it will force quit.
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
                
                
                '''Gonna revise this, seems fishy...'''
                
                
# =============================================================================
#                 if(not js.LegalMove(local, suggested_move, called,trump = GlobalCards[36], player = 1)): #player 1 meaning that cards with value 1 are available for play (as is the case in local pov)
#                     for i in range(36):
#                         if(js.LegalMove(local, i, called, trump = GlobalCards[36], player = 1)):
#                             suggested_move = i
#                     #just to make sure it doesnt play the "playstyle"
#                     if(tmp==suggested_move):
#                         intermediate = local.index(1)
#                         if(js.LegalMove(local,suggested_move, None, trump = GlobalCards[36], player = 1)):
#                             pass #yes I know it aint pretty, but im tired, its 01:19 27:04:2019
# #                            print("Won't win but not incorrect (more of a test fuck off)\nalso, if this happens randomly, let me know it worked (ST) thx.\n\n")
#                         elif(intermediate != 36):
#                             suggested_move = intermediate
#                             tmp = suggested_move
# =============================================================================
                ###############################################################
#               Gonna rewrite this bit
#               Step by step...
                ###############################################################
                
                
                if(not js.LegalMove(local, suggested_move, called,trump = GlobalCards[36], player = 1)): #player 1 meaning that cards with value 1 are available for play (as is the case in local pov)
                                    #does player hold card?
                    if(local[suggested_move]!=1):#malus for not holding a card.
                        points[activeplayer] -= 100000
                                    #what card should be played...
                    if(called==None):
                        try:
                            suggested_move = local.index(1)
                        except:
                            print('Holy fucking shit we fucked up pls lets never get his message (SingleRound in Dealer.py , around line 107 as of writing this), if this shows up we\'re so fucking screwed')
                            raise SystemExit('fuck this shit i\'m out') #not sure if this function exitst but fuck it, lets hope we never find out.
                            
                                    #find card with appropriate color
                    else:
                        i = called*9
                        while(i<(called+1)*9):
                            if(local[i]==1):
                                suggested_move = i
                                break
                            i += 1
                                    #if no card with correct colour was found:
                    if(tmp==suggested_move):
                        try:
                            suggested_move = tmp =local.index(1) #tmp is equal because no wrong color was played.
                        except:
                            print('Holy fucking shit we fucked up pls lets never get his message (SingleRound in Dealer.py , around line 107 as of writing this), if this shows up we\'re so fucking screwed')
                            raise SystemExit('fuck this shit i\'m out') #not sure if this function exitst but fuck it, lets hope we never find out.
                        
                
                
                '''yes, very fishy...
                also, I wanna add different mali(?) for different fauxpass.
                also, fuck off ill write how I understand it so screw spellingz
                (ill do it later, gotta do smth first rn brb (letting it train so this might get pushed, hence the message(also, not sure if its training correctly as I mentioned this part might be fishy)))
                '''
                
                #malus for color
                if(tmp != suggested_move):
                    points[activeplayer] -= 1000
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
            ModelArray[i].reset_states()
        
    if(queue == None):
        return points
    else:
        queue.put(points)

def TrainTable(model_list, epochs = 1000, batch = 10, mutations = [0.01], verbose = True):
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
            Defaults to 0.01
        verbose (boolean):
            Determines whether a progressbar is displayed (shows for True)
            
    Returns:
        Array(tf.keras.model.sequential)
        a list of RNNs, where the best one is at index `0` and the worst one is at index `3`
    '''
    
    
    '''apparently, numpy is not compatible with MPing tf models. so, I guess remove numpy from this part? (or sneak around it by using evaluate instead of np.argmax()
    this might backfire though, because evaluate is lietarylla armgax. eh. will see tmrw, define queue in parameters 
    
    and define queue in SingleGame you lazy shit!
    fuck off^
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
        mutations.append(0.01)
    while(len(mutations) > 3):
        mutations.pop()
    for i in mutations:
        if(i == None):
            i = 0.01
        elif(i < 0):
            i = 0.01
        elif(i > 1):
             i = 0.01
    
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

def TFSessMP(name,epochs,batch,mutations,verbose):
    '''
    TFSessMP
    An intermediate layer between MPTrain() and TrainTable(), which is responsible for crossloading RNNs (as they are stored in ram which complicates things a bit when using MP)
    It loads the weights from the harddisk where it was saved by MPTrain(). This has the tradoff between speed and backups on the go.
    
    Parameters:
        name (str):
            the name with which the fiels were stored on the harddisk. (the same that was given to MPTrain(name="MPTDefault"))
        
        epochs (int):
            the amount of epochs to be handed to `TrainTable()`
        
        batch (int):
            the amount of batches to be handed to `TrainTable()`
        
        mutations(array[float]):
            the mutations to be given to `TrainTable()`
        
        verbose (boolean):
            the verbose value to be given to `TrainTable()` (which will show the progress bar (works fine in MP))
        
        queue (multiprocessing.Queue()):
            `removed`
        
    Returns:
        None
        stores the weights on the harddisk, where it found them.
    '''
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

def MPTrain(model_list, generations = 100, epochs = 25000, batch = 10, mutations = 0.003,name = "MPTDefault"):
    '''
    MPTrain trains a list of (at this point in time) 36 RNNs and then returns this list.
    The training works as follows: seperate RNNs to 8 tables; randomly mutate and check which one is the best. once every 5 generations find the ultimate best RNN and set it to each table.
    
    Parameters:
        model_list (Array[tf.keras.model.sequential]):
            A list of RNNs that will face each other and improve. (list will be lenghtend or shortend as needed, can be empty.)
        
        generations(int):
            Defines for how many generations RNNs will be trained. Every 5th generation will place the best RNN at each table.
            Defaults to generations = 100
        
        epochs (int):
            Defines how many epochs will be made at each table before mixing. (epoch is passed down to `TFSessMP()` and from there to `TrainTable()`)
            Defaults to epochs = 25000
        
        batch (int):
            Defines how many batche will be pataken in each epoch. (batch is passed down to `TFSessMP()` and from there to `TrainTable()`)
            Defaults to batch = 10
        
        mutations (int):
            the desired mutation factor (will be passed donw to `TFSessMP()` and from there to `TrainTable()`)
            Defaults to mutations = 0.003
        
        name (str):
            The name with which RNNs are to be stored and found on the harddisk. (will also influence the points.txt file in /points where the points of the best player are written to)
            Defaults to name = 'MPTDefault'
    
    Returns:
        Array[tf.keras.model.sequential]:
            An array of RNNs.
    '''
    #Basics of MP
    processes = multiprocessing.cpu_count() if multiprocessing.cpu_count() < 8 else 8 ##I tend to run out of ram if its above 12 / starting from 10 and up it gets tricky
#    processes = 10
    
    ########################################################################################################
#    processes = 2
    ########################################################################################################
    
            #amount of required RNNs
    mutations = [mutations]*2
    while(len(model_list)<processes*4):
        model_list.append(rnn.GetModel())
    while(len(model_list)>processes*4):
        model_list.pop()
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
            process_list.append(multiprocessing.Process(target=TFSessMP, args=(MPname, epochs, batch, mutations, True)))#define process (hope it works... because there are some syntax cabbages I dislike here...)
        for prcs in process_list:
#            print("before prcs ",prcs)
            prcs.start() #start processes
#            sleep(10)        was an experiment, was successful-ish... idea was that windows tends to hog ram and as such if one were to slowly slice it away one could get more before recie3veing an error. This works, but then again, what's the point? it's just more data to crunch if you start even more processes, and loading and saving takes even longer so... yeah, ima pass on that.
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
        
        
        #new table = 3 of las rounds winners
        for table in range(processes):
            for model in range(1,4):
                model_list[table][model] = model_list[(table+1+table)%processes][0]
        
        if(generation%5!=0):
            #and the final player is a wild card
            print("Mutatin' dem Babies")
            for table in tqdm(range(processes)):
                model_list[table][3] = rnn.Reproduce(model_list[np.random.randint(processes)][np.random.randint(3)],model_list[np.random.randint(processes)][np.random.randint(3)],np.random.random())
        else:
            #plant best player into all rounds
            print("Find best RNN and spread it 'round")
            best = BestPlayer(model_list)
            with open('points/'+name+'-points'+'.txt', 'a') as f:
                print(best[1],"\t => avg:\t",int(best[1]/(processes*3+1)),"\t",ctime(),file=f) #include avg in out (note that avg. is over two rounds)
            print(best[1])
            bestmodel = model_list[int(best[0]/4)][best[0]%4] #check this pls
            
            #save it usefully, also, lets test this a bit...
#            rnn.pb_conversion(bestmodel,timestamp = ctime())
            
            for table in range(processes):
                model_list[table][3] = bestmodel
                
            #TFLite. fuck this thing.
            #it even fucking wrecks the code when you've encapsulated it in a (or rather two) failsafe...
# =============================================================================
#             try:
#                 rnn.TFLite(bestmodel)
#             except:
#                 print("fucking TFLite ain't working. Cabbage.")
# =============================================================================
                
                
            #if git is installed, push changes to GitHub
            system('git commit -a -m "_AutoPushWeights_"')
            system('git push')
            
            #maybe lend a helping hand to one of them...
            if(generation!=generations-1 and generation%2==0):
                try:
                    rnn.TrainModelBasics(model_list[np.random.randint(len(model_list))][3],100000,True)
                except:
                    print('yeah, it stopped working... but it works when only calling the function from say the prompt? idk, ill look at it tmrw or sth. (also, if this msg shows after 18.05.2019 hit me up, I prolly forgot or screwed up sth else.')
    
    
    
    
    return model_list

def BestPlayerLtd(model_list,rounds):
    '''
    BestPlayerLtd finds the best RNN of 4 over a certain amount of rounds.
    Parameters:
        model_list (array[tf.keras.sequential]):
            An array len(model_list)=4 of RNNs
        
        rounds (int):
            Determines for how many rounds the participating RNNs need to play each other.
    
    Returns:
        Array[int]:
            The points each RNN made (points[c] ≙ points made by model_list[c])
    '''
    points = [0]*4
    for _ in range(rounds):
        roundpoints = SingleGame(model_list)
        for model in model_list:
            model.reset_states()
        for i in range(4):
            points[i] += roundpoints[i]
    
    
    return points

def BestPlayer(model_list):
    '''
    BestPlayer() finds the best RNN of the given input RNNs.
    
    Parameters:
        model_list (Array[tf.keras.model.sequential]):
            An Array containing 4 or more RNNs (len(model_list)>=4).
    
    Returns:
        Array[int]:
            Array[0]:
                The index of the best RNN
            Array[1]:
                How many points the best RNN made.
    '''
    model_list = np.reshape(model_list,-1) ##just because of MPTrain, where i'll prolly forget to reshape them... so yeah, now i definetly wont but hey
    if(len(model_list)%4!=0):
        print("len(model_list) = ",len(model_list),"   ::  !=4\nthis may throw an error down the line (not this function though, as it is now compatible with any len as long as len>=4)")
    points = []
    for i in range(len(model_list)):
        points.append(0)
    table = [None]*4
    
    #lazy thought...
    #take one player, iterate the rest, then iterate the one player onece everyone was iterated through
    print(len(model_list))
    for player in tqdm(range(len(model_list))):
        table[0] = model_list[player]
        for other_players in range(len(model_list)):
            for opponent in range(1,4):
                table[opponent] = model_list[(other_players + opponent)%len(model_list)]
            
            ##get sum points
            score = BestPlayerLtd(model_list,2)
            points[player] += score[0]
            for opponent in range(1,4):
                points[(other_players + opponent)%len(model_list)] = score[opponent]
    
    Ret = [np.argmax(points),points[np.argmax(points)]]
    
    return Ret
    
    
# =============================================================================
#     
#     for i in range(len(model_list)%4):
#         table.append([None]*4)
#     for model in range(len(model_list)):
#         if(model%len(model_list)==0 or model%len(model_list)==1):
#             table[0][model%4] = model_list[model]
#         elif(model%3 == 0 or model%3 == 2 or len(model_list)==8):
#             table[1][model-2]
# =============================================================================


# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    system('cls')
    array = []
    
    
    #just a test
    for r in range(8):
        for c in range(4):
            array.append(rnn.GetModel())
            rnn.LoadWeights(array[r+c],("testsmall"+"_"+str(r)+"-"+str(c)))
#    print("loaded models")
#    print(BestPlayer(array))
    
    MPTrain(array,name = 'testsmall')
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
#    cards = js.Shuffle() #Testing ChooseTrump
#    tmp = iChooseTrump(cards, 0) 
#    print(tmp) 
        