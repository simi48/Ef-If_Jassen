package org.tensorflow.demo;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import java.util.ArrayList;

public class StartingPlayerActivity extends Activity {

    private boolean BackBtnAllowed = false;
    private ListView startingPlayerView;
    public int startingPlayer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setContentView(R.layout.select_startingplayer);

        startingPlayerView = (ListView) findViewById(R.id.startingPlayerList);
        ArrayList<String> startingPlayerAL = new ArrayList<>();
        startingPlayerAL.add("Neural Network");
        startingPlayerAL.add("Player 1");
        startingPlayerAL.add("Player 2");
        startingPlayerAL.add("Player 3");

        ArrayAdapter startingPlayerAdapter = new ArrayAdapter(this, android.R.layout.simple_list_item_1, startingPlayerAL);
        startingPlayerView.setAdapter(startingPlayerAdapter);

        startingPlayerView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                startingPlayer = i;

                Intent intent;
                if(i == 0){
                    intent = new Intent(StartingPlayerActivity.this, DetectorActivityGame.class);
                }
                else{
                    intent = new Intent(StartingPlayerActivity.this, TrumpActivity.class);
                }
                intent.putExtra("myCardsNorm", getIntent().getIntArrayExtra("myCardsNorm"));
                intent.putExtra("startingPlayer", startingPlayer);

                startActivity(intent);
            }
        });
    }

    //
    //
    //
    //
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

    //
    //
    //
    //
}
