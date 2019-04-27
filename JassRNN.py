# -*- coding: utf-8 -*-
"""
Project:       Deep Jass

File:           Jassen.py

Purpose:        Recurring Neural Network to learn how to play cards.

Created on:     17.03.2019 16:02:49
Author:         Simon Thür; Marc Matter

Copyright © 2019 Marc Matter, Michael Siebenmann, Ramon Heeb, Simon Thür. All rights reserved.
"""
import tensorflow as tf #using Anaconda: conda create --name tf_gpu tensorflow-gpu \n activate tf_gpu
import numpy as np
import Jassen as js
import multiprocessing #*NOTE Multiprocessing ?usually? does not work in iPython (Spyder). To use MP, run file through Anaconda: navigate to folder and type: `python JassRNN.py`
from tqdm import tqdm  #using anaconda/pip: pip install tqdm

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

def TrainArray(length, queue = None):
    '''
    Creates an 2d-array which holds multiple training arrays as well as the only legal move for each of these training arrays.
    
    Parameters:
        length(int):
            Defines how many indexes the resultating array ought to have.
        
        queue(multiprocessing.Queue()):
            Queue to which result are pushed.
            
    Returns:
        array[int][int]:
            [int][0]: training array (created with TrainArrayInputRaw).
            [int][1]: only legal move for the corresponding training array.
    '''
    SP=False #serial process y/n
    if( queue==None):
        SP=True
    if(SP):
        Ret=[0]*length
    else:
        Ret=[0]*2
    for i in range(length):
        if(SP):
            Ret[i] = [0]*2
        RawArray = TrainArrayInputRaw()
        while(CheckArray(RawArray)==None):
            RawArray = TrainArrayInputRaw()
        if(SP):
            Ret[i][1] = CheckArray(RawArray)
        else:
            Ret[1] = CheckArray(RawArray)
        RawArray.pop(37)
        if(SP):
            Ret[i][0] = RawArray
        else:
            Ret[0] = RawArray
            queue.put(Ret)
    return Ret

def test(length):
    
    return length


def MPTrainArrayIntermediate(length,queue):
    tmp = test(TrainArray(length))
#    print(tmp)
    queue.put(tmp)


def MPTrainArray(length):
    '''
    Creates a 2d-array which holds multiple training arrays as wella s the only legoa move for each of these training arrays.
    Uses Multiple cores to accelerate the creation of this training set.
    
    Parameters:
        length(int):
            Defines how many indexes the resulting array ought to have. (will be rounded to a multiple of `base`
        
        base(int):
            Defines the base value each process will calculate. Default to 50, max=95
        
    Returns:
        array[int][int]:
            [int][0]: training array
            [int][1]: only legal move for the corresponding training array.
    '''
    processes = multiprocessing.cpu_count()
    queue = multiprocessing.Queue()
    Collect = []
    process_list=[]
    prcs_length = int(length/processes)
    for i in range(processes):
        process_list.append(multiprocessing.Process(target=TrainArray,args=(prcs_length,queue)))#define process
    for prcs in process_list:
        prcs.start() #start processes
    for _ in tqdm(range(prcs_length*processes)):
        Collect.append(queue.get())
#join processes (terminate them once they're done) 
#apparantly wont close because there is stuff in the queue? problem solved by limiteing queue
    for prcs in process_list:
        prcs.join()
    
    return Collect



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
    Model.add(tf.keras.layers.CuDNNLSTM(40, name='LSTM2M_MEMORY',return_sequences=True, stateful=True)) #Stateful = remember what happended last time
    Model.add(tf.keras.layers.Dropout(0.5))
    Model.add(tf.keras.layers.Dense(36))
    
    Model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])        #maybe if we decide to use handmade training data for not playing incorrect cards.
    
    tf.global_variables_initializer()      #absolutly necessary! but still not working...?
    return Model




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
    '''
    Evaluates an array (RNN_Output) and decides at which index the highest number was located.
    
    Parameters:
        RNN_Output(Array/Matrix):
            An array in the shape the RNN has returned it's values.
    
    Returns:
        int:
            The index of the highest values, corresponding to the played card.
    
    '''
    return np.argmax(RNN_Output)


def TrainModelBasics(model,size, Multiprocessing = None): #Multiprocessing does not work in Spyder, to make use of this execute from Anaconda using `python JassRNN.py`
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
    if(Multiprocessing==None):
        Multiprocessing= size>5000
    print("Generating Data")
    if (Multiprocessing):
        training_data = MPTrainArray(size)
    else:
        training_data = TrainArray(size)
    
    '''Theres some problem with TrainArray(), because it returns a 3d array with 2 2d arrays... should not be happening like that though so will have to look at that'''
    
    x = []
    y = []
    
    for i in range(len(training_data)):
        x.append(training_data[i][0])
        tmp = [0]*36
        tmp[training_data[i][1]] = 1
        y.append(tmp)
    x=np.reshape(x,(len(x),1,1,37))
    y=np.reshape(y,(len(y),1,1,36))
    print("Adjusting Network")
    for i in tqdm(range(len(x))):
        model.fit(x[i],y[i],batch_size=1, verbose = 0,use_multiprocessing=Multiprocessing) #*NOTE it works with `use_multiprocessing=True` but I have no idea what it does or whether it helps at all
        if(i%10==0):
            model.reset_states()
            
