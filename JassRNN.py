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
from os import remove
from time import time


#Important: Makes sure that not all ge GPU memory is hogged. (noteworthy when Multiprocessing multiple RNNs)
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)



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
    if(called != None):
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
    if(len(Ret) != 1):
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
    SP = False #serial process y/n
    if( queue == None):
        SP = True
    if(SP):
        Ret = [0]*length
    else:
        Ret = [0]*2
    for i in range(length):
        if(SP):
            Ret[i] = [0]*2
        RawArray = TrainArrayInputRaw()
        while(CheckArray(RawArray) == None):
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


def MPTrainArrayIntermediate(length, queue):
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
    process_list = []
    prcs_length = int(length/processes)
    for i in range(processes):
        process_list.append(multiprocessing.Process(target=TrainArray, args=(prcs_length, queue)))#define process
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
#    Model.add(tf.keras.layers.InputLayer(batch_input_shape=(1,1,37), name='input'))
    #Model.add(tf.keras.layers.Dense(36, name='Dense1'))
    Model.add(tf.keras.layers.CuDNNLSTM(50,batch_input_shape=(1,1,37), name='LSTM1', return_sequences=True, stateful=True)) #Stateful = remember what happended last time
    Model.add(tf.keras.layers.Dense(30, name='Interpret'))
    Model.add(tf.keras.layers.Dropout(0.5))
    Model.add(tf.keras.layers.Dense(36, name='output'))
    
    Model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])        #maybe if we decide to use handmade training data for not playing incorrect cards.
    
    tf.global_variables_initializer()      #absolutly necessary! but still not working...?
    return Model


def GetModelBasic():
    '''
    Used for acquiring the RNN Model (using LSTM Cells) with input size (1,1,37) and output size (1/1/36), without an optimizer or other learning oriented aspects.
    
    Returns:
        Uncompiled TensorFlow_Model
    '''
    Model = tf.keras.models.Sequential()
#    Model.add(tf.keras.layers.InputLayer(batch_input_shape=(1,1,37),name='input'))
    Model.add(tf.keras.layers.CuDNNLSTM(50,batch_input_shape=(1,1,37), name='LSTM1', return_sequences=True, stateful=True)) #Stateful = remember what happended last time
    Model.add(tf.keras.layers.Dense(30, name='Interpret'))
    Model.add(tf.keras.layers.Dense(36, name='output'))
    return Model

# =============================================================================
# 
# def GetModelExperimental():
#     '''
#    Just a though, never mind prolly.
#    '''
#     Model = tf.keras.models.Sequential()
# #    Model.add(tf.keras.layers.InputLayer(batch_input_shape=(1,1,37),name='input'))
#     Model.add(tf.lite.nn.TFLiteLSTMCell(50,batch_input_shape=(1,1,37), name='LSTM1', return_sequences=True, stateful=True)) #Stateful = remember what happended last time
#     Model.add(tf.keras.layers.Dense(30, name='Interpret'))
#     Model.add(tf.keras.layers.Dense(36, name='output'))
#     return Model
# =============================================================================



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
    return np.reshape(input, [1,1,37])


def PrepareInputArray(input_array):
    '''
    Converts an array of array (len 37) into an array of matrices (1,1,37), which fits the input requirements of the RNN Model (from GetModel())
    
    
    Parameters:
        input_array(array[array[int]])
    '''
    
    Ret = []
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


def TrainModelBasics(model, size, Multiprocessing = None): #Multiprocessing does not work in Spyder, to make use of this execute from Anaconda using `python JassRNN.py`
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
    if(Multiprocessing == None):
        Multiprocessing = size>5000
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
    x = np.reshape(x,(len(x),1,1,37))
    y = np.reshape(y,(len(y),1,1,36))
    print("Adjusting Network")
    for i in tqdm(range(len(x))):
        model.fit(x[i], y[i], batch_size=1, verbose = 0, use_multiprocessing=False) #*NOTE it works with `use_multiprocessing=True` but I have no idea what it does or whether it helps at all
        if(i%10 == 0):
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
            if(np.random.random() < mutation_factor):
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
    ret.set_weights(A)
    return ret


def TFLite(model,path = None):
    '''
    !!!On Windows use https://colab.research.google.com/drive/1IUIn9ffk5ICKujqPyuGaHL2irQ9Wmtpm#scrollTo=QSLFKa8GfDMr&forceEdit=true&offline=true&sandboxMode=true!!!\n(actually doesn't work either...)\n
    Converts a keras model to a TFLite model and saves it.
    Parameters:
        model (tf.keras.models.Sequential()):
            The model to be converted to a TFLite
        
        path (str):
            the string of where the TFLite should be saved (the tmporary .h5 file will be saved there as well)
    
    Returns:
        None
    '''
    
    if(path == None):
        path = ''
    elif(path[-1:]!='/'):
        path = path + '/'
    keras_file = "tmp_keras_model.h5"
    tf.keras.models.save_model(model, keras_file)
    # Convert to TensorFlow Lite model.
    if(tf.__version__=='1.12.0'):
        converter = tf.contrib.lite.TFLiteConverter.from_keras_model_file(keras_file,allow_custom_ops=True)
    elif(tf.__version__>'1.12.0'):
