package org.tensorflow.demo;
import org.tensorflow.lite.Interpreter;
import java.io.*;
public class RNN {

    private float[][][] outputs = new float[1][1][36];

    private SimpleLSTMPropagator lstm;

    public RNN(){
        try{
            lstm = new SimpleLSTMPropagator("android_asset/weights/", 1);
        }
        catch(Exception e){
            System.out.println("Fuck this shit i'm out (also, cant be bothered to write a proper TAG thingy.");
        }
        String modelFile="DNN.tflite";
        protected Interpreter tflite;
        tflite = new Interpreter(loadModelFile(activity));


    }


}
