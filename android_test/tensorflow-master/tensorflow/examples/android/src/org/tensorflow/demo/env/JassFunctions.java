package org.tensorflow.demo.env;


import android.util.Log;

import java.util.ArrayList;

public class JassFunctions {

    private static final String TAG = "JassFunctions";

    //fill CardRecog with the names of all 36 cards
    public CardRecog[] fillCardNames() {
        CardRecog myCard;
        CardRecog[] myCards = new CardRecog[36];

        String cardType = "Rosen ";
        for (int i = 0; i < 36; i++) {
            myCard = new CardRecog();
            myCards[i] = myCard;
            if (i == 9) {
                cardType = "Eicheln ";
            }
            if (i == 18) {
                cardType = "Schellen ";
            }
            if (i == 27) {
                cardType = "Schilten ";
            }

            if (i % 9 < 5) {
                myCards[i].setCardTitle(cardType + ((i % 9) + 6));
                myCards[i].setConfidence(0);
            } else if (i % 9 == 5) {
                myCards[i].setCardTitle(cardType + "Under");
                myCards[i].setConfidence(0);
            } else if (i % 9 == 6) {
                myCards[i].setCardTitle(cardType + "Ober");
                myCards[i].setConfidence(0);
            } else if (i % 9 == 7) {
                myCards[i].setCardTitle(cardType + "König");
                myCards[i].setConfidence(0);
            } else if (i % 9 == 8) {
                myCards[i].setCardTitle(cardType + "Ass");
                myCards[i].setConfidence(0);
            }
//            Log.d(TAG, myCards[i].getCardTitle());
        }

        return myCards;
    }

    //convert the Strings of the nine recognised cards into the norm card array (local point of view) used by the RNN
    public int[] getNormArray(String[] recCards) {
        int[] normArray = new int[37];
        CardRecog[] cardsNamed = fillCardNames();

        //36 cards + trump
        for (int i = 0; i < 37; i++) {
            normArray[i] = 0;
        }

        //convert recognised cards into norm array
        for (int a = 0; a < 9; a++) {
            for (int b = 0; b < 36; b++) {
                if (cardsNamed[b].getCardTitle().equals(recCards[a])) {
                    normArray[b] = 1;
                    break;
                }
            }
        }
        return normArray;
    }

    //some sweet array functions
    public int ArgMax(int[] array) {
        int ret = 0;
        for(int i = 0; i < array.length; i++){
            if(array[i] > array[ret]){
                ret = i;
            }
        }
        return ret;
    }

    public int Count(int[] array, int hit) {
        int count = 0;
        for (int num : array) {
            if (num == hit) {
                count++;
            }
        }
        return count;
    }

    public int Index(int[] array, int hit) {
        int index = -1;
        for (int i = array.length - 1; i >= 0; i--) {
            if (array[i] == hit) {
                index = i;
            }
        }
        return index;
    }

    //somenumpyishthing
    public int Evaluate(float[][][] matrix){
        int max = 0;
        for (int i = 0; i<matrix[0][0].length;i++){
            if(matrix[0][0][i]>matrix[0][0][max]){
                max = i;
            }
        }
        return max;
    }


    public int ChooseTrump(int[] myCards) {

        //checking for wrong card arrays
        if (myCards.length < 36 || myCards.length > 37) {
            Log.d(TAG, "Only standard card arrays of length 36 or 37 are accepted. Please use the correct format.");
            return null;
        }

        ArrayList<Integer> colInput = new ArrayList<>();
        ArrayList<Integer> colOutput = new ArrayList<>();
        ArrayList<Integer> points = new ArrayList<>();
        int roses = 0;
        int acorn = 0;
        int bell = 0;
        int shield = 0;
        int ace = 0;
        int checkAce = 8;
        Integer ret = null;
        
        for(int i = 0; i < 36; i++){
            if(myCards[i] == 1){
                colInput.add(i);
            }
            if(i == checkAce && myCards[i] == 1){
                ace++;
                checkAce += 9;
            }
        }


        return ret;
    }

