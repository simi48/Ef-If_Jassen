package org.tensorflow.demo;

import android.content.Intent;
import android.os.Bundle;
import android.app.Activity;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.ImageView;
import org.tensorflow.demo.env.JassFunctions;

public class ValidationActivity extends Activity {

    private static final String TAG = "ValidationActivity";
    private boolean BackBtnAllowed = false;
    private String[] recCards = new String[9];
    private ImageView[] imgViews = new ImageView[9];
    private int[] normCards = new int[37];
    private JassFunctions js = new JassFunctions();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.validation);
        Log.d(TAG, "onCreate: Starting");

        getWindow().setFlags(WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS, WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS);

        Button continueBtn = (Button) findViewById(R.id.btnContinue);
        Button scanAgainBtn = (Button) findViewById(R.id.btnScanAgain);


        for (int i = 0; i < 9; i++){
            //get all nine ImageViews of ValidationActivity
            String cardID = "card" + (i + 1);
            int resID = getResources().getIdentifier(cardID, "id", getPackageName());
            imgViews[i] = (ImageView) findViewById(resID);

            //get all nine recognised imgViews
            recCards[i] = getIntent().getStringExtra(cardID);
        }

        normCards = js.getNormArray(recCards);

        //set values of the nine ImageViews
        int memory = 0;
        for(int a = 0; a < 9; a++){
            for(int b = memory; b < 36; b++){
                if(normCards[b] == 1){
                    String drawableID = "c" + b;
                    int resID = getResources().getIdentifier(drawableID,"drawable", getPackageName());
                    imgViews[a].setImageResource(resID);
                    memory = b + 1;
                    break;
                }
            }
        }


        continueBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d(TAG, "onClick: Clicked continueBtn");

                Intent intent = new Intent(ValidationActivity.this, DetectorActivity.class);
                startActivity(intent);
            }
        });

        scanAgainBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d(TAG, "onClick: Clicked scanAgainBtn");

                Intent intent = new Intent(ValidationActivity.this, DetectorActivity.class);
                startActivity(intent);
            }
        });
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
