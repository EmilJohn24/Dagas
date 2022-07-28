package com.cnil.dagas.services.notifications.helpers;

import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;

import java.io.IOException;

import okhttp3.Request;
import okhttp3.Response;

public class DagasNotificationRequestThread extends Thread{
    private static final String UNREAD_NOTIF_URL = "/relief/api/notifications/";
    private static final String MARK_ALL_AS_READ_URL = "/relief/api/notifications/mark_all_as_read/";
    private static final String UNREAD_MARK_PARAMS = "?unread=true";
    private int maxNotificationGrabs;
    private JSONArray notificationJSONArray;
    public DagasNotificationRequestThread(int max){
        maxNotificationGrabs = max;
    }


    private String getUnreadURL(){
        return UNREAD_NOTIF_URL + UNREAD_MARK_PARAMS;
    }


    @Override
    public void run() {
        OkHttpSingleton client = OkHttpSingleton.getInstance();
        Request request = client.builderFromBaseUrl(getUnreadURL())
                .get()
                .build();
        Request readAllRequest = client.builderFromBaseUrl(MARK_ALL_AS_READ_URL)
                .get()
                .build();
        try {
            Response response = client.newCall(request).execute();
            client.newCall(readAllRequest).execute();
            notificationJSONArray = new JSONArray(response.body().string());
//            notificationJSONArray = responseJSON.getJSONArray("unread_list");

        } catch (IOException | JSONException e) {
            e.printStackTrace();
        }
    }

    public JSONArray getNotificationJSONArray() {
        return notificationJSONArray;
    }
}