    public int[] CountPoints(int[] cards) {
        int[] ret = new int[ArgMax(cards)];
        //check for length inconsistencies, not gonna fix em though
        if(cards.length != 37){
            //            Log.d(TAG, myCards[i].getCardTitle());
            Log.d(TAG, "CountPoints(cards) -> cards.length!=37 cards.length:" + cards.length);
        }
        //Check for negative numbers
        for (int card : cards) {
            if (card < 0) {
                Log.d(TAG, "Players CANNOT be negative!");
            }
        }
        //yes, saving a variable that's already there, how ingenious
        int trump = cards[36];
        //fucking arrays #WannaHashtag.pop()ElementsPlsThx

        for (int i = 0; i < cards.length - 1; i++) {
            //Banner
            if (i % 9 == 4) {
                ret[cards[i]] += 10;
            }

            //König
            if (i % 9 == 4) {
                ret[cards[i]] += 4;
            }

            //Ober
            if (i % 9 == 6) {
                ret[cards[i]] += 3;
            }

            //As/6
            if (trump == 1) {
                if (i % 9 == 0) {
                    ret[cards[i]] += 11;
                }
            } else {
                if (i % 9 == 8) {
                    ret[cards[i]] += 11;
                }
            }

            //8 und under
            //8 first:
            switch (trump) {
                case 0:
                    if (i % 9 == 2) {
                        ret[cards[i]] += 8;
                    }
                    //and under
                    if (i % 9 == 5) {
                        ret[cards[i]] += 2;
                    }
                    break;
                case 1:
                    if (i % 9 == 2) {
                        ret[cards[i]] += 8;
                    }
                    //and under
                    if (i % 9 == 5) {
                        ret[cards[i]] += 2;
                    }
                    break;
                default:
                    break;
            }
        }

        switch (trump) {
            case 3:
                ret[cards[14]] += 20; //Buur
                ret[cards[12]] += 14; //Nell
                //under
                ret[cards[5]] += 2;
                ret[cards[23]] += 2;
                ret[cards[32]] += 2;
                break;
            case 4:
                ret[cards[23]] += 20; //Buur
                ret[cards[21]] += 14; //Nell
                //Under
                ret[cards[14]] += 2;
                ret[cards[5]] += 2;
                ret[cards[32]] += 2;
                break;
            case 5:
                ret[cards[32]] += 20;// #Buur
                ret[cards[30]] += 14;// #Nell
//        #Under
                ret[cards[14]] += 2;
                ret[cards[23]] += 2;
                ret[cards[5]] += 2;
                break;
            default:
                break;
        }
        return ret;
    }


    public boolean LegalMove(int[] playercards, int playedcard, int called) {
        boolean ret = true;
        if (playercards.length != 37) {
            Log.d(TAG, "pls use card length 37");
        }
        if(playedcard < 0 || playedcard > 35){
            Log.d(TAG, "PlayedCard was out of bounds");
            ret = false;
        }
        int playedcolour = Colour(playedcard);
        //check for whether player has card
        if (playercards[playedcard] != 1) {
            ret = false;
        }
        //if player has card, is it correct colour?
        else {
            if (playedcolour != called && playedcolour != playercards[36]) {
                //check if player really couldn't play called:
                for (int i = called * 9; i < (called + 1) * 9; i++) {
                    if (playercards[i] == 1) {
                        ret = false;
                    }
                }
            }
        }
        return ret;
    }


    public int Colour(int card) {
        int colour;
        if (card < 9) {
            colour = 0;
        } else if (card < 18) {
            colour = 1;
        } else if (card < 27) {
            colour = 2;
        } else if (card < 36) {
            colour = 3;
        } else {
            Log.d(TAG, "Card it out of range");
            colour = card;
        }
        return colour;
    }

    public int[] Colours(int[] cards) {
        int[] colours = new int[cards.length];
        for (int i = 0; i < cards.length; i++) {
            colours[i] = Colour(cards[i]);
        }
        return colours;
    }


