package com.cnil.dagas.data;

import android.util.Log;

import com.cnil.dagas.data.model.LoggedInUser;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class CurrentUserThread extends Thread {
    static public final int RESIDENT = 1;
    static public final int DONOR = 2;
    static public final int BARANGAY = 3;
    static public final int ADMIN = 4;


    private static final String USER_URL = "/relief/api/users/current_user/";
    private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
    private final static String TAG = CurrentUserThread.class.getName();
    private JSONObject user;

    public JSONObject getUser() {
        return this.user;
    }

    public void run() {
        try {
            user = getCurrentUser();
        } catch (IOException | JSONException e) {
            Log.e(TAG, e.getMessage());
        }

    }

    private JSONObject getCurrentUser() throws IOException, JSONException {
        // JSON Form Handling:
        // https://stackoverflow.com/questions/17810044/android-create-json-array-and-json-object
        // https://stackoverflow.com/questions/23456488/how-to-use-okhttp-to-make-a-post-request
        // https://stackoverflow.com/questions/34179922/okhttp-post-body-as-json
//            OkHttpSingleton.getInstance().setCredentials(username, password);

        //TODO: Turn client into singleton
        OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create();
        Request request = client.builderFromBaseUrl(USER_URL)
                .get()
                .build();
        Response response = client.newCall(request).execute();
        JSONObject responseJSON = new JSONObject(response.body().string());
        //TODO: Handle login failure
//            String token = responseJSON.get("key").toString();
//            Log.i(TAG, token);
        return responseJSON;
    }
}
