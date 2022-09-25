package com.cnil.dagas;

import android.location.Location;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.cnil.dagas.databinding.FragmentRequestsBinding;
import com.cnil.dagas.http.OkHttpSingleton;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.tasks.OnSuccessListener;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.HashMap;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.Response;

/**
 * A simple {@link Fragment} subclass.
 * create an instance of this fragment.
 */
public class RequestsFragment extends Fragment {
    private static String TAG = RequestsFragment.class.getName();
    public static class GrabRequests extends Thread {
        private static final String REQUESTS_URL = "/relief/api/requests/";
        private static final String EVAC_CENTER_URL = "/relief/api/evacuation-center/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");



        private RequestsAdapter adapter;
        private Location userLocation;
        private JSONObject donationAddResponse;
        private String query;
        private boolean isQueried;
        public GrabRequests(RequestsAdapter adapter, Location userLocation) {
            this.adapter = adapter;
            this.userLocation = userLocation;
            this.query = "";
            this.isQueried = false;
        }



        public void run() {
            try {
                grabRequests();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }

        public void createQuery(String query){
            this.query = query;
            this.isQueried = true;
        }

        private void grabRequests() throws IOException, JSONException {
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request;
            if (!isQueried) {
                request = client.builderFromBaseUrl(REQUESTS_URL)
                        .get()
                        .build();
            } else{
                request = client.builderFromBaseUrl(REQUESTS_URL + "?search=" + query)
                        .get()
                        .build();
            }
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONArray requestJSONArray = new JSONArray(response.body().string());
            for (int index = 0; index < requestJSONArray.length(); index++) {
                JSONObject requestJSONObject = requestJSONArray.getJSONObject(index);
                JSONObject barangayJSON = requestJSONObject.getJSONObject("barangay_serialized");
                String barangayName = barangayJSON.getString("user");
                JSONObject evacCenterJSON = requestJSONObject.getJSONObject("evacuation_center_serialized");
                String evacCenterName = evacCenterJSON.getString("name");
                JSONArray itemRequestJSONArray = requestJSONObject.getJSONArray("item_requests_serialized");
                HashMap<String, Integer> itemRequestMap = new HashMap<String, Integer>();
                for (int innerIndex = 0; innerIndex < itemRequestJSONArray.length(); innerIndex++) {
                    JSONObject itemRequestJSONObject = itemRequestJSONArray.getJSONObject(innerIndex);
                    itemRequestMap.put(itemRequestJSONObject.getString("type_str"), itemRequestJSONObject.getInt("pax"));
                }
                String coord = evacCenterJSON.getString("geolocation");
                String[] splitCoord = coord.split(",");
                double latitude = Float.parseFloat(splitCoord[0]);
                double longtitude = Float.parseFloat(splitCoord[1]);
                Location evacLocation = new Location(LocationManager.GPS_PROVIDER);
                evacLocation.setLatitude(latitude);
                evacLocation.setLongitude(longtitude);
                double evacuationCenterDistance = userLocation.distanceTo(evacLocation);
                this.adapter.add(new RequestsAdapter.BarangayRequest(barangayName, evacCenterName,
                                        evacuationCenterDistance, REQUESTS_URL + requestJSONObject.getInt("id") + "/",
                                        requestJSONObject.getInt("id"), itemRequestMap));

            }

            //TODO: Check for errors

        }
    }

    FragmentRequestsBinding binding;
    private FusedLocationProviderClient locationClient;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentRequestsBinding.inflate(inflater, container, false);
        View root = binding.getRoot();
        RecyclerView requestRecyclerView = root.findViewById(R.id.requestRecycler);
        RequestsAdapter adapter = new RequestsAdapter();

        locationClient.getLastLocation()
                .addOnSuccessListener(this.getActivity(), new OnSuccessListener<Location>() {
                    @Override
                    public void onSuccess(Location location) {
                        if (location != null) {
                            //TODO: Do location stuff
                            GrabRequests thread = new GrabRequests(adapter, location);
                            thread.start();
                            try {
                                thread.join();
                                requestRecyclerView.setAdapter(adapter);
                                requestRecyclerView.setLayoutManager(new LinearLayoutManager(root.getContext()));

                                Button queryButton = binding.requestSearchButton;
                                TextView queryBox = binding.searchQueryTextView;
                                queryButton.setOnClickListener(view -> {
                                    adapter.clear(); // Clear adapter
                                    GrabRequests searchThread = new GrabRequests(adapter, location);
                                    String query = queryBox.getText().toString();
                                    searchThread.createQuery(query);
                                    searchThread.start();
                                    try {
                                        searchThread.join();
                                    } catch (InterruptedException e) {
                                        e.printStackTrace();
                                    }
                                });
                            } catch (InterruptedException e) {
                                Log.e(TAG, e.getMessage());
                            }
                        }
                    }
                });




        return root;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        locationClient = LocationServices.getFusedLocationProviderClient(this.getActivity());
    }
}