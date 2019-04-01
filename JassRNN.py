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
                - 0:	Player 0 holds card
                - 1:	Player 1 holds card
                - 2:	Player 2 holds card
                - 3:	Player 3 holds card
                - 4:	Player 0 plays card
                - 5:	Player 1 plays card
                - 6:	Player 2 plays card
                - 7:	Player 3 plays card
                - 8:	Player 0 has played card
                - 9:	Player 1 has played card
                - 10:	Player 2 has played card
                - 11:	Player 3 has played card
            
            Two additional arrayelements [36] and [37]:
                [36]: Holds information about the desired playstyle:
                    - 0: Oben runter
                    - 1: Unten rauf
                    - 2: Trump is rose
                    - 3: Trump is acorn
                    - 4: Trump is bell
                    - 5: Trump is shield
                [37]: Holds information about whether a colour is called for or the player is free to choose one
                    
                    
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
    tmp = TrainArray(length)
#    print(tmp)
    queue.put(tmp)


def MPTrainArray(length, base = 95):
    '''
    Creates a 2d-array which holds multiple training arrays as wella s the only legoa move for each of these training arrays.
    Uses Multiple cores to accelerate the creation of this training set.
    
    Parameters:
        length(int):
            Defines how many indexes the resulting array ought to have. (will be rounded to a multiple of `base` (defaults to the max of 95)
        
        base(int):
            Defines the base value each process will calculate. Default to the max=95
        
    Returns:
        array[int][int]:
            [int][0]: training array
            [int][1]: only legal move for the corresponding training array.
    '''
    if(base>95):
        print("MPTrainArray(length, base) base was greater than 95: ",base,"\nBase was set to 95.")
        base = 95
    processes = int(length/base)
    queue = multiprocessing.Queue()
    print("MPTrainArray, using `",processes,"` processes with base=`",base,"`")
    process_list=[]
    for i in range(processes):
        process_list.append(multiprocessing.Process(target=MPTrainArrayIntermediate,args=(base,queue)))#define process

    for prcs in process_list:
        prcs.start() #start processes
    Collect = []

    for i in process_list:
        Collect.append(queue.get())

#join processes (terminate them once their done) this is clearly the issue...
#apparantly wont close because there is stuff in the queue?
    for prcs in process_list:
        prcs.join()
    Ret = []
    for i in Collect:
        Ret = Ret + i
    
    return Ret



# =============================================================================
# TESTtrainArray = TrainArray(100)
# for i in range(len(TESTtrainArray)):
#     print(js.CTT(TESTtrainArray[i][1]))
# =============================================================================

def GetModel():
    '''
    Used for acquiring the RNN Model (useing LSTM Cells) with input size (1,1,37) and output size (1,1,36)
    
    Returns:
        Tensorflow_Model
    '''
    Model = tf.keras.models.Sequential()
    Model.add(tf.keras.layers.InputLayer(batch_input_shape=(1,1,37),name='input'))
    #Model.add(tf.keras.layers.Dense(36, name='Dense1'))
    Model.add(tf.keras.layers.CuDNNLSTM(40, name='LSTM1',return_sequences=True, stateful=True)) #Stateful = remember what happended last time
    Model.add(tf.keras.layers.CuDNNLSTM(36, name='LSTM2',return_sequences=True, stateful=True))
    Model.add(tf.keras.layers.Dropout(0.5))
    Model.add(tf.keras.layers.Dense(36))
    
    Model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])        #maybe if we decide to use handmade training data for not playing incorrect cards.
    
    tf.global_variables_initializer()      #absolutly necessary! but still not working...?
    return Model


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

#sess.close()


def PrepareInput(input):
    '''
    Converts an array of length 37 into a  matrix (1,1,37), which fits the input requirements of the RNN Model (from GetModel())
    
    Parameters:
        input(array[int]):
            An array of length 37 (ideally in LocalPov format) which is to be converted to RNN Input.
            
        
    Returns:
        Numpy Matrix:
            Input Matrix for the RNN.
    '''
    return np.reshape(input,[1,1,37])


def PrepareInputArray(input_array):
    '''
    Converts an array of array (len 37) into an array of matrices (1,1,37), which fits the input requirements of the RNN Model (from GetModel())
    
    
    Parameters:
        input_array(array[array[int]])
    '''
    
    Ret=[]
    for i in input_array:
        Ret.append(PrepareInput(i))
    return Ret


def Evaluate(RNN_Output):
    Array = RNN_Output[0][0]
    highest = 0
    index = None
    for i in range(len(Array)):
        if(Array[i]>highest):
            index = i
            highest = Array[i]
            
    return index


def TrainModelBasics(model,size, Multiprocessing = False): #Multiprocessing does not work in Spyder, to make use of this execute from Anaconda/CMD
    '''
    Trains the Model to not be completely stupid
    
    Parameters:
        model(tf.keras.Model):
            TensorFlow model with input (1,1,37) and output (1,1,36)
        
        size(int):
            Determines the amount of training to be done
        
        Multiprocessing(Boolean):
            Specifies whether training should make use of Multiprocessing (default to False)
            *NOTE Multiprocessing will not work in Spyder IDE. To make use of this, execute Code in standalone console
            
    '''
    
    
    if Multiprocessing:
        training_data = MPTrainArray(size)
    else:
        training_data = TrainArray(size)
    
    '''Theres some problem with TrainArray(), because it returns a 3d array with 2 2d arrays... should not be happening like that though so will have to look at that'''
    
    
#    print(training_data)
    x = []
    y = []
    print(training_data)
    
    for i in training_data:
        x.append(i[0])
        tmp = [0]*36
        tmp[i[1]] = 1
        y.append(tmp)
    for i in x:
        print( x)
        x = PrepareInput(x)
    for i in y:
        y = np.reshape(y,(1,1,36))
    model.train_on_batch(x,y)



def SaveRNN(model, name):
    '''
    Saves the Neural Network to your Hard Disk.
    
    Parameters:
        model(tf.keras.Model):
            TensorFlow model with input (1,1,37) and output (1,1,36)
        name(String):
            The desired name under which you want so save your model.       
    '''
# =============================================================================
#     model.numpy.save(name, '_saved_wih.np', model.wih)
# =============================================================================

def LoadRNN(model, name):
    '''
    Loads the Neural Network from your Hard Disk.
    
    Parameters:
        model(tf.keras.Model):
            TensorFlow model with input (1,1,37) and output (1,1,36)
        name(String):
            The desired name under which your model was saved.        
    '''
    

# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    
    LocalCards = TrainArray(1)
    LocalCards0 = PrepareInput(LocalCards[0][0])
    Model = GetModel()
    RNN_Output = Model.predict(LocalCards0)
    Highest = Evaluate(RNN_Output)
    print("Model Output:\n",RNN_Output)
    print("Played Card (highest output)",Highest)
    print(js.CTT(Highest))
    
    
    print("\n\n\nTest Memory (using the same input several times in succession")
    for i in range(10):
        print(Evaluate(Model.predict(LocalCards0)))
#    Model.train_on_batch()
    
    print(RNN_Output)
    print(Model.predict(LocalCards0))
    print("\n\n\n\n")
    TrainModelBasics(Model,100)
#    Model.train_on_batch()
#print("______________________________\nJassRNN.py                 End\n______________________________")