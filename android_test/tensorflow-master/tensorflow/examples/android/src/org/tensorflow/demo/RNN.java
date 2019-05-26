package org.tensorflow.demo;
import org.jblas.DoubleMatrix;
import java.io.*;
public class RNN {

    private float[][][] outputs = new float[1][1][36];

    private SimpleLSTMPropagator lstm;
    private DenseLayer interpret;
    private DenseLayer output;

    public RNN(){
        try{
            lstm = new SimpleLSTMPropagator("android_asset/weights/", 1);

        }
        catch(Exception e){
            System.out.println("Fuck this shit i'm out (also, cant be bothered to write a proper TAG thingy.");
        }


//        String modelFile="DNN.tflite";
//        protected Interpreter tflite;
//        tflite = new Interpreter(loadModelFile(activity));


    }

    public double[] Predict(double[] localpov) {
        DoubleMatrix X = new DoubleMatrix(1,37,localpov);
        try {
            X = lstm.forward_propagate_full(X);
        } catch (IOException e) {
            e.printStackTrace();
        }

        double[] predictions = X.data;
        return predictions;
    }


}
