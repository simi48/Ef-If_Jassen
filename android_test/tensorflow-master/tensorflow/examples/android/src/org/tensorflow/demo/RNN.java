package org.tensorflow.demo;


import android.animation.AnimatorInflater;
import android.animation.AnimatorSet;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;
import org.tensorflow.contrib.android.TensorFlowInferenceInterface;
import android.os.Build.VERSION;
import android.os.Trace;
import android.text.TextUtils;
import android.util.Log;
import java.io.ByteArrayOutputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.DoubleBuffer;
import java.nio.FloatBuffer;
import java.nio.IntBuffer;
import java.nio.LongBuffer;
import java.util.ArrayList;
import java.util.List;
import org.tensorflow.Graph;
import org.tensorflow.Operation;
import org.tensorflow.Session;
import org.tensorflow.Tensor;
import org.tensorflow.TensorFlow;
import org.tensorflow.Tensors;
import org.tensorflow.types.UInt8;
//import android.content.res.AssetManager;
import org.tensorflow.demo.AssetManager;
public class RNN {
    //this crap was for DL4J:

    //cabbages
    //private MultiLayerNetwork model = KerasModelImport.importKerasSequentialModelAndWeights();


    //but here comes the sweet sweet tensorflow epicness we all wanted!
    private static final String INPUT_NAME = "LSTM1";
    private static final String OUTPUT_NAME = "output";
    private static final AssetManager assetManager = new AssetManager();
    private static final String MODEL_FILE = "file:///android_asset/JassRNN.pb";
    private static final int[] INPUT_SHAPE =  {1,1,37};

    //private static final int INPUT_SIZE = 37; //?

    //int numClasses = (int) c.inferenceInterface.graph().operation(OUTPUT_NAME).output(0).shape().size(1); //dont know the point of this...


    private float[][][] outputs = new float[1][1][36];



    private TensorFlowInferenceInterface tensorFlowInferenceInterface = new TensorFlowInferenceInterface(assetManager , MODEL_FILE);
    //tensorFlowInferenceInterface.feed( INPUT_NAME , inputs , 1, 28, 28);
    //tensorFlowInferenceInterface.run( new String[]{ OUTPUT_NAME } );
    //float[] outputs = new float[ 6];
    //tensorFlowInferenceInterface.fetch( OUTPUT_NAME , outputs ) ;

    public float[] Predict(float[][][] LocalPov) {
        // Copy the input data into TensorFlow.
        TensorFlowInferenceInterface.feed(INPUT_NAME, LocalPov, INPUT_SHAPE);

        // Run the inference call.
        TensorFlowInferenceInterface.run(OUTPUT_NAME);

        // Copy the output Tensor back into the output array.
        TensorFlowInferenceInterface.fetch(OUTPUT_NAME, outputs);

        return outputs;
    }
}
