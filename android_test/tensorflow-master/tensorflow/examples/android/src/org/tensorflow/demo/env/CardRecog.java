package org.tensorflow.demo.env;

public class CardRecog{ //array which is able to hold 36 cards with names attached to them
    private String CardTitle;
    private float Confidence;

    public CardRecog(){
    }

    public void setCardTitle(String name){
        CardTitle = name;
    }

    public void setConfidence(float confidence){
        Confidence = confidence;
    }

    public String getCardTitle(){
        return CardTitle;
    }

    public float getConfidence(){
        return Confidence;
    }
}
