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

import numpy as np

np.set_printoptions(linewidth=np.inf)

def ChooseTrump(Cards, StartingPlayer):
    '''
    ChooseTrump allows the AI to choose the best possible playstyle (At least I hope so, it's not like I'm a pro at Jass)
    depending on the cards in their possesion.
    
    Parameters:
        Cards (array[int]):
            An array with the standard 36-cards layout.

        StartingPlayer(int):
            Defines which player gets to select the playstyle.
            
    Returns:
        Trump(int):
            The suggested playstyle for the next round.
    '''
    
    #checking for wrong Cardarrays
    if(len(Cards) > 37 or len(Cards) < 36):
        print("Only standard Cardarrays of length 36 or 37 are accepted. Please use the correct format.")
        return None
    
    #checking for invalid players
    if(StartingPlayer < 0 or StartingPlayer > 3):
        print("There can only be four players starting with player 0 and ending with player 3. Please reconsider the starting player")
        return None
    
    myCards = LocalPov(Cards, StartingPlayer)
    colInput = []
    colOutput = []
    points = []
    roses = 0
    acorn = 0
    bell = 0
    shield = 0
    ace = 0
    checkAce = 8
# =============================================================================
#     six = 0
#     checkSix = 0
#     buur = 0
#     checkBuur = 5
#     nell = 0
#     checkNell = 3
# =============================================================================
    ret = None
    
    for i in range(36): #prepare Input for Colour()
        if(myCards[i] == 1):
            colInput.append(i)
        if(i == checkAce):
            if(myCards[i] == 1): #count special cards
                ace += 1
                checkAce += 9
# ============================================================================= in case further precision for the playstyle selection is needed
#         elif(i == checkSix): 
#             if(myCards[i] == 1):
#                 six += 1
#                 checkSix += 9
#         elif(i == checkNell):
#             if(myCards[i] == 1):
#                 nell += 1
#                 checkNell += 9
#         elif(i == checkBuur):
#             if(myCards[i] == 1):
#                 buur += 1
#                 checkBuur += 9
# =============================================================================
                
    colours = Colour(colInput)
    
    checkBuur = 5
    checkNell = 3
    checkAce = 8
    for b in range(len(colours)): #Count how many cards of each colour the player has
        if(colours[b] == 0):
            roses += 1
        elif(colours[b] == 1):
            acorn += 1
        elif(colours[b] == 2):
            bell += 1
        elif(colours[b] == 3):
            shield += 1
    colOutput.append(roses)
    colOutput.append(acorn)
    colOutput.append(bell)
    colOutput.append(shield)
    
    for i in range(4): #check for special card combinations
        if((myCards[checkBuur] == 1) and (myCards[checkNell] == 1) and (myCards[checkAce] == 1)):
            ret = i + 2
#            print('1')
            break
        elif((myCards[checkNell] == 1) and (myCards[checkAce] == 1) and ((colOutput[i] - 2) > 2)):
            ret = i + 2
#            print('2')
            break
        elif((myCards[checkBuur] == 1) and (myCards[checkNell] == 1) and (ace > 1) and ((colOutput[i] - 3) > 0)):
            ret = i + 2
#            print('3')
            break
        elif((myCards[checkBuur] == 1) and ((colOutput[i] - 1) > 2)):
            ret = i + 2
#            print('4')
            break
        elif((colOutput[i] > 4)):
            ret = i + 2
#            print('5')
            break
        checkBuur += 9
        checkNell += 9
        checkAce += 9
    
    if(ret == None): #in case the player has no special combinations, select the playstyle whith which the player can get the most points regardless of whether he wins the round
        for i in range(6):
            tmp = CountPoints(Cards, trump = i)
            points.append(tmp[StartingPlayer])
        tmp = np.argmax(points)
        ret = tmp
     
    return ret

