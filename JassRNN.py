# -*- coding: utf-8 -*-
"""
Project:       Deep Jass

File:           Jassen.py

Purpose:        Recurring Neural Network to learn how to play cards.

Created on:     17.03.2019 16:02:49
Author:         Simon Thür; Marc Matter

Copyright © 2019 Marc Matter, Michael Siebenmann, Ramon Heeb, Simon Thür. All rights reserved.
"""
#print("______________________________\nJassRNN.py               Start\n______________________________")
import tensorflow as tf
import numpy as np
import Jassen as js
import multiprocessing
import time
#from Jassen import *
#Feel free to delete the folowing if it is in any way a hindrance
GlobalCards = js.Shuffle()
GlobalCards.append(0) #playstyle
LocalCards = []
for i in range(4):
    LocalCards.append(js.LocalPov(GlobalCards,i)) #Is in RNN Input format, but needs to be converted to 3d array (only input if len()=37)
#for i in range(len(LocalCards)):
#    print("Player "+str(i)+" "+str(js.CsTT36(LocalCards[i],1))+"\n")

# =============================================================================
#           #Test, whether js.LocalPov() works properly, cuz I wasn't sure, but appears to be fine...
# print("Start Test")
# for z in range(100):
#     for i in range(4):
#         if(js.CsTT36(GlobalCards,i)==js.CsTT36(LocalCards[i],1)):
#             print("Identical")
#         else:
#             print(js.CsTT36(GlobalCards,i))
#             print(js.CsTT36(LocalCards,1))
#     GlobalCards =js.Shuffle()
#     for i in range(4):
#         LocalCards[i]=js.LocalPov(GlobalCards,i)
# =============================================================================
    


def TrainArrayInputRaw():
    '''
    Creates a array (36 cards) where every card gets one of the 11 possible conditions randomly assigned to it. 
    There are also two additional arrayindexes which determine the playstyle as well as which colour is called for.
    Its purpose is to create random training data for the NN automatically.
    
    Returns:
        Array[int]:
            Global Card array (36 Card layout) signified as follows:
                0:	Player 0 holds card\n
                1:	Player 1 holds card\n
                2:	Player 2 holds card\n
                3:	Player 3 holds card\n
                4:	Player 0 plays card\n
                5:	Player 1 plays card\n
                6:	Player 2 plays card\n
                7:	Player 3 plays card\n
                8:	Player 0 has played card\n
                9:	Player 1 has played card\n
                10:	Player 2 has played card\n
                11:	Player 3 has played card\n
            
            Two additional arrayelements [36] and [37]:
                [36]: Holds information about the desired playstyle:
                    0: Oben runter\n
                    1: Unten rauf\n
                    2: Trump is rose\n
                    3: Trump is acorn\n
                    4: Trump is bell\n
                    5: Trump is shield\n
                [37]: Holds information about whether a colour is called for or the player is free to choose one.
                    
    '''
    Ret = js.Shuffle()
    called = None
    for i in range(np.random.randint(20)):
        Ret[np.random.randint(36)]=np.random.randint(8,12)
    for i in range(np.random.randint(3)):
        index = np.random.randint(36)
        while(Ret[index]<8 and Ret[index]>4):
            index = np.random.randint(36)
        Ret[index] = 7-i
        called = index
    
    
    Ret.append(np.random.randint(6))
    if(called!=None):
        called = js.Colour([called])
        Ret.append(called[0])
    else:
        Ret.append(None)
    return Ret

def CheckArray(trainInput):
    '''
    Checks whether an array is fit for our intended training programm. An array is considered fit when there is only one 
    legal move to make. 
    
    Parameters:
        trainInput (array[int]):
            An array with 38 indexes whereof the first 36 indexes are the 36 cards each with its own condition, 
            the 37th is the playstyle and the 38th is the called for colour.
        
    Returns:
        None:
            There is no legal move left to make.
        int:
            Index of the card which has to be played during the players next move.
    '''
    Ret = []
    for i in range(36):
        if(js.LegalMove(trainInput,i,trainInput[37])):
            Ret.append(i)
    if(len(Ret)!=1):
        Ret = None
    else:
        Ret = Ret[0]
     
    return Ret

def TrainArray(length):
    '''
    Creates an 2d-array which holds multiple training arrays as well as the only legal move for each of these training arrays.
    
    Parameters:
        length(int):
            Defines how many indexes the resultating array ought to have.
        
        
            
    Returns:
        array[int][int]:
            [int][0]: training array (created with TrainArrayInputRaw).
            [int][1]: only legal move for the corresponding training array.
    '''
    Ret=[0]*length
