# -*- coding: utf-8 -*-
"""
Project:       Deep Jass

File:           Jassen.py

Purpose:        Recurring Neural Network to learn how to play cards.

Created on:     17.03.2019 16:02:49
Author:         Simon Thür; Marc Matter

Copyright © 2019 Marc Matter, Michael Siebenmann, Ramon Heeb, Simon Thür. All rights reserved.
"""
print("______________________________\nJassRNN.py               Start\n______________________________")
import tensorflow as tf
import numpy as np
#from Jassen import *
import Jassen as js


#Feel free to delete the folowing if it is in any way a hindrance
GlobalCards = js.Shuffle()
LocalCards = []
for i in range(4):
    LocalCards.append(js.LocalPov(GlobalCards,i)) #RNN Input format
for i in range(len(LocalCards)):
    print("Player "+str(i)+" "+str(js.CsTT36(LocalCards[i],1))+"\n")

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



print("______________________________\nJassRNN.py                 End\n______________________________")