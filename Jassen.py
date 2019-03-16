# -*- coding: utf-8 -*-
"""
Project:       Deep Jass

File:           Jassen.py
Purpose:        Assortment of Functions required for playing cards

Created on:     11.03.2019 13:41:18
Author:         Simon Thür; Marc Matter

Copyright © 2019
"""

import tensorflow as tf
import numpy as np

#print(tf.__version__)


def CountPoints(cards,trump=0):
    '''Counts points for each player.
    
    Parameters:
        cards (array[int]):
            Card array in standard 36 card layout, each card value signifying to which player it belongs. Value must be >= 0
        trump (int):
            signifying playstyle (0=ace;1=6;2=rose;3=acorn;4=bell;5=shield)
            If value is not provided, defaults to 0

    Returns:
        array[int]:
            points for each player (array position refers to player in ´cards´)
    '''
    #All Cards?
    ret = []
    if(len(cards)<36):
        print("Pls use standard 36 Card layout")
        return ret
    
    #PlayerCount/ArraySize
    playerCount=0
    for i in range(len(cards)):
        if(cards[i]<0):
            print("Players ID cannot be negative")
            return ret
        if(playerCount<cards[i]):
            playerCount=cards[i]
    Ret=[0]*(playerCount+1)
    
    #Banner
    Ret[cards[4]]+=10
    Ret[cards[13]]+=10
    Ret[cards[22]]+=10
    Ret[cards[31]]+=10
    #König
    Ret[cards[7]]+=4
    Ret[cards[16]]+=4
    Ret[cards[25]]+=4
    Ret[cards[34]]+=4
    #Ober
    Ret[cards[6]]+=3
    Ret[cards[15]]+=3
    Ret[cards[24]]+=3
    Ret[cards[33]]+=3
    
    #Ace / 6 ;for trump==1 => 6 is highest
    if(trump==1):
        Ret[cards[0]]+=11
        Ret[cards[9]]+=11
        Ret[cards[18]]+=11
        Ret[cards[27]]+=11
    else:
        Ret[cards[8]]+=11
        Ret[cards[17]]+=11
        Ret[cards[26]]+=11
        Ret[cards[35]]+=11
        
    #where is switch when you need it?
    #8 & Under (+Nell)
    if(trump==0 or trump==1):
        #8
        Ret[cards[2]]+=8
        Ret[cards[11]]+=8
        Ret[cards[20]]+=8
        Ret[cards[29]]+=8
        #Under
        Ret[cards[5]]+=2
        Ret[cards[14]]+=2
        Ret[cards[23]]+=2
        Ret[cards[32]]+=2
    elif(trump==3):
        Ret[cards[5]]+=20 #Buur
        Ret[cards[3]]+=14 #Nell
        #Under
        Ret[cards[14]]+=2
        Ret[cards[23]]+=2
        Ret[cards[32]]+=2
    elif(trump==4):
        Ret[cards[14]]+=20 #Buur
        Ret[cards[12]]+=14 #Nell
        #Under
        Ret[cards[5]]+=2
        Ret[cards[23]]+=2
        Ret[cards[32]]+=2
    elif(trump==5):
        Ret[cards[23]]+=20 #Buur
        Ret[cards[21]]+=14 #Nell
        #Under
        Ret[cards[14]]+=2
        Ret[cards[5]]+=2
        Ret[cards[32]]+=2
    elif(trump==6):
        Ret[cards[32]]+=20 #Buur
        Ret[cards[30]]+=14 #Nell
        #Under
        Ret[cards[14]]+=2
        Ret[cards[23]]+=2
        Ret[cards[5]]+=2
    else:
        print("well fuck, ought to have chosen a proper trump")
        Ret=[]
    return Ret


# =============================================================================
#       To test CountPoints
# testCards = np.random.randint(4,size=36)
# print(testCards)
# testPoints = CountPoints(testCards,5)
# print(testPoints)
# sumPoints = 0
# for i in range(len(testPoints)):
#     sumPoints += testPoints[i]
# print("Sum of Points should equal 152. Currently equals: "+str(sumPoints))
# =============================================================================
    


def LegalMove(playerCards,playedCard,called,trump,player=0):
    '''
    Checks whether a played card was playable
    
    Parameters:
        playerCards (array[int]):
            Card array in standard 36 Card layout. Card value
        
        playedCard (int):
            The card that the player wishes to play/has played. It states which card according to the same Card layout used for playerCards.
        
        called (int):
            Indicates which colour was called for:\n
            0=rose;
            1=acorn;
            2=bell;
            3=shield;
        
        trump (int):
            Indicates which playstyle is in use/which colour is trump:\n
            0=ace;
            1=6;
            2=rose;
            3=acorn;
            4=bell;
            5=shield;
        
        player (int):
            Signifies which number is the player. if nothing is indicated, player will be `Player 0?, meaning cards with value 0 are players cards
        
    Returns:
        boolean:
            true:
                if played card was playable and correct.
            
            false:
                if played card was not an acceptable choice.
    '''
    
    if(len(playerCards)!=36):
        print("Card array is not comprised of 36 cards.")
    if(playedCard<0 or playedCard>=len(playerCards)):
        print("played card is outside of card array. May throw error, may give false results.")
    Ret = True
    playedColour=3
    if(playedCard<9):
        playedColour=0
    elif(playedCard<18):
        playedColour=1
    elif(playedCard<27):
        playedColour=2
    if(playerCards[playedCard]!=player):
        Ret = False
        print("not in players posession")
    else:
        if(playedColour!=called and playedColour != trump-2):
            Ret=False
            print("incorrectColour")
    
    
    return Ret