    public int RoundWinner(int[] playedcards, int trump, int callingplayer) {
        for (int card : playedcards) {
            if (card < 0 || card > 35) {
                Log.d(TAG, "Cards are out of range, this might throw some nasty errors in a bit.");
            }
        }
        //basicinfos
        int[] playedcolours = Colours(playedcards);
        int winner;
        int called = Colour(playedcards[callingplayer]);
        //trump?(if true -> there are trumps in this round.
        if (Count(playedcolours, trump - 2) != 0) {
            //there appear to be sum trumps around. only 1?
            if (Count(playedcolours, trump - 2) == 1) {
                winner = Index(playedcolours, trump - 2);
            } else {
                //effectively, when there'a more than one trump around.
                int[] trumpcards = new int[Count(playedcolours, trump - 2)];    //because you cant append, gotta make it the right length...
                //and you need to know which players are still in the race:
                int q = 0; //q is the index to which it is saved (because there is no append, *sigh*)
                for (int i = 0; i < playedcards.length; i++) {
                    if (playedcolours[i] == trump - 2) {
                        trumpcards[q] = i;
                        q++;
                    }
                }//so now we have an array trumpcards within which there are the indexes to the cards in playedcards which are trump
                winner = trumpcards[0]; //not sure why, but I did it in python so I'll assume it was smart.
                //in general, higher number beats lower number:
                for (int index : trumpcards) {
                    if (playedcards[index] > playedcards[winner]) {
                        winner = index;
                    }
                }
                //Nell beats all up til now
                for (int index : trumpcards) {
                    if (playedcards[index] % 9 == 3) {
                        winner = index;
                    }
                }
                //Buuuuuuur lezzgo
                for (int index : trumpcards) {
                    if (playedcards[index] % 9 == 5) {
                        winner = index;
                    }
                }

                //this is the bit if there is no trump.
            }
        } else if (trump == 1) {
            //or rather the bit where 6 beats all:

            //first, only one person played correctly
            if (Count(playedcolours, called) == 1) {
                winner = Index(playedcolours, called);
            }

            int[] correctcolour = new int[Count(playedcolours, called)];    //because you cant append, gotta make it the right length...
            //and you need to know which players are still in the race:
            int q = 0; //q is the index to which it is saved (because there is no append, *sigh*)
            for (int i = 0; i < playedcards.length; i++) {
                if (playedcolours[i] == called) {
                    correctcolour[q] = i;
                    q++;
                }
            }//so now we have an array correctcolour within which there are the indexes to the cards in playedcards which are correct in colour
            winner = correctcolour[0];
            //assuming, worst card is best:
            for (int index : correctcolour) {
                if (playedcolours[index] < playedcolours[winner]) {
                    winner = index;
                }
            }
            //fancy done with 6wins
        } else {
            //no trump present, ace wins the day.
            //first, only one person played correctly
            if (Count(playedcolours, called) == 1) {
                winner = Index(playedcolours, called);
            }

            int[] correctcolour = new int[Count(playedcolours, called)];    //because you cant append, gotta make it the right length...
            //and you need to know which players are still in the race:
            int q = 0; //q is the index to which it is saved (because there is no append, *sigh*)
            for (int i = 0; i < playedcards.length; i++) {
                if (playedcolours[i] == called) {
                    correctcolour[q] = i;
                    q++;
                }
            }//so now we have an array correctcolour within which there are the indexes to the cards in playedcards which are correct in colour
            winner = correctcolour[0];
            //assuming, worst card is best:
            for (int index : correctcolour) {
                if (playedcolours[index] > playedcolours[winner]) {
                    winner = index;
                }
            }


        }

        return winner;
    }
    public int FancyMove(int[] playercards,int suggestedmove){
        if(LegalMove(playercards,suggestedmove,)){
            Log.d(TAG,"haha didnt get this far yet");
        }

        return suggestedmove;
    }

    ////Marc gönnt sich krassi funktione :)
    public int[] ArrayListToArray(ArrayList<Integer> arrayList){


    }
}


