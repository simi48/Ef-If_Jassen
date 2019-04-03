import Jassen as js
import multiprocessing #*NOTE Multiprocessing ?usually? does not work in iPython (Spyder). To use MP, run file through Anaconda: navigate to folder and type: `python JassRNN.py`
import numpy as np
from tqdm import tqdm #using anaconda/pip: pip install tqdm
import time

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

def TrainArray(length, queue = None):
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
    SP=False
    if( queue==None):
        SP=True
    if(SP):
        Ret=[0]*length
    else:
        Ret=[0]*2
    for i in range(length):
#        print((i+1)/length*100,"%")
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
            while(not queue.empty()):
                pass
            queue.put(Ret)
    return Ret

def test(length):
    
    return length


def MPTrainArrayIntermediate(length,queue):
    tmp = test(TrainArray(length))
#    print(tmp)
    queue.put(tmp)


def MPTrainArray(length, base = 50):
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
    if(base>95):
        print("MPTrainArray(length, base) base was greater than 95: ",base,"\nBase was set to 95.")
        base = 95
    processes = multiprocessing.cpu_count()
    queue = multiprocessing.Queue()
    Collect = []
    process_list=[]
    prcs_length = int(length/processes)
    for i in range(processes):
        process_list.append(multiprocessing.Process(target=TrainArray,args=(prcs_length,queue)))#define process
    for prcs in process_list:
        prcs.start() #start processes
    print(prcs_length*processes)
    for _ in tqdm(range(prcs_length*processes)):
        Collect.append(queue.get())
#join processes (terminate them once they're done) 
#apparantly wont close because there is stuff in the queue? problem solved by limiteing queue
    for prcs in process_list:
        prcs.join()
    return Collect


def FindTime():
    '''
    Checks for the size at which Muliprocessing becomes faster than serial processing.
    
    Returns:
        the size (int) at which MP is faster than SP
    '''
    size = multiprocessing.cpu_count()*50
    MP=1
    SP=0
    while(MP>SP):
        size+=multiprocessing.cpu_count()*50
        for i in range(2):
            startsp=time.time()
        tmp = TrainArray(size)
        endsp = time.time()
        SP = endsp-startsp
        startmp = time.time()
        for i in range(2):
            tmp = MPTrainArray(size)
        endmp = time.time()
        MP = endmp-startmp
        print("MP: ",MP)
        print("SP: ",SP)
        print("size:",size)

#    print(tmp)
    return size

if __name__ == '__main__':
#    print(FindTime())
    print(TrainArray(16))
    print("")
    print(MPTrainArray(16))
#    print(TrainArray(10))
#    TESTtrainArray = MPTrainArray(100000)
##    print(TESTtrainArray)
#    print(len(TESTtrainArray))
    
