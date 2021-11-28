package com.cnil.dagas.http;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class OkHttpSingleton extends OkHttpClient {
    private final String BASE_URL = "http://192.168.31.25:8000";
    public final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    private static class LazyHolder{
        private static final OkHttpSingleton client = new OkHttpSingleton();
    }

    public static OkHttpSingleton getInstance(){
        return LazyHolder.client;
    }

    public Request.Builder builderFromBaseUrl(String subURL){
        return new Request.Builder().url(BASE_URL + subURL);
    }


}