#    print(Ret)
    for i in range(length):
#        print((i+1)/length*100,"%")
        Ret[i] = [0]*2
        RawArray = TrainArrayInputRaw()
        while(CheckArray(RawArray)==None):
            RawArray = TrainArrayInputRaw()
        Ret[i][1] = CheckArray(RawArray)
        RawArray.pop(37)
        Ret[i][0] = RawArray
        
#    print("\n")
    
    return Ret

def test(length):
    
    return length


def MPTrainArrayIntermediate(length,queue):
    tmp = test(TrainArray(length))
#    print(tmp)
    queue.put(tmp)

def MPTrainArray(length,processes): #Not working yet pls fix thx.
    '''
    Creates a 2d-array which holds multiple training arrays as wella s the only legoa move for each of these training arrays.
    Uses Multiple cores to accelerate the creation of this training set.
    
    Parameters:
        length(int):
            Defines how many indexes the resulting array ought to have.
        
        processes(int):
            Defines how many processes (CPU cores) are to be used.
        
    Returns:
        array[int][int]:
            [int][0]: training array
            [int][1]: only legal move for the corresponding training array.
    '''
    
    
    queue = multiprocessing.Queue()
    process_list=[]
    for i in range(processes):
        process_list.append(multiprocessing.Process(target=MPTrainArrayIntermediate,args=(length,queue)))
    for prcs in process_list:
        prcs.start()
    for prcs in process_list:
        prcs.join()
    print("joined")
    Ret = []
    while not queue.empty():
        Ret.append(queue.get())
    return Ret



# =============================================================================
# TESTtrainArray = TrainArray(100)
# for i in range(len(TESTtrainArray)):
#     print(js.CTT(TESTtrainArray[i][1]))
# =============================================================================

    #Test some NN stuff
sess = tf.Session()
Model = tf.keras.models.Sequential()
Model.add(tf.keras.layers.InputLayer(input_shape=(1,37),name='input'))
#Model.add(tf.keras.layers.Dense(36, name='Dense1'))
Model.add(tf.keras.layers.CuDNNLSTM(40, name='LSTM1',return_sequences=True))
Model.add(tf.keras.layers.CuDNNLSTM(36, name='LSTM2',return_sequences=True))
Model.add(tf.keras.layers.Dropout(0.5))
Model.add(tf.keras.layers.Dense(36, activation='softmax'))

Model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])        #maybe if we decide to use handmade training data for not playing incorrect cards.
LocalCards0 = np.reshape(LocalCards[0],[1,1,37])                                            #reshaped for RNN input

LocalCards0TF = tf.convert_to_tensor(LocalCards0,dtype=tf.float32)             #Convert to float
#tf.initialize_all_variables()      #absolutly necessary! but still not working...?

# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# # # # print(LocalCards0)
# # # # Result = sess.run(Model.predict(LocalCards0TF,steps=1))
# # # # print(sess.run(Result))
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


#print(sess.run(tf.constant(5)))



#yeah no, fuck it, using the stuff on top now
# =============================================================================
# inputs = tf.keras.Input(shape=(36,))
# x = tf.keras.layers.InputLayer(input_shape=inputs)
# outputs = tf.keras.layers.Dense(36, activation=tf.nn.softmax)(x)
# model = tf.keras.Model(inputs=inputs, outputs=outputs)
# 
# TfArray=tf.constant([0,0,LocalCards[0]],name = 'TfArray',dtype=tf.uint8)
# 
# print(model)
# 
# TestLayer = tf.keras.layers.CuDNNGRU(units=36)
# 
# x = tf.placeholder(tf.float32, shape=[None,None,36])
# init = tf.global_variables_initializer()
# sess.run(init)
# #print(sess.run(TfArray))
# print(LocalCards[0])
# print(sess.run(x))
# #print(sess.run(TestLayer(x)))
# #print(sess.run(TestLayer(TfArray)))
# =============================================================================

sess.close()



if __name__ == '__main__':
    
#    print(TrainArray(5))
    TESTtrainArray = MPTrainArray(100,1)
    for i in range(len(TESTtrainArray)):
        print(js.CTT(TESTtrainArray[i][1]))


#print("______________________________\nJassRNN.py                 End\n______________________________")