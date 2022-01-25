package com.cnil.dagas;

import android.os.Bundle;

import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.cnil.dagas.databinding.FragmentRequestsBinding;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;

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
        private JSONObject donationAddResponse;

        public GrabRequests(RequestsAdapter adapter) {
            this.adapter = adapter;
        }



        public void run() {
            try {
                grabRequests();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void grabRequests() throws IOException, JSONException {
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(REQUESTS_URL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONArray requestJSONArray = new JSONArray(response.body().string());
            for (int index = 0; index < requestJSONArray.length(); index++) {
                JSONObject requestJSONObject = requestJSONArray.getJSONObject(index);
                Request barangayProfileRequest = client.builderFromFullUrl(requestJSONObject.getString("barangay"))
                        .get()
                        .build();
                Response barangayResponse = client.newCall(barangayProfileRequest).execute();
                JSONObject barangayJSON = new JSONObject(barangayResponse.body().string());
                String barangayName = barangayJSON.getString("user");

                Request evacuationCenterRequest = client.builderFromBaseUrl(
                                    EVAC_CENTER_URL + requestJSONObject.getInt("evacuation_center") + "/")
                                            .get()
                                            .build();
                Response evacuationCenterResponse = client.newCall(evacuationCenterRequest).execute();
                JSONObject evacCenterJSON = new JSONObject(evacuationCenterResponse.body().string());
                String evacCenterName = evacCenterJSON.getString("name");

                this.adapter.add(new RequestsAdapter.BarangayRequest(barangayName, evacCenterName,
                                        REQUESTS_URL + requestJSONObject.getInt("id") + "/"));

            }

            //TODO: Check for errors

        }
    }

    FragmentRequestsBinding binding;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentRequestsBinding.inflate(inflater, container, false);
        View root = binding.getRoot();
        RecyclerView requestRecyclerView = root.findViewById(R.id.requestRecycler);
        RequestsAdapter adapter = new RequestsAdapter();
        GrabRequests thread = new GrabRequests(adapter);
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }
        requestRecyclerView.setAdapter(adapter);
        requestRecyclerView.setLayoutManager(new LinearLayoutManager(root.getContext()));


        return root;
    }
}