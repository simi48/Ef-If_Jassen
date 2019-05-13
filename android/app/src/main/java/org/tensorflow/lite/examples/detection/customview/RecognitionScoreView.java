/* Copyright 2019 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

package org.tensorflow.lite.examples.detection.customview;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.util.Log;
import android.util.TypedValue;
import android.view.View;

import java.util.ArrayList;
import java.util.List;
import org.tensorflow.lite.examples.detection.tflite.Classifier.Recognition;


public class RecognitionScoreView extends View implements ResultsView {

//  public class CardRecog{ //array which is able to hold 36 cards with names attached to them
//    String CardTitle;
//    double Confidence;
//  }

  private static final float TEXT_SIZE_DIP = 14;
  private final float textSizePx;
  private final Paint fgPaint;
  private final Paint bgPaint;
  private List<Recognition> results;
//  private CardRecog[] tmpCards = new CardRecog[36];
//  public CardRecog[] myCards = fillCardNames(tmpCards);
//
//
//  public CardRecog[] fillCardNames(CardRecog[] myCards){ //fill CardRecog with the names of the cards
//    String cardType = "Rosen ";
//    for(int i = 0; i < 36; i++){
//      if(i == 9){
//        cardType = "Eicheln ";
//      }
//      if(i == 18){
//        cardType = "Schellen ";
//      }
//      if(i == 27){
//        cardType = "Schilten ";
//      }
//
//      if(i % 9 < 6) {
//        myCards[i].CardTitle = cardType + Integer.toString(i + 6);
//        myCards[i].Confidence = 0;
//      }
//      else if(i % 9 == 6){
//        myCards[i].CardTitle = cardType + "Under";
//        myCards[i].Confidence = 0;
//      }
//      else if(i % 9 == 7){
//        myCards[i].CardTitle = cardType + "Ober";
//        myCards[i].Confidence = 0;
//      }
//      else if(i % 9 == 8){
//        myCards[i].CardTitle = cardType + "König";
//        myCards[i].Confidence = 0;
//      }
//      else if(i % 9 == 0){
//        myCards[i].CardTitle = cardType + "Ass";
//        myCards[i].Confidence = 0;
//      }
//    }
//
//    return myCards;
//  }


  public RecognitionScoreView(final Context context, final AttributeSet set) {
    super(context, set);

    textSizePx =
        TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP, TEXT_SIZE_DIP, getResources().getDisplayMetrics());
    fgPaint = new Paint();
    fgPaint.setTextSize(textSizePx);

    bgPaint = new Paint();
    bgPaint.setColor(0xcc4285f4);
  }

  @Override
  public void setResults(final List<Recognition> results) {
    this.results = results;
    postInvalidate();
  }

  @Override
  public void onDraw(final Canvas canvas) {
    final int x = 10;
    int y = (int) (fgPaint.getTextSize() * 1.5f);

    canvas.drawPaint(bgPaint);

    if (results != null) {
      for (final Recognition recog : results) {
        canvas.drawText(recog.getTitle() + ": " + recog.getConfidence(), x, y, fgPaint);
        y += (int) (fgPaint.getTextSize() * 1.5f);

//        for (int i = 0; i < 36; i++){ //write Confidence of each recognised card into the card array
//          if(myCards[i].CardTitle.equals(recog.getTitle())){
//            if(myCards[i].Confidence < recog.getConfidence()){
//              myCards[i].Confidence = recog.getConfidence();
//            }
//          }
//        }
      }
    }
  }
}
