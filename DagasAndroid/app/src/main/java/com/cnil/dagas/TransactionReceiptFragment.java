package com.cnil.dagas;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.location.Location;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.cnil.dagas.data.CurrentUserThread;
import com.cnil.dagas.databinding.FragmentTransactionReceiptBinding;
import com.cnil.dagas.http.OkHttpSingleton;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapView;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.tasks.OnSuccessListener;
import com.squareup.picasso.Picasso;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;


public class TransactionReceiptFragment extends Fragment  implements OnMapReadyCallback {
    static private final String TAG = TransactionReceiptFragment.class.getName();
    double userLat = 0;
    double userLong = 0;

    // Based on: https://stackoverflow.com/questions/18125241/how-to-get-data-from-service-to-activity
    private BroadcastReceiver mMessageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            // Get extra data included in the Intent
            String message = intent.getStringExtra("Status");
            Bundle b = intent.getBundleExtra("Location");
            userLat = b.getDouble("latitude");
            userLong = b.getDouble("longitude");
            // Toast.makeText(context, message, Toast.LENGTH_SHORT).show();
        }
    };

    public static class RetrieveTransactionInfo extends Thread{
        private String transactionURL;
        private JSONObject transactionJSON;
        private JSONObject evacuationCenterJSON;

        public RetrieveTransactionInfo(String transactionURL) {
            this.transactionURL = transactionURL;
        }

        public void run(){
            try {
                retrieveTransaction();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }

        void retrieveTransaction() throws IOException, JSONException{
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(transactionURL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            this.transactionJSON = new JSONObject(response.body().string());


            Request evacuationCenterRequest = client.builderFromBaseUrl(transactionURL + "evacuation_center/")
                    .get()
                    .build();
            Response evacuationCenterResponse = client.newCall(evacuationCenterRequest).execute();

            this.evacuationCenterJSON = new JSONObject(evacuationCenterResponse.body().string());
        }

        public JSONObject getTransactionJSON() {
            return transactionJSON;
        }

        public JSONObject getEvacuationCenterJSON() {
            return evacuationCenterJSON;
        }
    }

    public TransactionReceiptFragment() {
        // Required empty public constructor
    }

    private MapView evacuationCenterMapView;
    private GoogleMap map;
    private FusedLocationProviderClient locationClient;
    FragmentTransactionReceiptBinding binding;


    @Override
    public void onMapReady(@NonNull GoogleMap googleMap) {
        map = googleMap;
        View root = binding.getRoot();
        assert getArguments() != null;
        String transactionURL = getArguments().getString("TRANSACTION_URL");
        //TODO: Implement mapview and recyclerview
        //TODO: Add transaction status
        evacuationCenterMapView = root.findViewById(R.id.evacMapView);
        ImageView qrCodeImageView = root.findViewById(R.id.qrCodeImageView);
        TextView referenceNumberTextView = root.findViewById(R.id.referenceNumberTextView);
        TextView donorNameTextView = root.findViewById(R.id.donorNameTextView);
        TextView statusLabel = binding.statusLabel;
        TextView statusTextView = binding.statusTextView;
        Button statusUpdateButton = binding.statusUpdateButton;
        RetrieveTransactionInfo thread = new RetrieveTransactionInfo(transactionURL);
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        try {
            String qrURL = thread.getTransactionJSON().getString("qr_code");
            Picasso.with(getContext()).load(qrURL)
                    .into(qrCodeImageView);
            referenceNumberTextView.setText(thread.getTransactionJSON().getString("id"));
            donorNameTextView.setText(thread.getTransactionJSON().getString("donor_name"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        // TODO: Convert to function (See EvacuationVisualMapFragment.java)
        JSONObject evacuationCenterJSON = thread.getEvacuationCenterJSON();
        try {
            String coord = evacuationCenterJSON.getString("geolocation");
            String name = evacuationCenterJSON.getString("name");
            String[] splitCoord = coord.split(",");
            double latitude = Float.parseFloat(splitCoord[0]);
            double longtitude = Float.parseFloat(splitCoord[1]);
            LatLng evacLatLng = new LatLng(latitude, longtitude);

            map.addMarker(new MarkerOptions()
                            .position(new LatLng(userLat,userLong))
                            .title("user location"));
            map.addMarker(new MarkerOptions()
                            .position(evacLatLng)
                            .title(name));
            map.animateCamera(CameraUpdateFactory.newLatLngZoom(evacLatLng, 20));
            locationClient.getLastLocation()
                    .addOnSuccessListener(this.getActivity(), new OnSuccessListener<Location>() {
                        @Override
                        public void onSuccess(Location location) {
                            if (location != null) {
                                //TODO: Do location stuff
                                LatLng userLocation = new LatLng(location.getLatitude(), location.getLongitude());
                                map.addMarker(new MarkerOptions()
                                        .position(userLocation)
                                        .title("Your location"));
                            }
                        }
                    });

        } catch (JSONException e) {
            e.printStackTrace();
        }

        CurrentUserThread currentUserThread = new CurrentUserThread();
        currentUserThread.start();
        try {
            currentUserThread.join();
            JSONObject currentUser = currentUserThread.getUser();
            Integer status = thread.getTransactionJSON().getInt("received");
            String transactionId = thread.getTransactionJSON().getString("id");
            switch (status){
                // TODO: Change to constants or enum
                // Packaging
                case 1:
                    statusTextView.setText("Packaging");
                    break;
                case 2:
                    statusTextView.setText("Incoming");
                    break;
                case 3:
                    statusTextView.setText("Received");
            }
            Integer role = currentUser.getInt("role");
            if (role == CurrentUserThread.BARANGAY){
                statusUpdateButton.setText("RECEIVED");
                if (status != 2) statusUpdateButton.setEnabled(false);
            } else if (role == CurrentUserThread.DONOR){
                statusUpdateButton.setText("PACKAGED");
                if (status != 1) statusUpdateButton.setEnabled(false);
            } else{
                statusUpdateButton.setVisibility(Button.INVISIBLE);
            }

            statusUpdateButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    Thread quickStatusUpdateThread = new Thread(new Runnable() {
                        final private String UPDATE_URL = "/relief/api/transactions/%s/quick_update_status/";
                        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
                        @Override
                        public void run() {
                            JSONObject emptyBody = new JSONObject();
                            RequestBody body = RequestBody.create(emptyBody.toString(), JSON);
                            OkHttpSingleton client = OkHttpSingleton.getInstance();
                            Request updateRequest = client.builderFromBaseUrl(String.format(UPDATE_URL, transactionId))
                                                            .put(body)
                                                            .build();
                            try {
                                Response updateResponse = client.newCall(updateRequest).execute();
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                        }
                    });
                    quickStatusUpdateThread.start();
                    try {
                        quickStatusUpdateThread.join();
                        //TODO: Add notification
                        Toast.makeText(TransactionReceiptFragment.this.getContext(), "Updated status", Toast.LENGTH_SHORT).show();
                        //refresh page
                        //Based on: https://stackoverflow.com/questions/63840150/reload-fragment-using-navigation-component
                        NavController navController = Navigation.findNavController(root);
                        int currentNavId = navController.getCurrentDestination().getId();
                        navController.popBackStack(currentNavId, true);
                        Bundle bundle = new Bundle();
                        bundle.putString("TRANSACTION_URL", transactionURL);
                        navController.navigate(currentNavId, bundle);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            });
        } catch (InterruptedException | JSONException e) {
            e.printStackTrace();
        }

    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        View root = binding.getRoot();
        LocalBroadcastManager.getInstance(getContext()).registerReceiver(
                mMessageReceiver, new IntentFilter("GPSLocationUpdates"));
        evacuationCenterMapView = root.findViewById(R.id.evacMapView);
        evacuationCenterMapView.onCreate(savedInstanceState);
        evacuationCenterMapView.onResume();
        evacuationCenterMapView.getMapAsync(this);
    }
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentTransactionReceiptBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        locationClient = LocationServices.getFusedLocationProviderClient(this.getActivity());
    }
}