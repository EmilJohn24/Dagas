package com.cnil.dagas.services.location;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.location.Location;
import android.location.LocationManager;
import android.os.Build;
import android.os.Bundle;
import android.os.IBinder;

import androidx.core.app.NotificationCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.cnil.dagas.R;
import com.cnil.dagas.services.location.helpers.CustomLocationListener;
import com.cnil.dagas.services.location.helpers.LocationHelper;
import com.cnil.dagas.services.location.helpers.LocationUpdateThread;

import java.util.Timer;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

// Based on: https://howtodoandroid.com/continuous-location-updates-android/
public class LocationService extends Service {
    private String NOTIFICATION_CHANNEL_ID = "Dagas_GPS_Notif";
    private String NOTIFICATION_CHANNEL_NAME = "Dagas GPS Notification";
    private Location latestLocation;
    public LocationService() {
    }
    // Thread queueing based on: https://stackoverflow.com/questions/8389585/android-thread-queue
    final static ExecutorService locationUpdateExecutor = Executors.newSingleThreadExecutor();

    @Override
    public void onCreate() {
        super.onCreate();
        //create

        NotificationCompat.Builder notifBuilder = new NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID)
                                                                        .setOngoing(false)
                                                                        .setSmallIcon(R.drawable.ic_dagaslogo_background);
        NotificationManager notifManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        NotificationChannel notifChannel = new NotificationChannel(NOTIFICATION_CHANNEL_ID,
                NOTIFICATION_CHANNEL_NAME,
                NotificationManager.IMPORTANCE_LOW);
        notifChannel.setDescription(NOTIFICATION_CHANNEL_ID);
        notifChannel.setSound(null, null);
        notifManager.createNotificationChannel(notifChannel);
        startForeground(1, notifBuilder.build());
//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O){

//        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Timer timer = new Timer();
        (new LocationHelper()).listenToUserLocation(this, new CustomLocationListener() {
            @Override
            public void onLocationChanged(Location location) {
                LocationUpdateThread locationUpdateThread = new LocationUpdateThread(location.getLatitude(),
                                                                                    location.getLongitude());
                sendMessageToActivity(location, "foo");
                locationUpdateExecutor.execute(locationUpdateThread);
                latestLocation = location;

            }
        });
        return START_STICKY;
        //        return super.onStartCommand(intent, flags, startId);
    }

    private void sendMessageToActivity(Location l, String msg) {
        Intent intent = new Intent("GPSLocationUpdates");
        // You can also include some extra data.
        intent.putExtra("Status", msg);
        Bundle b = new Bundle();
        b.putDouble("latitude", l.getLatitude());
        b.putDouble("longitude", l.getLongitude());
        intent.putExtra("Location", b);
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        // TODO: Return the communication channel to the service.
        throw new UnsupportedOperationException("Not yet implemented");
    }

    public Location getLatestLocation() {
        return latestLocation;
    }
}