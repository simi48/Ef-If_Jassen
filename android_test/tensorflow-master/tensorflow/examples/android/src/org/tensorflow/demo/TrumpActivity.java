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

public class TrumpActivity extends Activity {

    private ListView trumpView;
    public int trump;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setContentView(R.layout.select_startingplayer);

        trumpView = (ListView) findViewById(R.id.trumpList);
        ArrayList<String> trumpAL = new ArrayList<>();
        trumpAL.add("Rosen");
        trumpAL.add("Eichel");
        trumpAL.add("Schellen");
        trumpAL.add("Schilten");
        trumpAL.add("Obenabe");
        trumpAL.add("Undenufe");

        TextView trumpText = (TextView) findViewById(R.id.selectTrump);

        ArrayAdapter trumpAdapter = new ArrayAdapter(this, android.R.layout.simple_list_item_1, trumpAL);
        trumpView.setAdapter(trumpAdapter);

        trumpView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                trump = i;

                Intent intent = new Intent(TrumpActivity.this, DetectorActivityGame.class);
                intent.putExtra("myCardsNorm", getIntent().getIntArrayExtra("myCardsNorm"));
                intent.putExtra("trump", trump);

                startActivity(intent);
            }
        });
    }
}
