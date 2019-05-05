package org.tensorflow.lite.examples.detection;

import android.content.Intent;
import android.nfc.Tag;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

public class MainMenuActivity extends AppCompatActivity {

    private static final String TAG = "MainMenuActivity";

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main_menu);
        Log.d(TAG, "onCreate: Starting");

        //ImageView backImg = (ImageView) findViewById(R.id.backImg);
        Button playBtn = (Button) findViewById(R.id.btnPlay);
        
        //backImg.setImageResource(R.drawable.main_back);

        playBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d(TAG, "onClick: Clicked playBtn");

                Intent intent = new Intent(MainMenuActivity.this, DetectorActivity.class);
                startActivity(intent);
            }
        });
    }
}
