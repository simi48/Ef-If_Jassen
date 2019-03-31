# -*- coding: utf-8 -*-
"""
Project:       Deep Jass

File:           Jassen.py

Purpose:        Assortment of Functions required for playing cards

Functions:
    - CountPoints
    - LegalMove
    - Colour
    - RoundWinner
    - LocalPov
    - CTT (Card to Text)
    - CsTT (Variation of CTT)
    - CsTT36 (Variation of CsTT)



Created on:     11.03.2019 13:41:18
Author:         Simon Thür; Marc Matter

Copyright © 2019 Marc Matter, Michael Siebenmann, Ramon Heeb, Simon Thür. All rights reserved.
"""
#print("______________________________\nJassen.py                Start\n______________________________")


#import tensorflow as tf
import numpy as np

#print(tf.__version__)
np.set_printoptions(linewidth=np.inf)


def CountPoints(cards,trump=None):
    '''Counts points for each player.
    
    Parameters:
        cards (array[int]):
            Card array in standard 36 card layout, each card value signifying to which player it belongs. Value must be >= 0
        trump (int):
            signifying playstyle
            
                - 0=ace
                - 1=6
                - 2=rose
                - 3=acorn
                - 4=bell
                - 5=shield
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
    if(trump == None):
        if(len(cards)==37):
            trump = cards[36]
        else:
            trump = 0
    
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
    elif(trump==2):
        Ret[cards[5]]+=20 #Buur
        Ret[cards[3]]+=14 #Nell
        #Under
        Ret[cards[14]]+=2
        Ret[cards[23]]+=2
        Ret[cards[32]]+=2
    elif(trump==3):
        Ret[cards[14]]+=20 #Buur
        Ret[cards[12]]+=14 #Nell
        #Under
        Ret[cards[5]]+=2
        Ret[cards[23]]+=2
        Ret[cards[32]]+=2
    elif(trump==4):
        Ret[cards[23]]+=20 #Buur
        Ret[cards[21]]+=14 #Nell
        #Under
        Ret[cards[14]]+=2
        Ret[cards[5]]+=2
        Ret[cards[32]]+=2
    elif(trump==5):
        Ret[cards[32]]+=20 #Buur
        Ret[cards[30]]+=14 #Nell
        #Under
        Ret[cards[14]]+=2
        Ret[cards[23]]+=2
        Ret[cards[5]]+=2
    else:
        if(trump<0 or trump>5):
            print("well fuck, ought to have chosen a proper trump (note: check the 37th element of the card array if trump was left blank)")
            Ret=[]
    return Ret


# =============================================================================
# #     To test CountPoints
# testCards = np.random.randint(4,size=37)
# print(testCards)
# testPoints = CountPoints(testCards,2)
# print(testPoints)
# sumPoints = 0
# for i in range(len(testPoints)):
#     sumPoints += testPoints[i]
# print("Sum of Points should equal 152. Currently equals: "+str(sumPoints))
# =============================================================================
    


def LegalMove(playerCards,playedCard,called,trump=0,player=0):
    '''
    Checks whether a played card was playable
    
    Parameters:
        playerCards (array[int]):
            Card array in standard 36 Card layout. Card value
        
        playedCard (int):
            The card that the player wishes to play/has played. It states which card according to the same Card layout used for playerCards.
        
        called (int):
            - Indicates which colour was called for:\n
            - None = nothing called for
            - 0=rose;
            - 1=acorn;
            - 2=bell;
            - 3=shield;
        
        trump (int):
            Indicates which playstyle is in use/which colour is trump (if playerCards has 37 inputs, last element defines trump)(defaults to 0):\n
            - 0=ace;
            - 1=6;
            - 2=rose;
            - 3=acorn;
            - 4=bell;
            - 5=shield;
        
        player (int):
            Signifies which number is the player. if nothing is indicated, player will be `Player 0`, meaning cards with value 0 are players cards
        
    Returns:
        boolean:
            true:
                if played card was playable and correct.
            
            false:
                if played card was not an acceptable choice.
    '''
    
#    print("tmp checkpoint for TESMP.py")
    if(len(playerCards)!=36 and len(playerCards)!=37 and len(playerCards)!=38):
        print("Card array is not comprised of 36 (or 37) cards.")
    elif(len(playerCards)==37):
        trump = playerCards[36]
    if(playedCard<0 or playedCard>=len(playerCards)):
        print("played card is outside of card array. May throw error, may give false results.")
    Ret = True
    playedColour = Colour([playedCard])
    playedColour = playedColour[0]
    if(playerCards[playedCard]!=player):
        Ret = False
#        print("not in players possession")
    else:
        if(called != None):
            if(playedColour!=called and playedColour != trump-2):
                Ret=False
#                print("incorrectColour")
    
    
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


def Colour(playedCards):
    '''
    Identifies which colours the cards in the array have. (values of array represent card)
    
    Arguments:
        playedCards(array[int]):
            An array holding the numbers of cards requested.
    
    Returns:
        Array[int]:
            The Values of the colours of the card at each index:
            
                - 0=rose
                - 1=acorn
                - 2=bell
                - 3=shield
    '''
    playedColour = []
    for i in range(len(playedCards)):
        if(playedCards[i]<9):
            playedColour.append(0)
        elif(playedCards[i]<18):
            playedColour.append(1)
        elif(playedCards[i]<27):
            playedColour.append(2)
        else:
            playedColour.append(3)
    return playedColour

def RoundWinner(playedCards,trump,callingPlayer=None):
    '''
    Calculates which player (array index) has won the round.
    
    Parameters:
        playedCards (array[int]):
            An Array of the cards played in this round (corresponding to the 36 Card layout but only played cards). Each index represents a Player, the value the card. (if card values are outside of standard 36 card values, results will not be correct)
        
        trump (int):
            Indicates which playstyle is in use/which colour is trump:\n
            - 0=ace;
            - 1=6;
            - 2=rose;
            - 3=acorn;
            - 4=bell;
            - 5=shield;
        
        callingplyer (int):
            Indicates which colour was called for; which player is calling the colour:\n
            if nothing is selected, defaults to index 0 (player 0)
        
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
    playedColour=Colour(playedCards)
    
    #print(playedColour)
    Ret=None
    if(callingPlayer==None):
        callingPlayer = playedColour[0]
    else:
        callingPlayer = playedColour[callingPlayer]
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
        if(playedColour.count(callingPlayer)==1):
            #if only one person played appropriate colour
            Ret = playedColour.index(callingPlayer)
        else:
            colourCards=[]
            #which players played appropriate colour
            for i in range(len(playedColour)):
                if(playedColour[i]==callingPlayer):
                    colourCards.append(i)#players which played correct colour
            #If no trump, only general
            Ret = colourCards[0]
            for i in range(len(colourCards)):
                
                if(playedCards[colourCards[i]]<playedCards[Ret]):
                    Ret = colourCards[i]
    else:
        #for when no trump is present and ace wins
        if(playedColour.count(callingPlayer)==1):
            #if only one person played appropriate colour
            Ret = playedColour.index(callingPlayer)
        else:
            colourCards=[]
            #which players played appropriate colour
            for i in range(len(playedColour)):
                if(playedColour[i]==callingPlayer):
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