def CountPoints(cards, trump=None):
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
    if(len(cards) < 36):
        print("Pls use standard 36 Card layout")
        return ret
    if(trump == None):
        if(len(cards) == 37):
            trump = cards[36]
        else:
            trump = 0
    
    #PlayerCount/ArraySize
    playerCount = 0
    for i in range(len(cards)):
        if(cards[i] < 0):
            print("Players ID cannot be negative")
            return ret
        if(playerCount < cards[i]):
            playerCount = cards[i]
    Ret = [0]*(playerCount + 1)
    
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
    if(trump == 1):
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
    if(trump == 0 or trump == 1):
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
    elif(trump == 2):
        Ret[cards[5]]+=20 #Buur
        Ret[cards[3]]+=14 #Nell
        #Under
        Ret[cards[14]]+=2
        Ret[cards[23]]+=2
        Ret[cards[32]]+=2
    elif(trump == 3):
        Ret[cards[14]]+=20 #Buur
        Ret[cards[12]]+=14 #Nell
        #Under
        Ret[cards[5]]+=2
        Ret[cards[23]]+=2
        Ret[cards[32]]+=2
    elif(trump == 4):
        Ret[cards[23]]+=20 #Buur
        Ret[cards[21]]+=14 #Nell
        #Under
        Ret[cards[14]]+=2
        Ret[cards[5]]+=2
        Ret[cards[32]]+=2
    elif(trump == 5):
        Ret[cards[32]]+=20 #Buur
        Ret[cards[30]]+=14 #Nell
        #Under
        Ret[cards[14]]+=2
        Ret[cards[23]]+=2
        Ret[cards[5]]+=2
    else:
        if(trump < 0 or trump > 5):
            print("well fuck, ought to have chosen a proper trump (note: check the 37th element of the card array if trump was left blank)")
            Ret = []
    return Ret



def LegalMove(playerCards, playedCard, called, trump = 0, player = 0):
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
    
    if(len(playerCards) != 36 and len(playerCards) != 37 and len(playerCards) != 38):
        print("Card array is not comprised of 36 (or 37) cards.")
    elif(len(playerCards) == 37):
        trump = playerCards[36]
    if(playedCard < 0 or playedCard >= len(playerCards)):
        print("played card is outside of card array. May throw error, may give false results.")
    Ret = True
    playedColour = Colour([playedCard])
    playedColour = playedColour[0]
    if(playerCards[playedCard] != player):
        Ret = False
#        print("not in players possession")
    else:
        if(called != None):
            if(playedColour!= called and playedColour != (trump-2)):
                Ret = False
#                print("incorrectColour")
    
    
    return Ret

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
        if(playedCards[i] < 9):
            playedColour.append(0)
        elif(playedCards[i] < 18):
            playedColour.append(1)
        elif(playedCards[i] < 27):
            playedColour.append(2)
        else:
            playedColour.append(3)
    return playedColour

def RoundWinner(playedCards, trump = 0, callingPlayer = None):
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
        
        callingplayer (int):
            Indicates which colour was called for; which player is calling the colour:\n
            if nothing is selected, defaults to index 0 (player 0)
        
    Returns:
        int:
            Index/Player which won the round.
    '''
    warning = False
    for i in range(len(playedCards)):
        if(playedCards[i] > 35 or playedCards[i] < 0):
            warning = True
    if(warning):
        print("Card values are out of bounds, results will not reflect reality")
    playedColour=Colour(playedCards)
    
    Ret = None
    if(callingPlayer == None):
        callingPlayer = playedColour[0]
    else:
        callingPlayer = playedColour[callingPlayer]
    #Check for Trump
    if(playedColour.count(trump-2) != 0):
        trumpCards = []
        #if there is only one trump, EZ win
        if(playedColour.count(trump-2) == 1):
            Ret=playedColour.index(trump-2)
        else:
            #which players have trumpcards
            for i in range(len(playedColour)):
                if(playedColour[i] == trump-2):
                    trumpCards.append(i) #saves which players had trump
                    
            
            #General
            Ret = trumpCards[0]
            for i in range(len(trumpCards)):
                if(playedCards[trumpCards[i]] > Ret):
                    Ret = trumpCards[i]
            #Nell
            for i in range(len(trumpCards)):
                if(playedCards[trumpCards[i]]%9 == 3):
                    Ret=trumpCards[i]
            #Buur
            for i in range(len(trumpCards)):
                if(playedCards[trumpCards[i]]%9 == 5):
                    Ret=trumpCards[i]
    elif(trump == 1):
        #6 Beats all
        if(playedColour.count(callingPlayer) == 1):
            #if only one person played appropriate colour
            Ret = playedColour.index(callingPlayer)
        else:
            colourCards = []
            #which players played appropriate colour
            for i in range(len(playedColour)):
                if(playedColour[i] == callingPlayer):
                    colourCards.append(i)#players which played correct colour
            #If no trump, only general
            Ret = colourCards[0]
            for i in range(len(colourCards)):
                
                if(playedCards[colourCards[i]] < playedCards[Ret]):
                    Ret = colourCards[i]
    else:
        #for when no trump is present and ace wins
        if(playedColour.count(callingPlayer) == 1):
            #if only one person played appropriate colour
            Ret = playedColour.index(callingPlayer)
        else:
            colourCards = []
            #which players played appropriate colour
            for i in range(len(playedColour)):
                if(playedColour[i] == callingPlayer):
                    colourCards.append(i)#players which played correct colour
            #If no trump, only general
            Ret = colourCards[0]
            for i in range(len(colourCards)):
                
                if(playedCards[colourCards[i]] > playedCards[Ret]):
                    Ret = colourCards[i]
    return Ret




def LocalPov(Cards, player = 0):
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
                - 2:	Player 1 plays card
                - 3:	Player 2 plays card
                - 4:	Player 3 plays card
                - 5:	Player has already played card
                - 6:	Player 1 has already played card
                - 7:	Player 2 has already played card
                - 8:	Player 3 has already played card


    '''
    if(len(Cards) != 36 and len(Cards) != 37):
        print("Card array is not equal to 36/37. (len="+str(len(Cards))+")")
    if(player < 0 or player > 3):
        print("Player "+str(player)+" is out of bounds, will not return correct values")
    Ret = [0]*37
    for i in range(36):
        if(Cards[i] == player+4):
            print("Player can see which card he played this turn. pls reconsider! Card["+str(i)+"]"+"\nThis may throw an error down the line")
            Ret[i] = None
        #For cards in hand
        elif(Cards[i] < 4):
            if(Cards[i]%4 == player):
                Ret[i] = 1
        #For Cards being played
        elif(Cards[i] < 8):
            Ret[i]=(Cards[i]-player)%4 + 1
        #For Cards already played
        elif(Cards[i] < 12):
            Ret[i]=(Cards[i]-player)%4 + 5
        else:
            print("Card Value out of bounds: Cards["+str(i)+"]="+str(Cards[i]))
            Ret[i] = None
        #Playstyle / trump
    if(len(Cards) == 37):
        Ret[36] = Cards[36]
    return Ret


