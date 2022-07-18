package com.cnil.dagas;

import android.content.Context;
import android.os.Bundle;

import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.placeholder.Suggestion;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.Response;

/**
 * A fragment representing a list of Items.
 */
public class SuggestionNodeFragment extends Fragment {
    private static String TAG = SuggestionNodeFragment.class.getName();
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
                    Suggestion.SuggestionNode node = new Suggestion.SuggestionNode(id, barangayName, evacuationCenterName);
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
        GrabSuggestionNodes suggestionThread = new GrabSuggestionNodes();
        suggestionThread.start();
        try {
            suggestionThread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Set the adapter
        if (view instanceof RecyclerView) {
            Context context = view.getContext();
            RecyclerView recyclerView = (RecyclerView) view;
            if (mColumnCount <= 1) {
                recyclerView.setLayoutManager(new LinearLayoutManager(context));
            } else {
                recyclerView.setLayoutManager(new GridLayoutManager(context, mColumnCount));
            }
            recyclerView.setAdapter(new SuggestionNodeRecyclerViewAdapter(Suggestion.ITEMS));
        }
        return view;
    }
}