# =============================================================================
#       To test LegalMove
# playerCards=[]
# for i in range(36):
#     playerCards.append(i&3)
# playedCard = 32
# called =2
# trump=5
# print(playerCards)
# print("playedCard: "+str(playedCard))
# print("called: "+str(called))
# print("trump: "+str(trump))
# print(LegalMove(playerCards,playedCard,called,trump))
# =============================================================================


def RoundWinner(playedCards,trump,called=None):
    '''
    Calculates which player (array index) has won the round.
    
    Parameters:
        playedCards (array[int]):
            An Array of the cards played in this round (corresponding to the 36 Card layout). Each index represents a Player, the value the card. (if card values are outside of standard 36 card values, results will not be correct)
        
        trump (int):
            Indicates which playstyle is in use/which colour is trump:\n
            0=ace;
            1=6;
            2=rose;
            3=acorn;
            4=bell;
            5=shield;
        
        called (int):
            Indicates which colour was called for:\n
            0=rose;
            1=acorn;
            2=bell;
            3=shield;
            \n if nothing is selected, defaults to index 0 (player 0)
        
    Returns:
        int:
            Index/Player which won the round.
    '''
    warning = False
    for i in range(len(playedCards)):
        if(playedCards[i]>35 or playedCards[i]<0):
            warning = True
    if(warning):
        print("Card values are out of bounds, results will not reflect reality")
    playedColour=[]
    for i in range(len(playedCards)):
        if(playedCards[i]<9):
            playedColour.append(0)
        elif(playedCards[i]<18):
            playedColour.append(1)
        elif(playedCards[i]<27):
            playedColour.append(2)
        else:
            playedColour.append(3)
    #print(playedColour)
    Ret=None
    if(called==None):
        called = playedColour[0]
    else:
        called = playedColour[called]
    #Check for Trump
    if(playedColour.count(trump-2)!=0):
        trumpCards=[]
        #if there is only one trump, EZ win
        if(playedColour.count(trump-2)==1):
            Ret=playedColour.index(trump-2)
        else:
            #which players have trumpcards
            for i in range(len(playedColour)):
                if(playedColour[i]==trump-2):
                    trumpCards.append(i) #saves which players had trump
                    
            
            #General
            Ret = trumpCards[0]
            for i in range(len(trumpCards)):
                if(playedCards[trumpCards[i]]>Ret):
                    Ret = trumpCards[i]
            #Nell
            for i in range(len(trumpCards)):
                if(playedCards[trumpCards[i]]%9==3):
                    Ret=trumpCards[i]
            #Buur
            for i in range(len(trumpCards)):
                if(playedCards[trumpCards[i]]%9==5):
                    Ret=trumpCards[i]
    elif(trump==1):
        #6 Beats all
        if(playedColour.count(called)==1):
            #if only one person played appropriate colour
            Ret = playedColour.index(called)
        else:
            colourCards=[]
            #which players played appropriate colour
            for i in range(len(playedColour)):
                if(playedColour[i]==called):
                    colourCards.append(i)#players which played correct colour
            #If no trump, only general
            Ret = colourCards[0]
            for i in range(len(colourCards)):
                
                if(playedCards[colourCards[i]]<playedCards[Ret]):
                    Ret = colourCards[i]
    else:
        #for when no trump is present and ace wins
        if(playedColour.count(called)==1):
            #if only one person played appropriate colour
            Ret = playedColour.index(called)
        else:
            colourCards=[]
            #which players played appropriate colour
            for i in range(len(playedColour)):
                if(playedColour[i]==called):
                    colourCards.append(i)#players which played correct colour
            #If no trump, only general
            Ret = colourCards[0]
            for i in range(len(colourCards)):
                
                if(playedCards[colourCards[i]]>playedCards[Ret]):
                    Ret = colourCards[i]
    return Ret


# =============================================================================
#       To test RoundWinner
# stats=[0,0]
# for i in range(247):
#     playedCards = np.random.randint(36,size=4)
#     trump = np.random.randint(6)
#     called = np.random.randint(4)
#     print("Cards: "+str(playedCards)+"  Trump: "+str(trump)+"  Called: "+str(called))
#     Winner =RoundWinner(playedCards,trump,called)
#     if(called==Winner):
#         stats[0]+=1
#     else:
#         stats[1]+=1
#     print("Winner: "+str(Winner)+"                                                 iteration "+str(i+1))
# print(100/(stats[1]+stats[0])*stats[0])
# print(stats)
# =============================================================================
