package com.cnil.dagas.http;

import okhttp3.Credentials;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;

public class OkHttpSingleton extends OkHttpClient {
    private final String BASE_URL = "http://192.168.100.2:8000";
    private String credentials;
    public final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    public void setCredentials(String username, String password){
        this.credentials = Credentials.basic(username, password);
    }
    private static class LazyHolder{
        private static final OkHttpSingleton client = new OkHttpSingleton();
    }

    public static OkHttpSingleton getInstance(){
        return LazyHolder.client;
    }

    public Request.Builder builderFromBaseUrl(String subURL){
        return new Request.Builder().url(BASE_URL + subURL).header("Authorization", credentials);
    }


}
