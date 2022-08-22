package com.cnil.dagas;

import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.cnil.dagas.http.DagasJSONServer;
import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.placeholder.Suggestion;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapView;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
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

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.Response;

/**
 * A fragment representing a list of Items.
 */
public class SuggestionNodeFragment extends Fragment implements OnMapReadyCallback {
    private static String TAG = SuggestionNodeFragment.class.getName();
    private MapView suggestionMapView;
    private GoogleMap map;
    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        suggestionMapView.onCreate(savedInstanceState);
        suggestionMapView.onResume();
        suggestionMapView.getMapAsync(this);
    }
    @Override
    public void onMapReady(@NonNull GoogleMap googleMap) {
        map = googleMap;

        TransactionReceiptFragment.RetrieveGeolocation geolocationThread = new TransactionReceiptFragment
                                                            .RetrieveGeolocation(TransactionReceiptFragment
                                                                                    .RetrieveGeolocation.SELF);
        geolocationThread.start();
        try {
            geolocationThread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        LatLng donorGeolocation = new LatLng(geolocationThread.getDonorLat(), geolocationThread.getDonorLong());
                        map.getUiSettings().setZoomControlsEnabled(true);
                map.moveCamera(CameraUpdateFactory.newLatLngZoom(donorGeolocation, 15));
        Marker donorMarker = map.addMarker(new MarkerOptions()
                .position(donorGeolocation)
                .title("Donor Position"));
                //Create dummy node from donor
        Suggestion.SuggestionNode previousNode = new Suggestion.SuggestionNode(
                "-1", "Donor", "Donor", donorGeolocation);
        GeoApiContext context = new GeoApiContext.Builder()
                .apiKey("AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM")
                .build();
        for (Suggestion.SuggestionNode node : Suggestion.ITEMS){
            Marker nodeMarker = map.addMarker(new MarkerOptions()
                    .position(node.getEvacCoordinate())
                    .title(node.suggestedEvacuationCenterName));

            List<LatLng> path = new ArrayList();

            DirectionsApiRequest req = DirectionsApi.getDirections(context,
                    previousNode.getEvacCoordinate().latitude + "," + previousNode.getEvacCoordinate().longitude,
                    node.getEvacCoordinate().latitude + "," + node.getEvacCoordinate().longitude);

            DirectionsResult res = null;
            try {
                res = req.await();
            } catch (ApiException | IOException | InterruptedException e) {
                e.printStackTrace();
                Log.e(TAG, e.getMessage());
            }


            //Loop through legs and steps to get encoded polylines of each step
            if (res.routes != null && res.routes.length > 0) {
                //TODO: Consider placing this into a function
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
                map.addPolyline(opts);
            }

            //Set previous node to current node
            previousNode = node;
//            if(!firstAnimateCamera[0]) {
//                map.getUiSettings().setZoomControlsEnabled(true);
//                map.moveCamera(CameraUpdateFactory.newLatLngZoom(new LatLng(retrieveGeolocationThread.getDonorLat(),
//                        retrieveGeolocationThread.getDonorLong()), 15));
//                firstAnimateCamera[0] = true;
//            }
        }
    }

    public static class GrabSuggestionNodes extends Thread {
        private static final String SUGGESTION_URL = "/relief/api/suggestions/";

        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");



        public void run() {
            try {
                grabSuggestions();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void grabSuggestions() throws IOException, JSONException {
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(SUGGESTION_URL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONArray suggestionJSONArray = new JSONArray(response.body().string());
            for (int index = 0; index < suggestionJSONArray.length(); index++) {
                String donorName = suggestionJSONArray.getJSONObject(index).getString("donor_name");
                JSONArray routeNodes = suggestionJSONArray.getJSONObject(index).getJSONArray("route_nodes");
                for (int nodeIndex = 0; nodeIndex < routeNodes.length(); nodeIndex++){
                    JSONObject currentNode = routeNodes.getJSONObject(nodeIndex);
                    String id = currentNode.getString("id");
                    String barangayName = currentNode.getString("barangay_name");
                    String evacuationCenterName = currentNode.getString("evacuation_center_name");

                    // Parse geolocation
                    String geolocationString = currentNode.getString("evacuation_center_geolocation");
                    String[] splitCoord = geolocationString.split(",");
                    double latitude = Float.parseFloat(splitCoord[0]);
                    double longtitude = Float.parseFloat(splitCoord[1]);
                    LatLng evacCoordinate = new LatLng(latitude, longtitude);

                    Suggestion.SuggestionNode node = new Suggestion.SuggestionNode(id, barangayName,
                                evacuationCenterName, evacCoordinate);
                    JSONArray fufillments = currentNode.getJSONArray("fulfillments");

                    for (int fIndex = 0; fIndex < fufillments.length(); fIndex++){
                        JSONObject fulfillment = fufillments.getJSONObject(fIndex);
                        String itemType = fulfillment.getString("type_name");
                        Integer amount = fulfillment.getInt("pax");
                        node.addFulfillment(itemType, amount);

                    }

                    Suggestion.ITEMS.add(node);
                }
            }

            //TODO: Check for errors

        }
    }

    // TODO: Customize parameter argument names
    private static final String ARG_COLUMN_COUNT = "column-count";
    // TODO: Customize parameters
    private int mColumnCount = 1;

    /**
     * Mandatory empty constructor for the fragment manager to instantiate the
     * fragment (e.g. upon screen orientation changes).
     */
    public SuggestionNodeFragment() {
    }

    // TODO: Customize parameter initialization
    @SuppressWarnings("unused")
    public static SuggestionNodeFragment newInstance(int columnCount) {
        SuggestionNodeFragment fragment = new SuggestionNodeFragment();
        Bundle args = new Bundle();
        args.putInt(ARG_COLUMN_COUNT, columnCount);
        fragment.setArguments(args);

        //Item initialization

        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (getArguments() != null) {
            mColumnCount = getArguments().getInt(ARG_COLUMN_COUNT);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_card_suggestions, container, false);
        suggestionMapView = view.findViewById(R.id.suggestionMapView);
        GrabSuggestionNodes suggestionThread = new GrabSuggestionNodes();
        suggestionThread.start();
        try {
            suggestionThread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        RecyclerView recyclerView =  view.findViewById(R.id.list);
        // Set the adapter
        if (recyclerView != null) {
            Context context = view.getContext();
            if (mColumnCount <= 1) {
                recyclerView.setLayoutManager(new LinearLayoutManager(context));
            } else {
                recyclerView.setLayoutManager(new GridLayoutManager(context, mColumnCount));
            }
            recyclerView.setAdapter(new SuggestionNodeRecyclerViewAdapter(Suggestion.ITEMS));
        }

        Button acceptSuggestionButton = view.findViewById(R.id.acceptSuggestionsButton);
        View navigatorBarView = view.findViewById(R.id.navigator_bar);
        Button manualRequestButton = navigatorBarView.findViewById(R.id.nextButton);
        acceptSuggestionButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View buttonView) {
                // /relief/api/transactions/transactions_from_suggestion/
                try {
                    DagasJSONServer.post("/relief/api/transactions/transactions_from_suggestion/", new JSONObject());
                    //action_nav_suggestions_to_nav_transactions
                    Navigation.findNavController(view)
                            .navigate(R.id.action_nav_suggestions_to_nav_transactions);
                } catch (Exception e) {
                    Log.e(TAG, e.getMessage());
                }
            }
        });

        manualRequestButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Navigation.findNavController(view).navigate(R.id.action_nav_suggestions_to_nav_view_requests);
            }
        });
        return view;
    }
}