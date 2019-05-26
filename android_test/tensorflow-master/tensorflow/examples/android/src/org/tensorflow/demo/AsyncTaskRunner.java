package org.tensorflow.demo;

private class AsyncTaskRunner extends AsyncTask<String, Integer, INDArray> {

    // Runs in UI before background thread is called.
    @Override
    protected void onPreExecute() {
        super.onPreExecute();
    }

    @Override
    protected INDArray doInBackground(String... params) {
        // Main background thread, this will load the model and test the input image
        // The dimensions of the images are set here
        int height = 28;
        int width = 28;
        int channels = 1;

        //Now we load the model from the raw folder with a try / catch block
        try {
            // Load the pretrained network.
            InputStream inputStream = getResources().openRawResource(R.raw.trained_mnist_model);
            MultiLayerNetwork model = ModelSerializer.restoreMultiLayerNetwork(inputStream);

            //load the image file to test
            File f = new File(absolutePath, "drawn_image.jpg");

            //Use the nativeImageLoader to convert to numerical matrix
            NativeImageLoader loader = new NativeImageLoader(height, width, channels);

            //put image into INDArray
            INDArray image = loader.asMatrix(f);

            //values need to be scaled
            DataNormalization scalar = new ImagePreProcessingScaler(0, 1);

            //then call that scalar on the image dataset
            scalar.transform(image);

            //pass through neural net and store it in output array
            output = model.output(image);

        } catch (IOException e) {
            e.printStackTrace();
        }
        return output;
    }
}