def LocalPov(Cards, player=0):
    '''
    Transcribes Global Card array to local card array from pov of a player. (used for RNN Input)
    
    Parameters:
        Cards (array[int]):
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
        player (int):
            Indicates the desired perspective
        
    Returns:
        array[int]:
            36 Card pov layout for player:
            
                - 0:	Card location not known
                - 1:	player holds card
                - 2:	Player 1 holds card
                - 3:	Player 2 holds card
                - 4:	Player 3 holds card
                - 5:	Player has already played card
                - 6:	Player 1 has already played card
                - 7:	Player 2 has already played card
                - 8:	Player 3 has already played card


    '''
    if(len(Cards)!=36 and len(Cards)!=37):
        print("Card array is not equal to 36/37. (len="+str(len(Cards))+")")
    if(player<0 or player>3):
        print("Player "+str(player)+" is out of bounds, will not return correct values")
    Ret = [0]*37
    for i in range(len(Cards)):
        if(Cards[i]==player+4):
            print("Player can see which card he played this turn. pls reconsider! Card["+str(i)+"]"+"\nThis may throw an error down the line")
            Ret[i]=None
        #For cards in hand
        elif(Cards[i]<4):
            if(Cards[i]%4==player):
                Ret[i]=1
        #For Cards being played
        elif(Cards[i]<8):
            Ret[i]=(Cards[i]-player)%4 + 1
        #For Cards already played
        elif(Cards[i]<12):
            Ret[i]=(Cards[i]-player)%4 + 5
        else:
            print("Card Value out of bounds: Cards["+str(i)+"]="+str(Cards[i]))
            Ret[i]=None
        #Playstyle / trump
        if(len(Cards)==37):
            Ret[36]=Cards[36]
    return Ret

