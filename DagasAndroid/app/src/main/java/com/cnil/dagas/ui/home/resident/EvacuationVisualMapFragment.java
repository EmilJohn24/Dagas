package com.cnil.dagas.ui.home.resident;

import android.location.Address;
import android.location.Geocoder;
import android.os.Bundle;
import android.util.Log;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
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
import com.google.android.material.floatingactionbutton.FloatingActionButton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.List;

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
    static class AddEvacThread extends Thread {
        private static final String EVAC_CENTER_URL = "/relief/api/evacuation-center/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");


       private String name;
       private String address;
       private String geolocation;

       AddEvacThread(String name, String address, double latitude, double longtitude){
           this.name = name;
           this.address = address;
           this.geolocation = latitude + ", " + longtitude;
       }



        public void run() {
            try {
                addEvac();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void addEvac() throws IOException, JSONException {
            JSONObject createRequestJSON = new JSONObject();
            try {
                createRequestJSON.put("name", name);
                createRequestJSON.put("address", address);
                createRequestJSON.put("geolocation", geolocation);
            } catch (JSONException e) {
                Log.e(TAG, e.getMessage());
            }
            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);


            OkHttpSingleton client = OkHttpSingleton.getInstance();
            Request request = client.builderFromBaseUrl(EVAC_CENTER_URL)
                    .post(body)
                    .build();
            //TODO: Check if request succeeded
            Response response = client.newCall(request).execute();

        }
    }

    private EvacuationcentervisualmapBinding binding;
    private MapView mapView;
    private GoogleMap map;
    private Marker newEvacMarker;

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
            //TODO: Update markers after adding new evacuation center
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

        map.setOnMapClickListener(new GoogleMap.OnMapClickListener() {
            @Override
            public void onMapClick(@NonNull LatLng latLng) {
                    if (newEvacMarker != null) newEvacMarker.remove();
                    newEvacMarker = map.addMarker(new MarkerOptions()
                            .position(latLng)
                            .title("New Evacuation Center"));

            }
        });
        //Create Evacuation Center
//        map.addMarker(new MarkerOptions().)
        EditText editTextEvacName = root.findViewById(R.id.editTextEvacName);
        FloatingActionButton addEvacButton = root.findViewById(R.id.addEvacButton);
        editTextEvacName.setOnEditorActionListener(new TextView.OnEditorActionListener() {
            @Override
            public boolean onEditorAction(TextView textView, int actionID, KeyEvent keyEvent) {
                if (actionID == EditorInfo.IME_ACTION_DONE){
                    // Add Evacuation Center
                    //TODO: Find better ways to get address
                    Geocoder geocoder = new Geocoder(EvacuationVisualMapFragment.this.getContext());
                    try {
                        List<Address> addressComponents = geocoder.getFromLocation(
                                    newEvacMarker.getPosition().latitude, newEvacMarker.getPosition().longitude, 1);
                        if (!addressComponents.isEmpty()){
                            String address = addressComponents.get(0).getFeatureName() + ", " +
                                                addressComponents.get(0).getLocality() +", " +
                                                addressComponents.get(0).getAdminArea() + ", " +
                                                addressComponents.get(0).getCountryName();
                            String name = editTextEvacName.getText().toString();
                            AddEvacThread addEvacThread = new AddEvacThread(name, address,
                                    newEvacMarker.getPosition().latitude, newEvacMarker.getPosition().longitude);
                            addEvacThread.start();
                            addEvacThread.join();
                            editTextEvacName.getText().clear();

                        }
                    } catch (IOException | InterruptedException e) {
                        Log.e(TAG, e.getMessage());
                    }
                    return true;
                }
                return false;
            }
        });
        addEvacButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                editTextEvacName.setVisibility(View.VISIBLE);
            }
        });

    }
}