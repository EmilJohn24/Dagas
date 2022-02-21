package com.cnil.dagas.http;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.Objects;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class DagasJSONServerThread extends Thread{
    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
    private static final OkHttpSingleton client = OkHttpSingleton.getInstance();

    public JSONObject getDetail(String baseURL) throws IOException, JSONException {
        Request request = client.builderFromBaseUrl(baseURL)
                .get()
                .build();
        return this.connectJSON(request);
    }

    public JSONArray getList(String baseURL) throws IOException, JSONException{
        Request request = client.builderFromBaseUrl(baseURL)
                .get()
                .build();
        return this.connectJSONArray(request);
    }

    public Response post(String baseURL, JSONObject body) throws IOException {
        RequestBody requestBody = RequestBody.create(body.toString(), JSON);
        Request request = client.builderFromBaseUrl(baseURL)
                .post(requestBody)
                .build();
        return this.connect(request);
    }

    public Response put(String baseURL, JSONObject body) throws IOException {
        RequestBody requestBody = RequestBody.create(body.toString(), JSON);
        Request request = client.builderFromBaseUrl(baseURL)
                .put(requestBody)
                .build();
        return this.connect(request);
    }

    public JSONObject postJSON(String baseURL, JSONObject body) throws IOException, JSONException {
        RequestBody requestBody = RequestBody.create(body.toString(), JSON);
        Request request = client.builderFromBaseUrl(baseURL)
                .post(requestBody)
                .build();
        return this.connectJSON(request);
    }

    public JSONObject connectJSON(Request request) throws IOException, JSONException {
        return new JSONObject(Objects.requireNonNull(this.connect(request).body()).string());
    }

    public JSONArray connectJSONArray(Request request) throws IOException, JSONException{
        return new JSONArray(Objects.requireNonNull(this.connect(request).body()).string());
    }

    public Response connect(Request request) throws IOException{
        return client.newCall(request).execute();
    }
}
