package com.cnil.dagas.data;

import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;

import java.io.IOException;

import okhttp3.Request;
import okhttp3.Response;

public class DisasterListThread extends Thread{
    private static final String DISASTER_LIST_URL = "/relief/api/disasters/";
    private JSONArray disasterListJSONArray;
    @Override
    public void run(){
        OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create();
        Request request = client.builderFromBaseUrl(DISASTER_LIST_URL)
                .get()
                .build();
        try {
            Response response = client.newCall(request).execute();
            disasterListJSONArray = new JSONArray(response.body().string());
        } catch (JSONException | IOException e) {
            e.printStackTrace();
        }
    }

    public JSONArray getDisasterJSONArray() {
        return this.disasterListJSONArray;
    }
}