#           print('test')
        converter = tf.lite.TFLiteConverter.from_keras_model_file(keras_file)
#           print('ought to be here')
        
    else:
        print("Pleas update your Tensorflow version or write your own function/edit this one to convert to TFLite. (JassRNN.py/TFLite(model)  ; line ≈445)")
        remove(keras_file)
        return None
#    converter.target_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]
    tflite_model = converter.convert()
    open("converted_model.tflite", "wb").write(tflite_model)
#    remove(keras_file)
#        print('didnt work huh...\nTFLite conversion, but we already knew it wouldn\'t, work so what gives')
    
    


def TFLiteSess(model,path=None):
    if(path == None):
        path = ''
    elif(path[-1:]!='/'):
        path = path + '/'
    converter = tf.lite.TFLiteConverter.from_session(tf.keras.backend.get_session(),x,y)
    tflite_model = converter.convert()
    open("converted_model.tflite", "wb").write(tflite_model)
    #not working

#fancy copypaste
def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
    """
    This Code is from StackOverflow (https://stackoverflow.com/questions/45466020/how-to-export-keras-h5-to-tensorflow-pb) as posted by jdehesa, posted on Aug 2 2017 at 16:33, last edited May 18 2019 at 12:34
    personal queries: Is it Stateful?, will rewrite if not
    
    
    Freezes the state of a session into a pruned computation graph.

    Creates a new computation graph where variable nodes are replaced by
    constants taking their current value in the session. The new graph will be
    pruned so subgraphs that are not necessary to compute the requested
    outputs are removed.
    @param session The TensorFlow session to be frozen.
    @param keep_var_names A list of variable names that should not be frozen,
                          or None to freeze all the variables in the graph.
    @param output_names Names of the relevant graph outputs.
    @param clear_devices Remove the device directives from the graph for better portability.
    @return The frozen graph definition.
    """
#    from tensorflow.python.framework.graph_util import convert_variables_to_constants
    graph = session.graph
    with graph.as_default():
        freeze_var_names = list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
        output_names = output_names or []
        output_names += [v.op.name for v in tf.global_variables()]
        # Graph -> GraphDef ProtoBuf
        input_graph_def = graph.as_graph_def()
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""
        frozen_graph = tf.graph_util.convert_variables_to_constants(session, input_graph_def, output_names, freeze_var_names)
        return frozen_graph

def pb_conversion(model, name='JassRNN', path='FrozenGraph', text = False, timestamp = False):
    '''
    Converts a Keras model to a tensorflow frozengraph and saves it to the harddisk (as a .pb file)
    
    Parameters:
        model (tf.keras.model.Sequential):
            A Keras model, from which the underlying 'Session' will be used to freeze the tensorflow graph.
        
        name (str):
            The name of the Frozengraph file, defaults to 'JassRNN'
        
        path (str):
            Determines the path to which the .pb file is saved.
        
        text (boolean):
            Determines whether the .pb file should be written as text or as binary. Defaults to False -> binary.
    
    Returns:
        None
    '''
#    tmp = model.get_weights()
#    TrainModelBasics(model,1,False)
#    model.set_weights(tmp)
    model.predict(PrepareInput(range(37)))
    model.reset_states()
#    print('gothere')
    frozen_graph = freeze_session(tf.keras.backend.get_session())
    tf.train.write_graph(frozen_graph, path, name+".pb", as_text=False)
    tf.train.write_graph(frozen_graph, path, name+"_as_txt.pb", as_text=True)

    
    
    
    if(timestamp):
        tf.train.write_graph(frozen_graph, path, name +' ' + str(time()) +'.pb',as_text = False)
        tf.train.write_graph(frozen_graph, path, name +' ' + str(time()) +'_as_txt.pb',as_text = True)
        
    
    TFLite(model)
