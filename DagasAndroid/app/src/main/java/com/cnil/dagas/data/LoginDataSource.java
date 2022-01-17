package com.cnil.dagas.data;

import android.util.Log;
import android.widget.Toast;

import com.cnil.dagas.data.model.LoggedInUser;
import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.ui.login.LoginActivity;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * Class that handles authentication w/ login credentials and retrieves user information.
 */
public class LoginDataSource {

    private final String TAG = LoginDataSource.class.getName();



    class LoginThread extends Thread{
        private static final String LOGIN_URL = "/api/rest-authlogin/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        private String username, password;
        private boolean loggedIn = false;

        LoggedInUser getLoggedInUser() {
            return loggedInUser;
        }

        LoggedInUser loggedInUser;
        LoginThread(String username, String password){
            this.username = username;
            this.password = password;
        }
        boolean hasLoggedIn(){
            return loggedIn;
        }

        public void run(){
            try {
                loggedInUser = serverLogin(this.username, this.password);
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }

            loggedIn = true;
        }

        private LoggedInUser serverLogin(String username, String password) throws IOException, JSONException {
            JSONObject loginJSON = new JSONObject();
            // JSON Form Handling:
            // https://stackoverflow.com/questions/17810044/android-create-json-array-and-json-object
            // https://stackoverflow.com/questions/23456488/how-to-use-okhttp-to-make-a-post-request
            // https://stackoverflow.com/questions/34179922/okhttp-post-body-as-json
            OkHttpSingleton.getInstance().setCredentials(username, password);
            try {
                loginJSON.put("username", username);
                loginJSON.put("password", password);
            } catch (JSONException e) {
                e.printStackTrace();
            }

            //TODO: Turn client into singleton
            OkHttpSingleton client = OkHttpSingleton.getInstance();
            RequestBody body = RequestBody.create(loginJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(LOGIN_URL)
                    .post(body)
                    .build();
            Response response = client.newCall(request).execute();
            JSONObject responseJSON = new JSONObject(response.body().string());
            //TODO: Handle login failure
            String token = responseJSON.get("key").toString();
            Log.i(TAG, token);
            return new LoggedInUser(token, username);
        }
    }
    public Result<LoggedInUser> login(String username, String password) {

        try {
            // TODO: handle loggedInUser authentication
            LoginThread loginThread = new LoginThread(username, password);
            loginThread.start();
            loginThread.join();
//            LoggedInUser fakeUser =
//                    new LoggedInUser(
//                            java.util.UUID.randomUUID().toString(),
//                            "Jane Doe");

            return new Result.Success<>(loginThread.loggedInUser);
        } catch (Exception e) {
            return new Result.Error(new IOException("Error logging in", e));
        }
    }

    public void logout() {
        // TODO: revoke authentication
    }
}