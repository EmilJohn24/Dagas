package com.cnil.dagas.ui.home.resident;

import android.content.Context;
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
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;


import com.cnil.dagas.R;
import com.cnil.dagas.data.CurrentUserThread;
import com.cnil.dagas.data.ResidentRegisterActivity;
import com.cnil.dagas.databinding.EvacuationcentervisualmapBinding;
import com.cnil.dagas.http.DagasJSONServerThread;
import com.cnil.dagas.http.OkHttpSingleton;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapView;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.material.floatingactionbutton.FloatingActionButton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

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
    private static String roleVerbose = null;
    public static class GrabEvacsThread extends DagasJSONServerThread {
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
            JSONArray evacCenterJSONArray = this.getList(CURR_EVAC_CENTER_URL);
            for (int typeIndex = 0; typeIndex < evacCenterJSONArray.length(); typeIndex++) {
                JSONObject typeJSONObject = evacCenterJSONArray.getJSONObject(typeIndex);
                this.centers.add(typeJSONObject);
            }

            //TODO: Check for errors

        }
    }
    static class AddEvacThread extends DagasJSONServerThread {
        private static final String EVAC_CENTER_URL = "/relief/api/evacuation-center/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");


       private final String name;
       private final Context context;
       private final double latitude;
       private final double longtitude;
       private final String geolocation;
       private String address;

       AddEvacThread(String name, Context context, double latitude, double longtitude){
           this.name = name;
           this.context = context;
           this.latitude = latitude;
           this.longtitude = longtitude;
           this.address = "Placeholder";
           this.geolocation = latitude + "," + longtitude;
       }



        public void run() {
            try {
                Geocoder geocoder = new Geocoder(context);
                List<Address> addressComponents = geocoder.getFromLocation(
                        latitude, longtitude, 1);
                if (!addressComponents.isEmpty()) {
                    this.address = addressComponents.get(0).getFeatureName() + ", " +
                            addressComponents.get(0).getLocality() + ", " +
                            addressComponents.get(0).getAdminArea() + ", " +
                            addressComponents.get(0).getCountryName();
                }

            } catch (IOException e) {
                Log.e(TAG, e.getMessage());
                this.address = this.name;
            }
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
            Response response = this.post(EVAC_CENTER_URL, createRequestJSON);
        }
    }

    private EvacuationcentervisualmapBinding binding;
    private MapView mapView;
    private GoogleMap map;
    private Marker newEvacMarker = null;

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState){

        binding = EvacuationcentervisualmapBinding.inflate(inflater, container, false);
        View root = binding.getRoot();
//        SupportMapFragment mapFragment = (SupportMapFragment) this.getChildFragmentManager()
//                .findFragmentById(R.id.evacMap);
        //Load current user data
        CurrentUserThread currentUserThread = new CurrentUserThread();
        currentUserThread.start();
        try {
            currentUserThread.join();
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }
        try {
            roleVerbose = currentUserThread.getUser().getString("role");
        } catch (JSONException e) {
            e.printStackTrace();
        }
        if(!roleVerbose.equals("3")) {
            root.findViewById(R.id.addEvacButton).setVisibility(View.INVISIBLE);
            root.findViewById(R.id.addressSearchBar).setVisibility(View.INVISIBLE);
        }
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
        EditText addressSearchBar = root.findViewById(R.id.addressSearchBar);
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
        if(roleVerbose.equals("3")) {
            //Create Evacuation Center
            //        map.addMarker(new MarkerOptions().)
            EditText editTextEvacName = root.findViewById(R.id.editTextEvacName);
            FloatingActionButton addEvacButton = root.findViewById(R.id.addEvacButton);
            final Marker[] marker = {null};
            addressSearchBar.setOnEditorActionListener(new TextView.OnEditorActionListener() {
                @Override
                public boolean onEditorAction(TextView textView, int actionID, KeyEvent keyEvent) {
                    if (actionID == EditorInfo.IME_ACTION_DONE) {
                        String address = addressSearchBar.getText().toString();
                        // Based on: https://stackoverflow.com/questions/17160508/how-to-search-address-by-name-on-google-map-android
                        Geocoder geoCoder = new Geocoder(EvacuationVisualMapFragment.this.getContext(), Locale.getDefault());
                        try {
                            List<Address> addresses = geoCoder.getFromLocationName(address, 5);
                            if (addresses.size() > 0) {
                                Double lat = (double) (addresses.get(0).getLatitude());
                                Double lon = (double) (addresses.get(0).getLongitude());

                                Log.d("lat-long", "" + lat + "......." + lon);
                                final LatLng user = new LatLng(lat, lon);
                                if (marker[0] != null) marker[0].remove();
                                marker[0] = map.addMarker(new MarkerOptions()
                                        .position(user)
                                        .title(address));
                                // Move the camera instantly to hamburg with a zoom of 15.
                                map.moveCamera(CameraUpdateFactory.newLatLngZoom(user, 25));

                                // Zoom in, animating the camera.
                                map.animateCamera(CameraUpdateFactory.zoomTo(20), 2000, null);
                            }
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                        return true;
                    }
                    return false;
                }
            });

            map.setOnMapClickListener(new GoogleMap.OnMapClickListener() {
                @Override
                public void onMapClick(@NonNull LatLng latLng) {
                    if (marker[0] != null) marker[0].remove();
                    if (newEvacMarker != null) newEvacMarker.remove();
                    newEvacMarker = map.addMarker(new MarkerOptions()
                            .position(latLng)
                            .title("New Evacuation Center"));

                }
            });
            editTextEvacName.setOnEditorActionListener(new TextView.OnEditorActionListener() {
                @Override
                public boolean onEditorAction(TextView textView, int actionID, KeyEvent keyEvent) {
                    if (actionID == EditorInfo.IME_ACTION_DONE) {
                        // Add Evacuation Center
                        //TODO: Find better ways to get address
                        try {
                            if (marker[0] != null)
                                marker[0].remove(); //remove marker from search bar
                            String name = editTextEvacName.getText().toString();
                            AddEvacThread addEvacThread = new AddEvacThread(name, EvacuationVisualMapFragment.this.getContext(),
                                    newEvacMarker.getPosition().latitude, newEvacMarker.getPosition().longitude);
                            addEvacThread.start();
                            addEvacThread.join();
                            LatLng newEvacLatLng = new LatLng(newEvacMarker.getPosition().latitude, newEvacMarker.getPosition().longitude);
                            map.addMarker(new MarkerOptions()
                                    .position(newEvacLatLng)
                                    .title(name));
                            newEvacMarker.remove();
                            editTextEvacName.getText().clear();
                            editTextEvacName.setVisibility(View.GONE);
                            String address = null;
                            try {
                                Geocoder geocoder = new Geocoder(EvacuationVisualMapFragment.this.getContext());
                                List<Address> addressComponents = geocoder.getFromLocation(
                                        newEvacMarker.getPosition().latitude, newEvacMarker.getPosition().longitude, 1);
                                if (!addressComponents.isEmpty()) {
                                    address = addressComponents.get(0).getFeatureName() + ", " +
                                            addressComponents.get(0).getLocality() + ", " +
                                            addressComponents.get(0).getAdminArea() + ", " +
                                            addressComponents.get(0).getCountryName();
                                }

                            } catch (IOException e) {
                                Log.e(TAG, e.getMessage());
                                address = name;
                            }
                            JSONObject createRequestJSON = new JSONObject();
                            createRequestJSON.put("name", name);
                            createRequestJSON.put("address", address);
                            createRequestJSON.put("geolocation", newEvacMarker.getPosition().latitude + "," + newEvacMarker.getPosition().longitude);
                            adapter.add(name);
                            adapter.notifyDataSetChanged();
                            centers.add(createRequestJSON);
                            Toast.makeText(EvacuationVisualMapFragment.this.getContext(), "Registration complete", Toast.LENGTH_SHORT).show();
                        } catch (InterruptedException | JSONException e) {
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
}