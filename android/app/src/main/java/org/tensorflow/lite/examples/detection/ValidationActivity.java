package org.tensorflow.lite.examples.detection;

import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.ImageView;

public class ValidationActivity extends AppCompatActivity {

    private static final String TAG = "ValidationActivity";

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.validation);
        Log.d(TAG, "onCreate: Starting");

        getWindow().setFlags(WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS, WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS);

        Button continueBtn = (Button) findViewById(R.id.btnContinue);
        Button scanAgainBtn = (Button) findViewById(R.id.btnScanAgain);

        ImageView card1 = (ImageView) findViewById(R.id.cardOne);
        ImageView card2 = (ImageView) findViewById(R.id.cardTwo);
        ImageView card3 = (ImageView) findViewById(R.id.cardThree);
        ImageView card4 = (ImageView) findViewById(R.id.cardFour);
        ImageView card5 = (ImageView) findViewById(R.id.cardFive);
        ImageView card6 = (ImageView) findViewById(R.id.cardSix);
        ImageView card7 = (ImageView) findViewById(R.id.cardSeven);
        ImageView card8 = (ImageView) findViewById(R.id.cardEight);
        ImageView card9 = (ImageView) findViewById(R.id.cardNine);

        card1.setImageResource(R.drawable.c0);
        card2.setImageResource(R.drawable.c14);
        card3.setImageResource(R.drawable.c6);
        card4.setImageResource(R.drawable.c24);
        card5.setImageResource(R.drawable.c35);
        card6.setImageResource(R.drawable.c16);
        card7.setImageResource(R.drawable.c6);
        card8.setImageResource(R.drawable.c18);
        card9.setImageResource(R.drawable.c21);


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
}
