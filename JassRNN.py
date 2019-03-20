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
import Jassen as js
#from Jassen import *
#Feel free to delete the folowing if it is in any way a hindrance
GlobalCards = js.Shuffle()
GlobalCards.append(0) #playstyle
LocalCards = []
for i in range(4):
    LocalCards.append(js.LocalPov(GlobalCards,i)) #Is in RNN Input format, but needs to be converted to 3d array (only input if len()=37)
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

print(LocalCards0)
Result = sess.run(Model.predict(LocalCards0TF,steps=1))
print(sess.run(Result))
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

print("______________________________\nJassRNN.py                 End\n______________________________")