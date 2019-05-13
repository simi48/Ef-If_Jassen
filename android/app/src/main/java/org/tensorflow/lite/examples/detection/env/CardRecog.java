package org.tensorflow.lite.examples.detection.env;

public class CardRecog{ //array which is able to hold 36 cards with names attached to them
    private String CardTitle;
    private double Confidence;

    public CardRecog(){
    }

    public void setCardTitle(String name){
        CardTitle = name;
    }

    public void setConfidence(int confidence){
        Confidence = confidence;
    }
}
