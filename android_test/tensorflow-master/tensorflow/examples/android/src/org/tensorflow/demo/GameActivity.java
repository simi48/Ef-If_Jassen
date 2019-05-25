package org.tensorflow.demo;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;

public class GameActivity extends Activity {

    private static final String TAG = "GameActivity";
    private boolean BackBtnAllowed = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.validation);
        Log.d(TAG, "onCreate: Starting");
    }




    //method which can be used to disable BackButton
    @Override
    public void onBackPressed(){
        if(!BackBtnAllowed){
            //literally do nothing
        }
        else{
            super.onBackPressed();
        }
    }
}
