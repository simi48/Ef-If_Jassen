/*
 * Copyright 2016 The TensorFlow Authors. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.tensorflow.demo;

import android.Manifest;
import android.app.Activity;
import android.app.Fragment;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.hardware.Camera;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.media.Image;
import android.media.Image.Plane;
import android.media.ImageReader;
import android.media.ImageReader.OnImageAvailableListener;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Trace;
import android.util.Log;
import android.util.Size;
import android.view.KeyEvent;
import android.view.Surface;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import org.tensorflow.demo.env.CardRecog;
import org.tensorflow.demo.env.ImageUtils;
import org.tensorflow.demo.env.JassFunctions;
import org.tensorflow.demo.env.Logger;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;

//
//
//
//
//
//
//
//

public abstract class CameraActivityGame extends Activity
    implements OnImageAvailableListener, Camera.PreviewCallback {
  private static final Logger LOGGER = new Logger();

  private static final int PERMISSIONS_REQUEST = 1;

  private static final String PERMISSION_CAMERA = Manifest.permission.CAMERA;
  private static final String PERMISSION_STORAGE = Manifest.permission.WRITE_EXTERNAL_STORAGE;

  private boolean debug = false;

  private Handler handler;
  private HandlerThread handlerThread;
  private boolean useCamera2API;
  private boolean isProcessingFrame = false;
  private byte[][] yuvBytes = new byte[3][];
  private int[] rgbBytes = null;
  private int yRowStride;

  protected int previewWidth = 0;
  protected int previewHeight = 0;

  private Runnable postInferenceCallback;
  private Runnable imageConverter;

  //
  //
  //
  //
  private boolean BackBtnAllowed = false;
  private JassFunctions js = new JassFunctions();
  public boolean canClick = false;
  public Button nextBtn;
  public int startingPlayer;
  public float[] suggestedMoves;
  public String[] recognizedCard = new String[1];
  public int recognizedCardInt;
  private int Stage = 0;
  public int[] myCardsNorm;
  private int[] playedCards = new int[4];
  public int count = 0;
  public CardRecog[] myCards = js.fillCardNames();
  public String[] Memory = {"0", "0", "0", "0", "0", "0", "0", "0", "0","0", "0", "0", "0", "0", "0", "0", "0", "0","0", "0", "0", "0", "0", "0", "0", "0", "0","0", "0", "0", "0", "0", "0", "0", "0", "0"};
  public int MemoryInt = 0;
  public TextView roundView;
  public TextView playerView;
  public TextView recommendedView;
  public TextView trumpView;
  public int activePlayer;
  public int round = 0;
  public int turn = 0;
  public ArrayList<String> cardMemory = new ArrayList<>();
  // input array for RNN
  public int[][][] local_pov = new int[1][1][37];
  public int winner;
  private RNN rnn = new RNN();
  //
  //
  //
  //

  @Override
  protected void onCreate(final Bundle savedInstanceState) {
    LOGGER.d("onCreate " + this);
    super.onCreate(null);
    getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    setContentView(R.layout.activity_camera_game);


    if (hasPermission()) {
      setFragment();
    } else {
      requestPermission();
    }

    //
    //
    //
    //


    //get passed Data
    startingPlayer = getIntent().getIntExtra("startingPlayer", 0);
    myCardsNorm = getIntent().getIntArrayExtra("myCardsNorm");
    
    //add cards to cardMemory which are already in the AI's possession
    int check = 0;
    for(int i = 0; i < 36; i++){
        if(myCardsNorm[i] == 1){
          cardMemory.add(js.CTT(i));
          Memory[check] = js.CTT(i);
//          LOGGER.d("Cardmemory: " + cardMemory.get(check));
          check++;
        }
    }
    MemoryInt = 9;

    //initialize Buttons and Textviews
    nextBtn = (Button) findViewById(R.id.btnNext);
    nextBtn.setTextColor(Color.RED);
    roundView = (TextView) findViewById(R.id.roundView);
    playerView = (TextView) findViewById(R.id.playerView);
    recommendedView = (TextView) findViewById(R.id.recommendedView);
    trumpView = (TextView) findViewById(R.id.trumpView);

    roundView.setText("Round: 0");
    playerView.setText("Player: " + startingPlayer);
    recommendedView.setText("Press Next to start");
    activePlayer = startingPlayer;

    if(activePlayer == 0){
      nextBtn.setTextColor(Color.WHITE);
    }

    //if AI gets to choose Trump
    if(startingPlayer == 0){
        myCardsNorm[36] = js.ChooseTrump(myCardsNorm);
      }

    int tmp = myCardsNorm[36];
    switch(tmp){
      case 0:
        trumpView.setText("Trump: Rosen");
        break;
      case 1:
        trumpView.setText("Trump: Eichel");
        break;
      case 2:
        trumpView.setText("Trump: Schellen");
        break;
      case 3:
        trumpView.setText("Trump: Schilten");
        break;
    }


    nextBtn.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View view) {

        if(canClick && turn < 10 || (startingPlayer + round)%4 == 0){
          canClick = false;
          nextBtn.setTextColor(Color.RED);
          count = 0;

          //get the recognized card from a human (or as I, the AI, like to call them: obsolete machines)
          CardRecog[] sorted = js.sortCards(myCards);
          //check for already recognized cards
          Integer wanted = null;
          boolean quit = false;
          boolean match = false;
          for(int i = 0; i < 36 && !quit; i++){
            for(int b = 0; b < cardMemory.size() && !quit; b++){
              LOGGER.d("YoMyCard: " + sorted[i].getCardTitle());
              LOGGER.d("YoMyCard1: " + cardMemory.get(b));
              if(sorted[i].getCardTitle().equals(cardMemory.get(b))){
                  LOGGER.d("Match found: " + cardMemory.get(b));
                  quit = true;
                  match = true;
              }
            }
            quit = false;
            if(!match){
                wanted = i;
                quit = true; 
            }
            else{
                match = false;
            }
          }
          if(wanted == null){
            Toast.makeText(CameraActivityGame.this, "Sorry, no new card, try again", Toast.LENGTH_SHORT).show();
          }
          else{
            LOGGER.d("mahomies" + sorted[wanted].getCardTitle());
            recognizedCard[0] = sorted[wanted].getCardTitle();
            int[] recognizedCardNorm = js.getNormArray(recognizedCard);
            recognizedCardInt = js.Index(recognizedCardNorm, 1);
            LOGGER.d("mahomies1 " + recognizedCardInt);

            if(round < 4 && turn < 9){
              AdvanceRound();
              round++;

              if(round == 4){
                canClick = true;
                nextBtn.setTextColor(Color.WHITE);
              }

              if((startingPlayer + round)%4 == 0){
                nextBtn.setTextColor(Color.WHITE);
              }
            }
            else if(round == 4 && turn < 9){
              AdvanceTurn();
              round = 0;
              turn++;
              playerView.setText("Player: " + activePlayer);
              recommendedView.setText("Press Next to continue");
            }
            else if(turn == 9){
              for(int i = 0; i < 36; i++){
                myCardsNorm[i] -= 5;
              }
              winner = js.ArgMax(js.CountPoints(myCardsNorm));
              recommendedView.setText("P " + winner + " won (" + js.CountPoints(myCardsNorm)[winner] + " Points)");
              nextBtn.setText("Play Again");
              turn++;
            }
          }

        }
        else if(!canClick){
          Toast.makeText(CameraActivityGame.this, "You have to wait until the AI has succeeded in recognizing a card!", Toast.LENGTH_LONG).show();
        }
        else if(turn == 10){
          Intent intent = new Intent(CameraActivityGame.this, CameraActivity.class);
          startActivity(intent);
        }
        myCards = js.fillCardNames();
      }
    });
  }


  public void AdvanceTurn(){
    //get the winner of the round and thus define new starting player
    startingPlayer = js.RoundWinner(playedCards, myCardsNorm[36], startingPlayer);
    activePlayer = startingPlayer;
    LOGGER.d("the new activePlayer: " + activePlayer);
    if(activePlayer == 0){
      nextBtn.setTextColor(Color.WHITE);
    }

    //update myCardsNorm again because from this moment on, the cards were played in the last round ma Hillaries
    for(int i = 0; i < 36; i++){
      if(myCardsNorm[i] > 1 && myCardsNorm[i] < 5){
        myCardsNorm[i] += 4;
      }
    }

    //making sure the "wrongly" scanned cards can be scanned again
    for(int i = 0; i < 36; i++){
      if(i < cardMemory.size()){
        Memory[i] = cardMemory.get(i);
      }
      else{
        Memory[i] = "0";
      }
    }
    MemoryInt = cardMemory.size();
  }

  public void AdvanceRound(){
    roundView.setText("Round: " + (turn + 1));

    activePlayer = (startingPlayer + round)%4;
    playerView.setText("Player: " + activePlayer);

    //if it's the AI's turn
    if(activePlayer == 0){
      //RNN.EvaluateMoves ma homies! This has priority! Load the RNN!
//      try{
//        double[] feed = new double[myCardsNorm.length];
//        for (int i = 0; i < myCardsNorm.length; i++) {
//          feed[i] = myCardsNorm[i];
//        }
//        double[] tmp = rnn.Predict(feed);
//        for (int i = 0; i < suggestedMoves.length; i++) {
//          suggestedMoves[i] = (float) tmp[i];
//        }
//      } catch (Exception e){
      suggestedMoves = js.RNNEvaluate();
//      }
      //double[] doubles = Arrays.stream(ints).asDoubleStream().toArray();
      //suggestedMoves = RNNOutput; this needs to be changed, it should be whatever the AI recommends #Reality can be whatever I want

      recommendedView.setText("Recommended Move: " + js.CTT(js.FancyMove(myCardsNorm, suggestedMoves)[0]));
      playedCards[round] = js.FancyMove(myCardsNorm, suggestedMoves)[0];

    }
    //if it's the players turn
    else{
      recommendedView.setText("My Observation: " + js.CTT(recognizedCardInt));
      playedCards[round] = recognizedCardInt;
    }

    //update myCardsNorm
    if(activePlayer == 0){
      myCardsNorm[playedCards[round]] = 5;
      cardMemory.add(js.CTT(playedCards[round]));
    }
    else{
      myCardsNorm[playedCards[round]] = activePlayer + 1;
      cardMemory.add(js.CTT(playedCards[round]));
    }

    //making sure the "wrongly" scanned cards can be scanned again
    for(int i = 0; i < 36; i++){
      if(i < cardMemory.size()){
        Memory[i] = cardMemory.get(i);
      }
      else{
        Memory[i] = "0";
      }
    }
    MemoryInt = cardMemory.size();
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

  public void closeApplication(View view) {
    finish();
    moveTaskToBack(true);
  }
  //
  //
  //
  //

  private byte[] lastPreviewFrame;

  protected int[] getRgbBytes() {
    imageConverter.run();
    return rgbBytes;
  }

  protected int getLuminanceStride() {
    return yRowStride;
  }

  protected byte[] getLuminance() {
    return yuvBytes[0];
  }

  /**
   * Callback for android.hardware.Camera API
   */
  @Override
  public void onPreviewFrame(final byte[] bytes, final Camera camera) {
    if (isProcessingFrame) {
      LOGGER.w("Dropping frame!");
      return;
    }

    try {
      // Initialize the storage bitmaps once when the resolution is known.
      if (rgbBytes == null) {
        Camera.Size previewSize = camera.getParameters().getPreviewSize();
        previewHeight = previewSize.height;
        previewWidth = previewSize.width;
        rgbBytes = new int[previewWidth * previewHeight];
        onPreviewSizeChosen(new Size(previewSize.width, previewSize.height), 90);
      }
    } catch (final Exception e) {
      LOGGER.e(e, "Exception!");
      return;
    }

    isProcessingFrame = true;
    lastPreviewFrame = bytes;
    yuvBytes[0] = bytes;
    yRowStride = previewWidth;

    imageConverter =
        new Runnable() {
          @Override
          public void run() {
            ImageUtils.convertYUV420SPToARGB8888(bytes, previewWidth, previewHeight, rgbBytes);
          }
        };

    postInferenceCallback =
        new Runnable() {
          @Override
          public void run() {
            camera.addCallbackBuffer(bytes);
            isProcessingFrame = false;
          }
        };
    processImage();
  }

  /**
   * Callback for Camera2 API
   */
  @Override
  public void onImageAvailable(final ImageReader reader) {
    //We need wait until we have some size from onPreviewSizeChosen
    if (previewWidth == 0 || previewHeight == 0) {
      return;
    }
    if (rgbBytes == null) {
      rgbBytes = new int[previewWidth * previewHeight];
    }
    try {
      final Image image = reader.acquireLatestImage();

      if (image == null) {
        return;
      }

      if (isProcessingFrame) {
        image.close();
        return;
      }
      isProcessingFrame = true;
      Trace.beginSection("imageAvailable");
      final Plane[] planes = image.getPlanes();
      fillBytes(planes, yuvBytes);
      yRowStride = planes[0].getRowStride();
      final int uvRowStride = planes[1].getRowStride();
      final int uvPixelStride = planes[1].getPixelStride();

      imageConverter =
          new Runnable() {
            @Override
            public void run() {
              ImageUtils.convertYUV420ToARGB8888(
                  yuvBytes[0],
                  yuvBytes[1],
                  yuvBytes[2],
                  previewWidth,
                  previewHeight,
                  yRowStride,
                  uvRowStride,
                  uvPixelStride,
                  rgbBytes);
            }
          };

      postInferenceCallback =
          new Runnable() {
            @Override
            public void run() {
              image.close();
              isProcessingFrame = false;
            }
          };

      processImage();
    } catch (final Exception e) {
      LOGGER.e(e, "Exception!");
      Trace.endSection();
      return;
    }
    Trace.endSection();
  }

  @Override
  public synchronized void onStart() {
    LOGGER.d("onStart " + this);
    super.onStart();
  }

  @Override
  public synchronized void onResume() {
    LOGGER.d("onResume " + this);
    super.onResume();

    handlerThread = new HandlerThread("inference");
    handlerThread.start();
    handler = new Handler(handlerThread.getLooper());
  }

  @Override
  public synchronized void onPause() {
    LOGGER.d("onPause " + this);

    if (!isFinishing()) {
      LOGGER.d("Requesting finish");
      finish();
    }

    handlerThread.quitSafely();
    try {
      handlerThread.join();
      handlerThread = null;
      handler = null;
    } catch (final InterruptedException e) {
      LOGGER.e(e, "Exception!");
    }

    super.onPause();
  }

  @Override
  public synchronized void onStop() {
    LOGGER.d("onStop " + this);
    super.onStop();
  }

  @Override
  public synchronized void onDestroy() {
    LOGGER.d("onDestroy " + this);
    super.onDestroy();
  }

  protected synchronized void runInBackground(final Runnable r) {
    if (handler != null) {
      handler.post(r);
    }
  }

  @Override
  public void onRequestPermissionsResult(
      final int requestCode, final String[] permissions, final int[] grantResults) {
    if (requestCode == PERMISSIONS_REQUEST) {
      if (grantResults.length > 0
          && grantResults[0] == PackageManager.PERMISSION_GRANTED
          && grantResults[1] == PackageManager.PERMISSION_GRANTED) {
        setFragment();
      } else {
        requestPermission();
      }
    }
  }

  private boolean hasPermission() {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
      return checkSelfPermission(PERMISSION_CAMERA) == PackageManager.PERMISSION_GRANTED &&
          checkSelfPermission(PERMISSION_STORAGE) == PackageManager.PERMISSION_GRANTED;
    } else {
      return true;
    }
  }

  private void requestPermission() {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
      if (shouldShowRequestPermissionRationale(PERMISSION_CAMERA) ||
          shouldShowRequestPermissionRationale(PERMISSION_STORAGE)) {
        Toast.makeText(CameraActivityGame.this,
            "Camera AND storage permission are required for this demo", Toast.LENGTH_LONG).show();
      }
      requestPermissions(new String[] {PERMISSION_CAMERA, PERMISSION_STORAGE}, PERMISSIONS_REQUEST);
    }
  }

  // Returns true if the device supports the required hardware level, or better.
  private boolean isHardwareLevelSupported(
      CameraCharacteristics characteristics, int requiredLevel) {
    int deviceLevel = characteristics.get(CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL);
    if (deviceLevel == CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_LEGACY) {
      return requiredLevel == deviceLevel;
    }
    // deviceLevel is not LEGACY, can use numerical sort
    return requiredLevel <= deviceLevel;
  }

  private String chooseCamera() {
    final CameraManager manager = (CameraManager) getSystemService(Context.CAMERA_SERVICE);
    try {
      for (final String cameraId : manager.getCameraIdList()) {
        final CameraCharacteristics characteristics = manager.getCameraCharacteristics(cameraId);

        // We don't use a front facing camera in this sample.
        final Integer facing = characteristics.get(CameraCharacteristics.LENS_FACING);
        if (facing != null && facing == CameraCharacteristics.LENS_FACING_FRONT) {
          continue;
        }

        final StreamConfigurationMap map =
            characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);

        if (map == null) {
          continue;
        }

        // Fallback to camera1 API for internal cameras that don't have full support.
        // This should help with legacy situations where using the camera2 API causes
        // distorted or otherwise broken previews.
        useCamera2API = (facing == CameraCharacteristics.LENS_FACING_EXTERNAL)
            || isHardwareLevelSupported(characteristics, 
                                        CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_FULL);
        LOGGER.i("Camera API lv2?: %s", useCamera2API);
        return cameraId;
      }
    } catch (CameraAccessException e) {
      LOGGER.e(e, "Not allowed to access camera");
    }

    return null;
  }

  protected void setFragment() {
    String cameraId = chooseCamera();
    if (cameraId == null) {
      Toast.makeText(this, "No Camera Detected", Toast.LENGTH_SHORT).show();
      finish();
    }

    Fragment fragment;
    if (useCamera2API) {
      CameraConnectionFragment camera2Fragment =
          CameraConnectionFragment.newInstance(
              new CameraConnectionFragment.ConnectionCallback() {
                @Override
                public void onPreviewSizeChosen(final Size size, final int rotation) {
                  previewHeight = size.getHeight();
                  previewWidth = size.getWidth();
                  CameraActivityGame.this.onPreviewSizeChosen(size, rotation);
                }
              },
              this,
              getLayoutId(),
              getDesiredPreviewFrameSize());

      camera2Fragment.setCamera(cameraId);
      fragment = camera2Fragment;
    } else {
      fragment =
          new LegacyCameraConnectionFragment(this, getLayoutId(), getDesiredPreviewFrameSize());
    }

    getFragmentManager()
        .beginTransaction()
        .replace(R.id.container, fragment)
        .commit();
  }

  protected void fillBytes(final Plane[] planes, final byte[][] yuvBytes) {
    // Because of the variable row stride it's not possible to know in
    // advance the actual necessary dimensions of the yuv planes.
    for (int i = 0; i < planes.length; ++i) {
      final ByteBuffer buffer = planes[i].getBuffer();
      if (yuvBytes[i] == null) {
        LOGGER.d("Initializing buffer %d at size %d", i, buffer.capacity());
        yuvBytes[i] = new byte[buffer.capacity()];
      }
      buffer.get(yuvBytes[i]);
    }
  }

  public boolean isDebug() {
    return debug;
  }

  public void requestRender() {
    final OverlayView overlay = (OverlayView) findViewById(R.id.debug_overlay);
    if (overlay != null) {
      overlay.postInvalidate();
    }
  }

  public void addCallback(final OverlayView.DrawCallback callback) {
    final OverlayView overlay = (OverlayView) findViewById(R.id.debug_overlay);
    if (overlay != null) {
      overlay.addCallback(callback);
    }
  }

  public void onSetDebug(final boolean debug) {}

  @Override
  public boolean onKeyDown(final int keyCode, final KeyEvent event) {
    if (keyCode == KeyEvent.KEYCODE_VOLUME_DOWN || keyCode == KeyEvent.KEYCODE_VOLUME_UP
            || keyCode == KeyEvent.KEYCODE_BUTTON_L1 || keyCode == KeyEvent.KEYCODE_DPAD_CENTER) {
      debug = !debug;
      requestRender();
      onSetDebug(debug);
      return true;
    }
    return super.onKeyDown(keyCode, event);
  }

  protected void readyForNextImage() {
    if (postInferenceCallback != null) {
      postInferenceCallback.run();
    }
  }

  protected int getScreenOrientation() {
    switch (getWindowManager().getDefaultDisplay().getRotation()) {
      case Surface.ROTATION_270:
        return 270;
      case Surface.ROTATION_180:
        return 180;
      case Surface.ROTATION_90:
        return 90;
      default:
        return 0;
    }
  }

  protected abstract void processImage();

  protected abstract void onPreviewSizeChosen(final Size size, final int rotation);
  protected abstract int getLayoutId();
  protected abstract Size getDesiredPreviewFrameSize();
}
