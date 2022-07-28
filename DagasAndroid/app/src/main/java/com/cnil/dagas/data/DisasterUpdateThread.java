package com.cnil.dagas.data;

import android.util.Log;

import com.cnil.dagas.http.OkHttpSingleton;

import java.io.IOException;

import okhttp3.Request;

public class DisasterUpdateThread extends Thread{
    final public static int NONE = -1;
    private final static String CHANGE_DISASTER_URL = "/relief/api/disasters/%d/change_to_disaster/";
    private final static String REMOVE_DISASTER_URL = "/relief/api/disasters/remove_disaster/";
    private int disasterId;

    public DisasterUpdateThread(int disasterId) {
        this.disasterId = disasterId;
    }

    @Override
    public void run(){
        OkHttpSingleton client = OkHttpSingleton.getInstance();
        Request request;
        if (disasterId != NONE) {
//            RequestBody body = RequestBody.create();
            final String changeDisasterUrlDetail = String.format(CHANGE_DISASTER_URL, disasterId);
            Log.i(DisasterUpdateThread.class.getName(), changeDisasterUrlDetail);
            request = client.builderFromBaseUrl(changeDisasterUrlDetail)
                .get()
                .build();
        } else{
            request = client.builderFromBaseUrl(REMOVE_DISASTER_URL)
                    .get()
                    .build();
        }
        try {
            client.newCall(request).execute();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}