# =============================================================================
#       To test LocalPov
# Cards = np.random.randint(12, size=37)
# print(Cards)
# print(LocalPov(Cards,3))
# =============================================================================


def Shuffle(playercount=4):
    '''
    Shuffles the 36 Cards.
    
    Parameters:
        playercount (int):
            Indicates the amount of players (defaults to 4)
    
    Returns:
        Array[int]:
            An array of standard 36 Card distributed among `playercount` players, in values of range(`playercount`)
    '''
    if(36%playercount!=0):
        print("Not all players have the same amount of cards")
    Ret = []
    for i in range(36):
        Ret.append(i%playercount)
    np.random.shuffle(Ret)
    return Ret


# =============================================================================
#       To test Shuffle and the other stuff
# print(Colour([1]))
# print(RoundWinner([5,6,9],0))
# cardArray=Shuffle()
# trump = np.random.randint(6)
# card = np.random.randint(36)
# print("Cards"+str(cardArray))
# print("Points: "+str(CountPoints(cardArray,trump)))
# localCard=LocalPov(cardArray)
# #print(localCard)
# print("Card "+str(card))
# print(LegalMove(cardArray,card,0,trump))
# =============================================================================





#ConvenienceFunctions:

def CTT(SingleCard):
    '''
    Finds card name for a given value
    
    Arguments:
        SingleCard(int):
            Which card one would like in plain text.
    
    Returns:
        str:
            Card given in plain text.
    '''
    Ret = ""
    if(SingleCard<0 or SingleCard>35):
        Ret = "Card out of range, will display incorrect answer:\n "
    colour = Colour([SingleCard])
    colour = colour[0]
    
    if(colour==0):
        Ret = Ret + "Rosen"
    elif(colour==1):
        Ret = Ret + "Eichel"
    elif(colour==2):
        Ret = Ret + "Schellen"
    elif(colour==3):
        Ret = Ret + "Schilten"
    if(SingleCard%9==0):
        Ret = Ret + " 6"
    elif(SingleCard%9==1):
        Ret = Ret + " 7"
    elif(SingleCard%9==2):
        Ret = Ret + " 8"
    elif(SingleCard%9==3):
        Ret = Ret + " 9"
    elif(SingleCard%9==4):
        Ret = Ret + " 10"
    elif(SingleCard%9==5):
        Ret = Ret + " Under"
    elif(SingleCard%9==6):
        Ret = Ret + " Ober"
    elif(SingleCard%9==7):
        Ret = Ret + " König"
    elif(SingleCard%9==8):
        Ret = Ret + " As"

    return Ret


def CsTT(CardArray):
    '''
    Finds card names for each given value
    
    Arguments:
        CardArray (array[int]):
            Values for cards one wishes in plain text.
    
    Returns:
        Array(str):
            Cards given in plain text.
    '''
    
    Ret=[]
    for i in range(len(CardArray)):
        Ret.append(CTT(CardArray[i]))
    return Ret


def CsTT36(cardArray,player=0):
    '''
    Finds Card names for selected Cards
    
    Parameters:
        cardArray (array[int]):
            Standard 36 Card arrangement, int signifying to whom it belongs.
        
        player (int):
            Indicates which players cards one wishes to see.
    
    Returns:
        Array(str):
            Cards of selected person given in plain text.
    '''
    if(len(cardArray)!=36):
        print("Cardarray lenght is not 36; may not accuratly portray cards. len(cardArray) = "+str(len(cardArray)))
    tmp = []
    for i in range(len(cardArray)):
        if(cardArray[i]==player):
            tmp.append(i)
    Ret = CsTT(tmp)
    return Ret


# =============================================================================
# inputarray = Shuffle()
# inputarray.append(0)
# print(inputarray)
# inputarray = LocalPov(inputarray)
# print(inputarray)
# =============================================================================

# =============================================================================
# #      To test CTT and related
# Cards = Shuffle()
# print(Cards)
# print("player 0:\n",CsTT36(Cards,0))
# print("player 1:\n",CsTT36(Cards,1))
# print("player 2:\n",CsTT36(Cards,2))
# print("player 3:\n",CsTT36(Cards,3))
# =============================================================================

#print(Shuffle(9))


#print("______________________________\nJassen.py                  End\n______________________________")