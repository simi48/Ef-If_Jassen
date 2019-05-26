package org.tensorflow.demo;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;

import org.jblas.*;



public class SimpleLSTMPropagator {

    public DoubleMatrix forwardStep(DoubleMatrix X) {

        // If our input is shorter then defined by architecture (15),
        // let's add some zero vectors to it to allow adequate matrix multiplication
        if (this.layerNum == 0) {
            X = inputFix(X);
        }

        ArrayList<DoubleMatrix> outputs = new ArrayList();

        // Let's define previous cell output and hidden state
        DoubleMatrix h_t_1 = DoubleMatrix.zeros(this.W_i.columns, 1);
        DoubleMatrix C_t_1 = DoubleMatrix.zeros(this.W_i.columns, 1);

        for (int i = 0; i < X.columns; i++) {

            // Weights update for every cell step-by-step.
            // For more details check out: http://deeplearning.net/tutorial/lstm.html
            DoubleMatrix x_t = X.getColumn(i);
            DoubleMatrix W_i_mul_x = this.W_i.transpose().mmul(x_t);
            DoubleMatrix U_i_mul_h_1 = this.U_i.transpose().mmul(h_t_1);
            DoubleMatrix i_t = ActivationFunction.hardSigmoid(W_i_mul_x.addColumnVector(U_i_mul_h_1).addColumnVector(this.b_i));

            DoubleMatrix W_c_mul_x = this.W_c.transpose().mmul(x_t);
            DoubleMatrix U_c_mul_h_1 = this.U_c.transpose().mmul(h_t_1);
            DoubleMatrix C_tilda = ActivationFunction.tanh(W_c_mul_x.addColumnVector(U_c_mul_h_1).addColumnVector(this.b_c));

            DoubleMatrix W_f_mul_x = this.W_f.transpose().mmul(x_t);
            DoubleMatrix U_f_mul_h_1 = this.U_f.transpose().mmul(h_t_1);
            DoubleMatrix f_i = ActivationFunction.hardSigmoid(W_f_mul_x.addColumnVector(U_f_mul_h_1).addColumnVector(this.b_f));

            DoubleMatrix C_t = (i_t.mul(C_tilda)).add(f_i.mul(C_t_1));

            DoubleMatrix W_o_mul_x = this.W_o.transpose().mmul(x_t);
            DoubleMatrix U_o_mul_h_1 = this.U_o.transpose().mmul(h_t_1);

            DoubleMatrix o_t = ActivationFunction.hardSigmoid(W_o_mul_x.addColumnVector(U_o_mul_h_1).addColumnVector(this.b_o));
            DoubleMatrix h_t = o_t.mul(ActivationFunction.tanh(C_t));

            outputs.add(h_t);
            h_t_1 = h_t;
            C_t_1 = C_t;

        }

        if (this.returnSequence) {

            // We return out sequence corresponding to our input,
            // which has length of this.realSize.
            // We will restore it in next layer again using fixInput()
            int rows = outputs.get(0).rows;
            DoubleMatrix result = DoubleMatrix.zeros(rows, this.realSize);
            for (int i = 0; i < outputs.size(); i++) {
                for (int j = 0; j < this.realSize; j++) {
                    result.put(i, j, outputs.get(j).get(i));
                }
            }
            return result;

        } else {
            // If we don't want to return sequence of outputs from every cell,
            // but only for the last one (for the last LSTM layer), use this.
            return outputs.get(outputs.size() - 1);
        }

    }



    ///
    public static DoubleMatrix loadMatrixFromFile(String filePath) throws IOException {
        FileInputStream fstream = new FileInputStream(filePath);
        BufferedReader br = new BufferedReader(new InputStreamReader(fstream));
        ArrayList<ArrayList> loadedArrays = new ArrayList();

        String strLine;
        while ((strLine = br.readLine()) != null) {
            ArrayList<Double> row = new ArrayList();
            String[] a = strLine.split(" ");
            for (String s : a) {
                row.add(Double.parseDouble(s));
            }
            loadedArrays.add(row);
        }
        br.close();

        int columns = loadedArrays.get(0).size();
        int rows = loadedArrays.size();
        double[][] target = new double[rows][columns];

        for (int i = 0; i < loadedArrays.size(); i++) {
            for (int j = 0; j < target[i].length; j++) {
                target[i][j] = (Double) loadedArrays.get(i).get(j);
            }
        }
        return new DoubleMatrix(target);
    }





//og
    private ArrayList<AbstractLayer> layers = new ArrayList();

    public SimpleLSTMPropagator(String path, int numLSTMLayers) throws IOException {

        for (int i = 0; i < numLSTMLayers; i++) {
            boolean returnSequence = i == 0;
            layers.add(new LSTMLayer(path, i, returnSequence));
        }
        layers.add(new DenseLayer(path));
    }

    public DoubleMatrix forward_propagate_full(DoubleMatrix X) throws IOException {
        int realSize = X.rows;
        DoubleMatrix intermediateResult = X;
        for (AbstractLayer layer : layers) {
            layer.setRealSize(realSize);
            intermediateResult = layer.forwardStep(intermediateResult);
        }

        return intermediateResult;
    }
}

