package com.cnil.dagas;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.cnil.dagas.data.CurrentUserThread;
import com.cnil.dagas.databinding.FragmentTransactionReceiptBinding;
import com.cnil.dagas.http.DagasJSONServer;
import com.cnil.dagas.http.OkHttpSingleton;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapView;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.Polyline;
import com.google.android.gms.maps.model.PolylineOptions;
import com.google.maps.DirectionsApi;
import com.google.maps.DirectionsApiRequest;
import com.google.maps.GeoApiContext;
import com.google.maps.errors.ApiException;
import com.google.maps.model.DirectionsLeg;
import com.google.maps.model.DirectionsResult;
import com.google.maps.model.DirectionsRoute;
import com.google.maps.model.DirectionsStep;
import com.google.maps.model.EncodedPolyline;
import com.squareup.picasso.Picasso;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

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
    public static class RetrieveGeolocation extends Thread {
        public static int SELF = -1;
        private int donorUserId;
        private double donorLat;
        private double donorLong;

        RetrieveGeolocation(int donorUserId){
            this.donorUserId = donorUserId;
        }
        public void run() {
            OkHttpSingleton client = OkHttpSingleton.getInstance();
            Request request = null;
            if (donorUserId == SELF){
                request = client.builderFromBaseUrl("/relief/api/users/get_own_most_recent_location/")
                        .get()
                        .build();

            } else {
               request = client.builderFromBaseUrl(
                        String.format(
                                "/relief/api/users/%d/get_most_recent_location/", donorUserId))
                        .get()
                        .build();
            }
            Response response = null;
            try {
                response = client.newCall(request).execute();
                JSONObject responseJSON = new JSONObject(response.body().string());
                String geolocationString = responseJSON.getString("geolocation");
                Log.i(TAG, "Setting geolocation of marker to: " + geolocationString);
                String[] geoSplit = geolocationString.split(",");
                donorLat = Float.parseFloat(geoSplit[0]);
                donorLong = Float.parseFloat(geoSplit[1]);
            } catch (JSONException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        public double getDonorLong() {
            return donorLong;
        }

        public double getDonorLat() {
            return donorLat;
        }
    }
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
        RecyclerView supplyRecycler = binding.supplyListRecycler;
        ViewSupplyAdapter.ViewSupplyCallback callback = new ViewSupplyAdapter.ViewSupplyCallback() {
            @Override
            public void respond(int position, ViewSupplyAdapter.ViewSupply supply, int amount) {
                //TODO: add TransactionOrder if it does not exist yet
            }

            @Override
            public void removeRespond(ViewSupplyAdapter.ViewSupply supply) {
            }
            @Override
            public void loadPicture(ViewSupplyAdapter.ViewSupply supply) {
                if (supply.hasPictureUrl()){
                    Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(supply.getPictureUrl()));
                    startActivity(browserIntent);
                }
            }
        };

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

            //Load in supply data
            ViewSupplyAdapter adapter = new ViewSupplyAdapter(callback);
            supplyRecycler.setAdapter(adapter);
            supplyRecycler.setLayoutManager(new LinearLayoutManager(root.getContext()));
            JSONArray transactionSupplyOrders = thread.getTransactionJSON().optJSONArray("transaction_orders");
            if (transactionSupplyOrders != null) {
                for (int i = 0; i != transactionSupplyOrders.length(); i++){
                    JSONObject transactionOrderInfo = transactionSupplyOrders.getJSONObject(i);
                    JSONObject supplyInfo = transactionOrderInfo.getJSONObject("supply_info");
                    String name = supplyInfo.getString("name");
                    Integer id = supplyInfo.getInt("id");
                    String type = supplyInfo.getString("type_str");
                    String supplyUrl = DagasJSONServer.createDetailUrl("/relief/api/supplies/", id);
                    String supplyPictureUrl = supplyInfo.optString("picture");
                    int availablePax = supplyInfo.getInt("available_pax");
                    ViewSupplyAdapter.ViewSupply supply = new ViewSupplyAdapter.ViewSupply(name, type, availablePax, supplyUrl, id);
                    if (!supplyPictureUrl.equals("")){
                        supply.setPictureUrl(supplyPictureUrl);
                    }
                    supply.setPaxTransacted(transactionOrderInfo.optInt("pax"));
                    adapter.add(supply);
                }
            }
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

            final Marker donorLocationMarker = map.addMarker(new MarkerOptions()
                            .position(new LatLng(0,0))
                            .title("Donor Location")
                            .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_CYAN)));
            map.addMarker(new MarkerOptions()
                            .position(evacLatLng)
                            .title(name));
            //map.animateCamera(CameraUpdateFactory.newLatLngZoom(evacLatLng, 1));

            //Direction Draw: https://stackoverflow.com/questions/47492459/how-do-i-draw-a-route-along-an-existing-road-between-two-points?fbclid=IwAR1adU2y6vUzwdKUPmcNjc44v43mD_omM7QmfJiyuUWUyaQfZGN3hFzzVFg
            //Define list to get all latlng for the route
            List<LatLng> path = new ArrayList();

            //Execute Directions API request
            GeoApiContext context = new GeoApiContext.Builder()
                    .apiKey("AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM")
                    .build();

            //Loader: https://stackoverflow.com/questions/10207612/android-execute-code-in-regular-intervals
            final int donorUserID = thread.getTransactionJSON().getJSONObject("donor_info").getInt("user");
            final Handler handler = new Handler();
            final boolean[] firstAnimateCamera = {false};
            final Polyline[] previousPath = {null, null};
            Runnable donorLocationThread = new Runnable() {
                @Override
                public void run() {

                    try{
                        RetrieveGeolocation retrieveGeolocationThread = new RetrieveGeolocation(donorUserID);
                        retrieveGeolocationThread.start();
                        retrieveGeolocationThread.join();
                        donorLocationMarker.setPosition(new LatLng(retrieveGeolocationThread.getDonorLat(),
                                                            retrieveGeolocationThread.getDonorLong()));

                        DirectionsApiRequest req = DirectionsApi.getDirections(context,retrieveGeolocationThread.getDonorLat() + "," + retrieveGeolocationThread.getDonorLong(),
                                latitude + "," + longtitude);

                        DirectionsResult res = null;
                        try {
                            res = req.await();
                        } catch (ApiException e) {
                            e.printStackTrace();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }

                        if(previousPath[0] != null || previousPath[1] != null) {
                            previousPath[0].remove();
                            previousPath[1].remove();
                            path.clear();
                        }
                        //Loop through legs and steps to get encoded polylines of each step
                        if (res.routes != null && res.routes.length > 0) {
                            DirectionsRoute route = res.routes[0];

                            if (route.legs !=null) {
                                for(int i=0; i<route.legs.length; i++) {
                                    DirectionsLeg leg = route.legs[i];
                                    if (leg.steps != null) {
                                        for (int j=0; j<leg.steps.length;j++){
                                            DirectionsStep step = leg.steps[j];
                                            if (step.steps != null && step.steps.length >0) {
                                                for (int k=0; k<step.steps.length;k++){
                                                    DirectionsStep step1 = step.steps[k];
                                                    EncodedPolyline points1 = step1.polyline;
                                                    if (points1 != null) {
                                                        //Decode polyline and add points to list of route coordinates
                                                        List<com.google.maps.model.LatLng> coords1 = points1.decodePath();
                                                        for (com.google.maps.model.LatLng coord1 : coords1) {
                                                            path.add(new LatLng(coord1.lat, coord1.lng));
                                                        }
                                                    }
                                                }
                                            } else {
                                                EncodedPolyline points = step.polyline;
                                                if (points != null) {
                                                    //Decode polyline and add points to list of route coordinates
                                                    List<com.google.maps.model.LatLng> coords = points.decodePath();
                                                    for (com.google.maps.model.LatLng coord : coords) {
                                                        path.add(new LatLng(coord.lat, coord.lng));
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        //Draw the polyline
                        if (path.size() > 0) {
                            PolylineOptions opts = new PolylineOptions().addAll(path).color(Color.BLUE).width(5);
                            previousPath[0] = map.addPolyline(opts);
                            previousPath[1] = map.addPolyline(opts);
                        }

                        if(!firstAnimateCamera[0]) {
                            map.getUiSettings().setZoomControlsEnabled(true);
                            map.moveCamera(CameraUpdateFactory.newLatLngZoom(new LatLng(retrieveGeolocationThread.getDonorLat(),
                                    retrieveGeolocationThread.getDonorLong()), 15));
                            firstAnimateCamera[0] = true;
                        }
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    } finally{
                        handler.postDelayed(this, 5000);
                    }
                }
            };
            handler.post(donorLocationThread);

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