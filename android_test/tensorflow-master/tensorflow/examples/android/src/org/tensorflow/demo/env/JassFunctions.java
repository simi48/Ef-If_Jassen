package org.tensorflow.demo.env;


import android.util.Log;

import java.util.ArrayList;

import static java.lang.Float.NEGATIVE_INFINITY;
import static java.lang.Integer.MIN_VALUE;

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
                cardType = "Eichel ";
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
        for (int a = 0; a < recCards.length; a++) {
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
        int index = 0;
        for(int i = 0; i < array.length; i++){
            if(array[i] > array[index]){
                index = i;
            }
        }
        return index;
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

    public int[] ArgMaxOrder(int[] array){
        int[] ordered = new int[array.length];
        for (int i = 0; i < array.length; i++) {
            int max = ArgMax(array);
            ordered[i] = max;
            array[max] = MIN_VALUE;
        }
        return ordered;
    }

    public int ArgMaxF(float[] array){
        int index = 0;
        for(int i = 0; i < array.length; i++){
            if(array[i] > array[index]){
                index = i;
            }
        }
        return index;
    }

    public int[] ArgMaxOrderF(float[] array){
        int[] ordered = new int[array.length];
        for (int i = 0; i < array.length; i++) {
            int max = ArgMaxF(array);
            ordered[i] = max;
            array[max] = NEGATIVE_INFINITY;
        }
        return ordered;
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



    //If the AI gets to choose a playstyle this function is all you need
    public Integer ChooseTrump(int[] myCards){

        //checking for wrong card arrays
        if (myCards.length < 36 || myCards.length > 37) {
            Log.d(TAG, "Only standard card arrays of length 36 or 37 are accepted. Please use the correct format.");
            return null;
        }

        ArrayList<Integer> colInput = new ArrayList<>();
        ArrayList<Integer> colOutput = new ArrayList<>();
        ArrayList<Integer> points = new ArrayList<>();
        int[] colours;
        int roses = 0;
        int acorn = 0;
        int bell = 0;
        int shield = 0;
        int ace = 0;
        int checkAce = 8;
        int checkBuur = 5;
        int checkNell = 3;
        int check;
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

        colours = Colours(ArrayListToArray(colInput));

        checkAce = 8;
        //count the amount of cards the player possesses of each colour
        for(int i = 0; i < colours.length; i++){
            check = colours[i];
            switch (check){
                case 0:
                    roses++;
                    break;
                case 1:
                    acorn++;
                    break;
                case 2:
                    bell++;
                    break;
                case 3:
                    shield++;
                    break;
                default:
                    Log.d(TAG, check + " isn't a colour");
                    break;
            }
        }
        colOutput.add(roses);
        colOutput.add(acorn);
        colOutput.add(bell);
        colOutput.add(shield);

        //check for special card combinations
        for(int i = 0; i < 4; i++){
            if(myCards[checkBuur] == 1 && myCards[checkNell] == 1 && myCards[checkAce] == 1){
                ret = i + 2;
                break;
            }
            else if(myCards[checkNell] == 1 && myCards[checkAce] == 1 && (colOutput.get(i) - 2) > 2){
                ret = i + 2;
                break;
            }
            else if(myCards[checkBuur] == 1 && myCards[checkNell] == 1 && ace > 1){
                if(myCards[checkAce] == 1 && (colOutput.get(i) - 3) > 0){
                    ret = i + 2;
                    break;
                }
                else if(myCards[checkAce] == 0 && (colOutput.get(i) - 2) > 0){
                    ret = i + 2;
                    break;
                }
            }
            else if(myCards[checkBuur] == 1 && (colOutput.get(i) - 1) > 2){
                ret = i + 2;
                break;
            }
            else if((colOutput.get(i)) > 4){
                ret = i + 2;
                break;
            }
            checkBuur += 9;
            checkNell += 9;
            checkAce += 9;
        }

        //in case the player has no such special combinations, select the play style with which the player could potentially score the most points
        if(ret == null){
            int[] tmp;
            for(int i = 0; i < 6; i++){
                tmp = CountPoints(myCards);
                points.add(tmp[0]);
            }
            ret = ArgMax(ArrayListToArray(points));
        }
        return ret;
    }

    public int[] CountPoints(int[] cards) {
        int[] ret = new int[(cards[ArgMax(cards)]) + 1];
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
    public int[] FancyMove(int[] playercards, float[] suggestedmoves){
        //array is as long as player currently holds cards.
        int[] bestmoves = new int[36];
        //what the rnn wanted most
        int[] wanted = ArgMaxOrderF((suggestedmoves));
        int iterator = 0;
        int called = -1;
        //called color:

        //double check this
        for (int i = 4; i > 1; i--) {
            if(Count(playercards,i)==1){
                called = Colour(Index(playercards,i));
            }
        }
        //double check this ^

//if colour was given:
        if(called != -1){
            for (int index:wanted) {
                if(LegalMove(playercards,index,called)){
                    bestmoves[iterator] = index;
                    iterator++;
                }
            }
        }
        //if rnn is first player to go:
        else{
            for(int index:wanted){
                if(LegalMove(playercards, index,Colour(index))){
                    bestmoves[iterator] = index;
                    iterator++;
                }
            }
        }
        return bestmoves;
    }

    //Marc gönnt sich krassi Funktione :)
    public int[] ArrayListToArray(ArrayList<Integer> arrayList){

        int[] array = new int[arrayList.size()];

        for (int i = 0; i < arrayList.size(); i++ ) {
            array[i] = arrayList.get(i);
        }

        return array;
    }

    public String CTT(int c_nb) {
        String c_name = "";
        int colour = Colour(c_nb);
        c_nb %= 9;

        switch(colour) {
            case 0:
                c_name += "Rosen ";
                break;
            case 1:
                c_name += "Eichel ";
                break;
            case 2:
                c_name += "Schellen ";
                break;
            case 3:
                c_name += "Schilten ";
                break;
        }

        switch(c_nb) {
            case 0:
                c_name += "6";
                break;
            case 1:
                c_name += "7";
                break;
            case 2:
                c_name += "8";
                break;
            case 3:
                c_name += "9";
                break;
            case 4:
                c_name += "10";
                break;
            case 5:
                c_name += "Under";
                break;
            case 6:
                c_name += "Ober";
                break;
            case 7:
                c_name += "König";
                break;
            case 8:
                c_name += "Ass";
                break;
        }

        return c_name;
    }

    public String[] CsTT(int[] c_nbs) {
        String[] c_names = new String[36];

        for (int i = 0; i < c_nbs.length; i++) {
            c_names[i] = CTT(c_nbs[i]);
        }

        return c_names;
    }

    public CardRecog[] sortCards(CardRecog[] sorted){ //The purpose of this method is to sort the Card array through putting those cards with a higher confidence first

        CardRecog tmp;
        for (int a = 0; a < sorted.length -1; a++){
            for (int b = 0; b < sorted.length -1; b++){
                if (sorted[b + 1].getConfidence() > sorted[b].getConfidence()){
                    tmp = sorted[b];
                    sorted[b] = sorted[b + 1];
                    sorted[b + 1] = tmp;
                }
            }
        }
        return sorted;
    }
}


