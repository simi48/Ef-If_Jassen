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
//            Log.d(TAG, myCards[i].getCardTitle());
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

    public int ArgMax(int[] array){
        int ret = 0;
        for(i = 0; i < array.length; i++){
            if(array[i] > array[ret]){
                ret = i;
            }
        }
        return ret;
    }

    public int[] CountPoints(int[] cards){
        int[] ret = new int[ArgMax(cards)];
        //check for length inconsistencies, not gonna fix em though
        if(cards.length!=37){
            //            Log.d(TAG, myCards[i].getCardTitle());
            Log.d(TAG,"CountPoints(cards) -> cards.length!=37 cards.length:"+ cards.length);
        }
        //Check for negative numbers
        for(i=0;i<cards.length;i++){
            if(cards[i] < 0){
                Log.d(TAG,"Players CANNOT be negative!");
            }
        }
        //yes, saving a variable that's already there, how ingenious
        int trump = cards[36];
        //fucking arrays #WannaHashtag.pop()ElementsPlsThx

        for(int i=0;0<cards.length-1;i++){
            //Banner
            if(i%9==4){
                ret[cards[i]] += 10;
            }

            //König
            if(i%9==4){
                ret[cards[i]] += 4;
            }

            //Ober
            if(i%9==6){
                ret[cards[i]] += 3;
            }

            //As/6
            if(trump==1){
                if(i%9==0){
                    ret[cards[i]] += 11;
                }
            }
            else{
                if(i%9==8){
                    ret[cards[i]] += 11;
                }
            }

            //8 und under
            //8 first:
            switch(trump){
                case 0:
                    if(i%9==2){
                        ret[cards[i]] += 8;
                    }
                    //and under
                    if(i%9==5){
                        ret[cards[i]] +=2;
            }
                    break;
                case 1:
                    if(i%9==2){
                        ret[cards[i]] += 8;
                    }
                    //and under
                    if(i%9==5) {
                        ret[cards[i]] += 2;
                    }
                    break;
                default:
                    break;


            }


        }

        switch(trump){
            case 3:
                ret[cards[14]]+=20; //Buur
                ret[cards[12]]+=14; //Nell
                //under
                ret[cards[5]]+=2;
                ret[cards[23]]+=2;
                ret[cards[32]]+=2;
                break;
            case 4:
                ret[cards[23]]+=20; //Buur
                ret[cards[21]]+=14; //Nell
        //Under
                ret[cards[14]]+=2;
                ret[cards[5]]+=2;
                ret[cards[32]]+=2;
                break;
            case 5:
                ret[cards[32]]+=20;// #Buur
                ret[cards[30]]+=14;// #Nell
//        #Under
                ret[cards[14]]+=2;
                ret[cards[23]]+=2;
                ret[cards[5]]+=2;
                break;
            default:
                break;
        }
        return ret;
    }


    public boolean LegalMove(int[] playercards, int playedcard, int called){
        ret = true;

        return ret;
    }
}


