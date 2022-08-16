package com.cnil.dagas.http;

import okhttp3.Credentials;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;

// TODO: Consider changing to Retrofit (https://square.github.io/retrofit/)
public class OkHttpSingleton extends OkHttpClient {
    private final String BASE_URL = "http://192.168.1.87:8000";
    private String credentials;
    public final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    public String getBaseUrl() {
        return BASE_URL;
    }

    public void setCredentials(String username, String password){
        this.credentials = Credentials.basic(username, password);
    }

    public void logout(){
        this.credentials = null;
    }
    private static class LazyHolder{
        private static final OkHttpSingleton client = new OkHttpSingleton();
    }

    public static OkHttpSingleton getInstance(){
        return LazyHolder.client;
    }

    public Request.Builder builderFromBaseUrlAnon(String subURL){
        return new Request.Builder().url(BASE_URL + subURL);
    }
    public Request.Builder builderFromBaseUrl(String subURL){
        return new Request.Builder().url(BASE_URL + subURL).header("Authorization", credentials);
    }

    public Request.Builder builderFromFullUrl(String URL){
        return new Request.Builder().url(URL).header("Authorization", credentials);
    }


}
