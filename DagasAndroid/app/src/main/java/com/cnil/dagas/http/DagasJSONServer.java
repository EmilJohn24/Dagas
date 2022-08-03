package com.cnil.dagas.http;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.util.Objects;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class DagasJSONServer {
    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
    private static final OkHttpSingleton client = OkHttpSingleton.getInstance();
    public static String createDetailUrl(String relativeUrl, Object id){
        return relativeUrl + id.toString() + "/";
    }
    public static JSONObject getDetail(String relativeUrl, Object id) throws Exception {
        //TODO: Consider adding params
        String detailUrl = createDetailUrl(relativeUrl, id);
        Request request = client.builderFromBaseUrl(detailUrl)
                .get()
                .build();
        return connectJSON(request);
    }

    public static JSONArray getList(String baseURL) throws Exception {
        Request request = client.builderFromBaseUrl(baseURL)
                .get()
                .build();
        return connectJSONArray(request);
    }

    public static JSONObject post(String baseURL, JSONObject body) throws Exception {
        RequestBody requestBody = RequestBody.create(body.toString(), JSON);
        Request request = client.builderFromBaseUrl(baseURL)
                .post(requestBody)
                .build();
        return connectJSON(request);
    }

    public static void put(String baseURL, JSONObject body) throws Exception {
        RequestBody requestBody = RequestBody.create(body.toString(), JSON);
        Request request = client.builderFromBaseUrl(baseURL)
                .put(requestBody)
                .build();
        connectJSON(request);
    }

    public static void delete(String relativeUrl, Object id) throws Exception {
        String detailUrl = createDetailUrl(relativeUrl, id);
        Request request = client.builderFromBaseUrl(detailUrl)
                .delete()
                .build();
        connectJSON(request);
    }

    public static void uploadWithPut(String relativeUrl, File file) throws Exception {
        RequestBody requestBody = new MultipartBody.Builder().setType(MultipartBody.FORM)
                .addFormDataPart("file", file.getName(),
                        RequestBody.create(file, MediaType.parse("image/*")))
                .addFormDataPart("some-field", "some-value")
                .build();
        Request request = client.builderFromBaseUrl(relativeUrl)
                .put(requestBody)
                .build();
        connectJSON(request);
    }

    public static JSONObject postJSON(String baseURL, JSONObject body) throws Exception {
        RequestBody requestBody = RequestBody.create(body.toString(), JSON);
        Request request = client.builderFromBaseUrl(baseURL)
                .post(requestBody)
                .build();
        return connectJSON(request);
    }

    public static JSONObject connectJSON(Request request) throws Exception {
        final JSONObject[] jsonObject = new JSONObject[1];
        final Response[] connectionResponse = new Response[1];
        final Exception[] connectionException = new Exception[1];
        Thread connectorThread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    connectionResponse[0] = DagasJSONServer.connect(request);
                    jsonObject[0] = new JSONObject(Objects.requireNonNull(
                            connectionResponse[0].body()).string());
                } catch (JSONException | IOException e) {
                    e.printStackTrace();
                    connectionException[0] = e;
                }
            }
        });
        connectorThread.start();
        connectorThread.join();
        if (connectionResponse[0].isSuccessful()) {
            return jsonObject[0];
        } else{
            throw connectionException[0];
        }
    }

    public static JSONArray connectJSONArray(Request request) throws Exception {
        final JSONArray[] jsonArray = new JSONArray[1];
        final Response[] connectionResponse = new Response[1];
        final Exception[] connectionException = new Exception[1];
        Thread connectorThread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    connectionResponse[0] = DagasJSONServer.connect(request);
                    jsonArray[0] = new JSONArray(Objects.requireNonNull(
                            connectionResponse[0].body()).string());
                } catch (JSONException | IOException e) {
                    e.printStackTrace();
                    connectionException[0] = e;
                }
            }
        });
        connectorThread.start();
        connectorThread.join();
        if (connectionResponse[0].isSuccessful()) {
            return jsonArray[0];
        } else{
            throw connectionException[0];
        }    }

    public static Response connect(Request request) throws IOException{
        return client.newCall(request).execute();
    }
}
