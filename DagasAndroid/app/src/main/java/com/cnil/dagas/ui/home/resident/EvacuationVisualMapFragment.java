package com.cnil.dagas.ui.home.resident;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;

import com.cnil.dagas.R;
import com.cnil.dagas.databinding.EvacuationcentervisualmapBinding;
import com.cnil.dagas.http.OkHttpSingleton;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapView;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.lang.reflect.Array;
import java.util.ArrayList;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

//Based on:
// https://stackoverflow.com/questions/35496493/getmapasync-in-fragment
// https://developers.google.com/maps/documentation/android-sdk/start#maps_android_mapsactivity-java
// https://developers.google.com/maps/documentation/android-sdk/reference/com/google/android/libraries/maps/SupportMapFragment
public class EvacuationVisualMapFragment extends Fragment implements OnMapReadyCallback {
    private final static String TAG = EvacuationVisualMapFragment.class.getName();
    static class GrabEvacsThread extends Thread {
        private static final String EVAC_CENTER_URL = "/relief/api/evacuation-center/";
        private static final String CURR_EVAC_CENTER_URL = "/relief/api/evacuation-center/current_evac/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");


        private ArrayList<JSONObject> centers;
        private JSONObject donationAddResponse;

        public GrabEvacsThread() {
            centers = new ArrayList<>();
        }


        ArrayList<JSONObject> getCenters() {
            return centers;
        }

        public void run() {
            try {
                grabEvacCoords();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void grabEvacCoords() throws IOException, JSONException {
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(CURR_EVAC_CENTER_URL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONArray evacCenterJSONArray = new JSONArray(response.body().string());
            for (int typeIndex = 0; typeIndex < evacCenterJSONArray.length(); typeIndex++) {
                JSONObject typeJSONObject = evacCenterJSONArray.getJSONObject(typeIndex);
                this.centers.add(typeJSONObject);
            }

            //TODO: Check for errors

        }
    }
    private EvacuationcentervisualmapBinding binding;
    private MapView mapView;
    private GoogleMap map;
    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState){

        binding = EvacuationcentervisualmapBinding.inflate(inflater, container, false);
        View root = binding.getRoot();
//        SupportMapFragment mapFragment = (SupportMapFragment) this.getChildFragmentManager()
//                .findFragmentById(R.id.evacMap);

        return root;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        View root = binding.getRoot();
        mapView = root.findViewById(R.id.mapView);
        mapView.onCreate(savedInstanceState);
        mapView.onResume();
        mapView.getMapAsync(this);
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
    @Override
    public void onMapReady(@NonNull GoogleMap googleMap) {
        map = googleMap;

        // Add a marker in Sydney and move the camera
//        LatLng sydney = new LatLng(-34, 151);
//        map.addMarker(new MarkerOptions()
//                .position(sydney)
//                .title("Marker in Sydney"));
//        map.moveCamera(CameraUpdateFactory.newLatLng(sydney));
        View root = binding.getRoot();
        mapView = root.findViewById(R.id.mapView);
        Spinner evacCenterSpinner = root.findViewById(R.id.evacCenterSpinner);
        GrabEvacsThread thread = new GrabEvacsThread();
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }
        // TODO: Convert to function
        // TODO: Move splitting to thread
        // TODO: Add name of evac center (title)
        ArrayList<JSONObject> centers = thread.getCenters();
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this.getContext(), android.R.layout.simple_spinner_item);
        for (JSONObject center : centers){
            String coord = null;
            String name = null;
            try {
                coord = center.getString("geolocation");
                name = center.getString("name");

            } catch (JSONException e) {
                Log.e(TAG, e.getMessage());
            }
            adapter.add(name);
            String[] splitCoord = coord.split(",");
            double latitude = Float.parseFloat(splitCoord[0]);
            double longtitude = Float.parseFloat(splitCoord[1]);
            LatLng evacLatLng = new LatLng(latitude, longtitude);
            map.addMarker(new MarkerOptions()
                            .position(evacLatLng)
                            .title(name));
        }
        evacCenterSpinner.setAdapter(adapter);
        evacCenterSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {
                JSONObject centerChosen = centers.get(i);
                String coord = null;
                try {
                    coord = centerChosen.getString("geolocation");
                    String[] splitCoord = coord.split(",");
                    double latitude = Float.parseFloat(splitCoord[0]);
                    double longtitude = Float.parseFloat(splitCoord[1]);
                                        LatLng evacLatLng = new LatLng(latitude, longtitude);
                    map.animateCamera(CameraUpdateFactory.newLatLngZoom(evacLatLng, 20));

                } catch (JSONException e) {
                    Log.e(TAG, e.getMessage());
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> adapterView) {

            }
        });


    }
}