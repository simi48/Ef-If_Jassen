package org.tensorflow.demo.env;


import android.util.Log;

public class JassFunctions {

    private static final String TAG = "JassFunctions";

    //fill CardRecog with the names of all 36 cards
    public CardRecog[] fillCardNames(){
        CardRecog myCard;
        CardRecog[] myCards = new CardRecog[36];

        String cardType = "Rosen ";
        for(int i = 0; i < 36; i++){
            myCard = new CardRecog();
            myCards[i] = myCard;
            if(i == 9){
                cardType = "Eicheln ";
            }
            if(i == 18){
                cardType = "Schellen ";
            }
            if(i == 27){
                cardType = "Schilten ";
            }

            if(i % 9 < 5) {
                myCards[i].setCardTitle(cardType + ((i%9) + 6));
                myCards[i].setConfidence(0);
            }
            else if(i % 9 == 5){
                myCards[i].setCardTitle(cardType + "Under");
                myCards[i].setConfidence(0);
            }
            else if(i % 9 == 6){
                myCards[i].setCardTitle(cardType + "Ober");
                myCards[i].setConfidence(0);
            }
            else if(i % 9 == 7){
                myCards[i].setCardTitle(cardType + "König");
                myCards[i].setConfidence(0);
            }
            else if(i % 9 == 8){
                myCards[i].setCardTitle(cardType + "Ass");
                myCards[i].setConfidence(0);
            }
            Log.d(TAG, myCards[i].getCardTitle());
        }

        return myCards;
    }

    //convert the Strings of the nine recognised cards into the norm card array (local point of view) used by the RNN
    public int[] getNormArray(String[] recCards){
        int[] normArray = new int[37];
        CardRecog[] cardsNamed = fillCardNames();

        //36 cards + trump
        for (int i = 0; i < 37; i++){
            normArray[i] = 0;
        }

        //convert recognised cards into norm array
        for (int a = 0; a < 9; a++){
            for (int b = 0; b < 36; b++){
                if(cardsNamed[b].getCardTitle().equals(recCards[a])){
                    normArray[b] = 1;
                    break;
                }
            }
        }
        return normArray;
    }


}
