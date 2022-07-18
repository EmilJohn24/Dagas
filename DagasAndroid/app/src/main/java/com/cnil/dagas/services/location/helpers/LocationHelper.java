package com.cnil.dagas.services.location.helpers;

import android.annotation.SuppressLint;
import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;

public class LocationHelper {
    private final int REFRESH_TIME = 5000;
    private final int REFRESH_DISTANCE = 0; //meters
    @SuppressLint("MissingPermission")
    public void listenToUserLocation(Context cxt, CustomLocationListener customListener){
        LocationManager locationManager = (LocationManager) cxt.getSystemService(Context.LOCATION_SERVICE);
        LocationListener locationListener = new LocationListener() {
            @Override
            public void onLocationChanged(Location location) {
                customListener.onLocationChanged(location);
            }

            @Override
            public void onStatusChanged(String provider, int status, Bundle extras) {

            }
        };
        locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                (long) REFRESH_TIME,
                (float) REFRESH_DISTANCE,
                locationListener
                );
    }
}
