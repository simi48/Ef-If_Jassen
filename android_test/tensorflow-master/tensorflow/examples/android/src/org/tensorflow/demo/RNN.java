package org.tensorflow.demo;

import android.content.Context;
import android.support.test.InstrumentationRegistry;
import android.support.test.runner.AndroidJUnit4;

import org.junit.Test;
import org.junit.runner.RunWith;

import static org.junit.Assert.*;

public class RNN {
    String rnn_ = new ClassPathResource("JassRNN.h5").getFile().getPath();
    MultiLayerNetwork model = KerasModelImport.importKerasSequentialModelAndWeights(rnn_);
}


