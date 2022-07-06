package com.cnil.dagas.http.response_objects;

public class UserLocation {
    private String geolocation;
    public void setGeolocation(float lat, float lng){
        geolocation = lat + "," + lng;
    }
}
