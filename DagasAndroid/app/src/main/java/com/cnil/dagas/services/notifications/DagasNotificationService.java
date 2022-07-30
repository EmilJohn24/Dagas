package com.cnil.dagas.services.notifications;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.location.Location;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;
import android.os.Process;

import androidx.core.app.NotificationCompat;

import com.cnil.dagas.R;
import com.cnil.dagas.services.notifications.helpers.DagasNotificationRequestThread;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Timer;

public class DagasNotificationService extends Service {
    private String NOTIFICATION_CHANNEL_ID = "Dagas_Notifications";
    private String NOTIFICATION_CHANNEL_NAME = "Dagas Notifications";
    private Handler handler;
    private Looper looper;
    private Location latestLocation;

    // See example here: https://developer.android.com/guide/components/services.html
    // https://stackoverflow.com/questions/40786743/android-push-notification-without-google-service
    // https://medium.com/@ali.muzaffar/handlerthreads-and-why-you-should-be-using-them-in-your-android-apps-dc8bf1540341
    // https://blog.nikitaog.me/2014/10/11/android-looper-handler-handlerthread-i/
    // https://androiderrors.com/how-to-run-a-runnable-thread-in-android-at-defined-intervals/
    @Override
    public void onCreate() {
        super.onCreate();
        //create
//        NotificationCompat.Builder notifBuilder = new NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID)
//                .setOngoing(false)
//                .setSmallIcon(R.drawable.ic_dagaslogo_background);
        NotificationManager notifManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        NotificationChannel notifChannel = new NotificationChannel(NOTIFICATION_CHANNEL_ID,
                NOTIFICATION_CHANNEL_NAME,
                NotificationManager.IMPORTANCE_HIGH);
        notifChannel.setDescription(NOTIFICATION_CHANNEL_ID);
//        notifChannel.setSound(null, null);
        notifManager.createNotificationChannel(notifChannel);

        HandlerThread thread = new HandlerThread("Notifications", Process.THREAD_PRIORITY_BACKGROUND);
        thread.start();
        looper = thread.getLooper();
        handler = new Handler(looper);
//        handler.post(new DagasNotificationRequestThread(3));
//        notifManager.notify()
//        startForeground(1, notifBuilder.build());
//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O){

//        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Timer timer = new Timer();
        NotificationManager notifManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        Runnable notificationThread = new Runnable() {
            @Override
            public void run() {
                DagasNotificationRequestThread thread = new DagasNotificationRequestThread(3);
                thread.start();
                try {
                    thread.join();
                    JSONArray newNotifications = thread.getNotificationJSONArray();
                    if (newNotifications != null) {
                        for (int notifIndex = 0; notifIndex != newNotifications.length(); notifIndex++) {
                            JSONObject notifJSONObject = newNotifications.getJSONObject(notifIndex);
                            NotificationCompat.Builder notifBuilder =
                                    new NotificationCompat.Builder(DagasNotificationService.this, NOTIFICATION_CHANNEL_ID)
                                            .setOngoing(false)
                                            .setSmallIcon(R.drawable.ic_dagaslogo_background)
                                            .setContentTitle("Dagas")
                                            .setContentText(notifJSONObject.getString("verb"));
                            notifManager.notify(2, notifBuilder.build());
                        }
                    }
                } catch (InterruptedException | JSONException e) {
                    e.printStackTrace();
                } finally{
                    handler.postDelayed(this, 100000);
                }
            }
        };
        handler.post(notificationThread);
        return START_STICKY;
        //        return super.onStartCommand(intent, flags, startId);
    }
    public DagasNotificationService() {
    }

    @Override
    public IBinder onBind(Intent intent) {
        // TODO: Return the communication channel to the service.
        throw new UnsupportedOperationException("Not yet implemented");
    }
}