def Shuffle(playercount = 4):
    '''
    Shuffles the 36 Cards.
    
    Parameters:
        playercount (int):
            Indicates the amount of players (defaults to 4)
    
    Returns:
        Array[int]:
            An array of standard 36 Card distributed among `playercount` players, in values of range(`playercount`)
    '''
    if(36%playercount != 0):
        print("Not all players have the same amount of cards")
    Ret = []
    for i in range(36):
        Ret.append(i%playercount)
    np.random.shuffle(Ret)
    return Ret





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
    if(SingleCard < 0 or SingleCard > 35):
        Ret = "Card out of range, will display incorrect answer:\n "
    colour = Colour([SingleCard])
    colour = colour[0]
    
    if(colour == 0):
        Ret = Ret + "Rosen"
    elif(colour == 1):
        Ret = Ret + "Eichel"
    elif(colour == 2):
        Ret = Ret + "Schellen"
    elif(colour == 3):
        Ret = Ret + "Schilten"
    if(SingleCard%9 == 0):
        Ret = Ret + " 6"
    elif(SingleCard%9 == 1):
        Ret = Ret + " 7"
    elif(SingleCard%9 == 2):
        Ret = Ret + " 8"
    elif(SingleCard%9 == 3):
        Ret = Ret + " 9"
    elif(SingleCard%9 == 4):
        Ret = Ret + " 10"
    elif(SingleCard%9 == 5):
        Ret = Ret + " Under"
    elif(SingleCard%9 == 6):
        Ret = Ret + " Ober"
    elif(SingleCard%9 == 7):
        Ret = Ret + " König"
    elif(SingleCard%9 == 8):
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


def CsTT36(cardArray, player = 0):
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
    if(len(cardArray) != 36):
        print("Cardarray lenght is not 36; may not accuratly portray cards. len(cardArray) = "+str(len(cardArray)))
    tmp = []
    for i in range(len(cardArray)):
        if(cardArray[i] == player):
            tmp.append(i)
    Ret = CsTT(tmp)
    return Ret

if __name__ == '__main__':
    
# =============================================================================
#     None of the below things are necessary, change as required.
# =============================================================================
    
    print(RoundWinner([10,11,5,4],0))
    testpov = []
    for i in range(36):
        testpov.append(i%12)
    x = LocalPov(testpov)
    print(testpov)
    print(x)
    
    
    tests = Shuffle()
    for i in range(4):
        print(tests.count(i))
