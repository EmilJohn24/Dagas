package com.cnil.dagas.services.location.helpers;

import android.util.Log;

import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class LocationUpdateThread extends Thread{
    private static final String LOCATION_URL = "/relief/api/user-location/";
    private static final String TAG = LocationUpdateThread.class.getName();
    private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
    private final String geolocation;

    public LocationUpdateThread(double lat, double lng) {
        this.geolocation = lat + "," + lng;
    }

    public void run() {
            try {
                postLocation();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void postLocation() throws IOException, JSONException {
            JSONObject postLocationRequestJSON = new JSONObject();
            try {
                postLocationRequestJSON.put("geolocation", geolocation);

            } catch (JSONException e) {
                Log.e(TAG, e.getMessage());
            }
            OkHttpSingleton client = OkHttpSingleton.getInstance();
            RequestBody body = RequestBody.create(postLocationRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(LOCATION_URL)
                    .post(body)
                    .build();
            Response response = client.newCall(request).execute();

//            JSONObject transactionJSON = new JSONObject(response.body().string());

    }

    public String getGeolocation() {
        return geolocation;
    }
}