# =============================================================================
#     print('hellayesfuckmethiswouldbelititwontbethoughcuzwellnevergetthisfarbutamancandreamright')
#         #    testing sum tflite
#     graph_def_file = path+'/'+name+".pb"
#     input_arrays = ["LSTM1"]
#     output_arrays = ["Interpret"]
#     print('0')
#     converter = tf.lite.TFLiteConverter.from_frozen_graph(graph_def_file, input_arrays, output_arrays)
#     print('1')
#     tflite_model = converter.convert()
#     print('2')
#     open("converted_model.tflite", "wb").write(tflite_model)
# =============================================================================

    
#    
#def pb_conversion_(model):
#    sess = tf.keras.backend.get_session()
#    constant_graph = tf.graph_util.convert_variables_to_constants(
#            sess,
#            sess.graph.as_graph_def(),
#            ["output"])
#    tf.train.write_graph(constant_graph, "",
#                         "xxxXXXFancyModelXXXxxx.pb", as_text=False)
#
#
#def pb_conv(model):
#    TrainModelBasics(model,1,False)
#    tf.train.write_graph(tf.keras.backend.get_session().graph,'','xxxXXXFancyModelXXXxxx.pb',as_text = False)

# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
#    old = model.get_weights()
#    new = model.get_weights()
#    SaveRNN(model,'test')
#    LoadRNN(model,'test')
#    
#    print((old[2] == new[2]).any())
#    TFLite(model)
#    pb_conversion(model,'asdfdsaf')
#    pb_conversion(model)
#    print(model.predict(PrepareInput(range(37))))
    print(time())
    #
#    model = GetModelBasic()
    model = GetModelExperimental()
    LoadWeights(model,'best')
    print(model.summary())
    SaveRNN(model,'250519')
    q = LoadRNN(model,'250519')
    print(q.summary())
#    print('n1')
#    TFLiteSess(q)
    pb_conversion(model,name='JassRNN',timestamp=True)
#    print(model.predict(PrepareInput(range(37))))
#    pb_conv(model)
#    pb_conversion_(model)
    
# =============================================================================
#     
#     LocalCards = TrainArray(1)
#     LocalCards0 = PrepareInput(LocalCards[0][0])
#     Cp_callback = CreateCheckpointCallback(5) #callbacks = [Cp_callback], parameter for model.fit
#     Model = GetModel()
#     LoadWeights(Model,"Basic")
#     #n = amount of iterations, but i reckon you guesse :)
#     n = 35
#     for i in range(n):
#         print("Iteration ", i+1,"of ", n)
#         TrainModelBasics(Model, 100000)
#         SaveWeights(Model, "Basic")
# =============================================================================
    
    
    




#What the fuck is this??? Help!?

#runfile('D:/GitHub/Ef-If_Jassen/JassRNN.py', wdir='D:/GitHub/Ef-If_Jassen')
#Reloaded modules: Jassen
#Generating Data
#Adjusting Network
#100%|██████████| 1/1 [00:02<00:00,  2.29s/it]
#INFO:tensorflow:Froze 280 variables.
#INFO:tensorflow:Converted 280 variables to const ops.
#
#runfile('D:/GitHub/Ef-If_Jassen/JassRNN.py', wdir='D:/GitHub/Ef-If_Jassen')
#Reloaded modules: Jassen
#Generating Data
#Adjusting Network
#100%|██████████| 1/1 [00:02<00:00,  2.04s/it]
#INFO:tensorflow:Froze 315 variables.
#INFO:tensorflow:Converted 315 variables to const ops.
#
#runfile('D:/GitHub/Ef-If_Jassen/JassRNN.py', wdir='D:/GitHub/Ef-If_Jassen')
#Reloaded modules: Jassen
#Generating Data
#Adjusting Network
#100%|██████████| 1/1 [00:02<00:00,  2.17s/it]
#INFO:tensorflow:Froze 350 variables.
#INFO:tensorflow:Converted 350 variables to const ops.
#
#runfile('D:/GitHub/Ef-If_Jassen/JassRNN.py', wdir='D:/GitHub/Ef-If_Jassen')
#Reloaded modules: Jassen
#Generating Data
#Adjusting Network
#100%|██████████| 1/1 [00:02<00:00,  2.33s/it]
#INFO:tensorflow:Froze 385 variables.
#INFO:tensorflow:Converted 385 variables to const ops.
#
#runfile('D:/GitHub/Ef-If_Jassen/JassRNN.py', wdir='D:/GitHub/Ef-If_Jassen')
#Reloaded modules: Jassen
#Generating Data
#Adjusting Network
#100%|██████████| 1/1 [00:02<00:00,  2.47s/it]
#INFO:tensorflow:Froze 420 variables.
#INFO:tensorflow:Converted 420 variables to const ops.
#
#runfile('D:/GitHub/Ef-If_Jassen/JassRNN.py', wdir='D:/GitHub/Ef-If_Jassen')
#Reloaded modules: Jassen
#Generating Data
#Adjusting Network
#100%|██████████| 1/1 [00:02<00:00,  2.62s/it]
#INFO:tensorflow:Froze 455 variables.
#INFO:tensorflow:Converted 455 variables to const ops.

