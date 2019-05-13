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
        card1.setImageResource(R.drawable.c0);

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