def Mutate(model, mutation_factor, reset = True):
    '''
    Mutate takes in a model, and alters random weights to random values.
    Parameters:
        model(tf.keras.model.sequential):
            The model which is to be mutated.
        
        mutation_factor(float):
            The ratio of altered to same values. (note, this is to be judged as a binomial experiment and will not necessarily return the exact ratio given.)
            if mutation_factor=0, nothing will change, elif mutation_factor=1 everything will change.
        
        reset(boolean):
            Indicates whether the states (memory) should be reset, as it may have been mutated.
    
    
    Returns:
        (Model will be altered, as such no return value.)
        
    
    '''
    weight_Matrix = model.get_weights()
    for i in weight_Matrix:
        for z in range(len(i)):
            if(np.random.random()<mutation_factor):
                i[z] = np.random.random()*2-1 #should set a value between 1 and -1
    model.set_weights(weight_Matrix)
    if(reset):
        model.reset_states()

def SaveRNN(model, name):
    '''
    Saves the Neural Network to your Hard Disk.
    Parameters:
        model(tf.keras.Model):
            TensorFlow model with input (1,1,37) and output (1,1,36)
        name(String):
            The desired name under which you want so save your model.       
    '''
    path = 'models/' + name + '.h5'
    model.save(path)
    
def LoadRNN(model, name):
    '''
    Loads the Neural Network from your Hard Disk.
    
    Parameters:
        model(tf.keras.Model):
            TensorFlow model with input (1,1,37) and output (1,1,36)
        name:
            The name of the savefile
            
    Returns:
        model(tf.keras.Model):
            TensorFlow model with input (1,1,37) and output (1,1,36) 
    '''
    path = 'models/' + name + '.h5'
    model = tf.keras.models.load_model(path)
    return model

def SaveWeights(model, name):
    '''
    Saves the Neural Networ's weights and biases to your Hard Disk.
    
    Parameters:
        model(tf.keras.Model):
            TensorFlow model with input (1,1,37) and output (1,1,36)
        name:
            The name of the savefile
    '''
    Path = 'checkpoints/' + name
    model.save_weights(Path)
    
def LoadWeights(model, name):
    '''
    Loads the Neural Network's weights from your Hard Disk.
    
    Parameters:
        model(tf.keras.Model):
            TensorFlow model with input (1,1,37) and output (1,1,36)
        name:
            The name of the savefile
            
    Returns:
        model(tf.keras.Model):
            TensorFlow model with input (1,1,37) and output (1,1,36) 
    '''
    Path = 'checkpoints/' + name
    model.load_weights(Path)
    return model
    
def CreateCheckpointCallback(epoches):
    '''
    Creates a checkpoint for the weights of the RNN all x epoches
    
    Parameters:
        epoches(int):
            defines the gap between the checkpoint saves, for example a 5 would mean that the model creates a checkpoint all 5 epoches
    
    Returns:
        callback variable (parameter for model.fit)
    '''
    checkpoint_path = "training_1/cp.ckpt"
    cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path, save_weights_only = True, verbose = epoches)
    
    return cp_callback


def Reproduce(ModelA, ModelB,ratio=0.5):
    '''
    Creates a new RNN that is the direct descendent of the two parent models
    Parameters:
        ModelA (tf.keras.model.sequential):
            One Parent RNN
        
        ModelB (tf.keras.model.sequential):
            The other Parent RNN
        
        ratio (float):
            a float values of [0,1] determining which RNN contributes how much to the child.
    Returns:
        RNN Model
    '''
    A = ModelA.get_weights()
    B = ModelB.get_weights()
    for i in range(len(A)):
        for z in range(len(A[i])):
            if(np.random.random()<ratio):
                A[i][z] = B[i][z]
    ret = GetModel()
    ret.load_weights(A)
    return ret
    
# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    LocalCards = TrainArray(1)
    LocalCards0 = PrepareInput(LocalCards[0][0])
    Cp_callback = CreateCheckpointCallback(5) #callbacks = [Cp_callback], parameter for model.fit
    Model = GetModel()
    LoadWeights(Model,"Basic")
    #n = amount of iterations, but i reckon you guesse :)
    n = 35
    for i in range(n):
        print("Iteration ",i+1,"of ",n)
        TrainModelBasics(Model,100000)
        SaveWeights(Model,"Basic")