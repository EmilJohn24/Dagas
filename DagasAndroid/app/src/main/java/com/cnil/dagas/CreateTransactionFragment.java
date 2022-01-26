package com.cnil.dagas;

import android.os.Bundle;

import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.cnil.dagas.databinding.EvacuationcentervisualmapBinding;
import com.cnil.dagas.databinding.FragmentCreateTransactionBinding;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.Response;


public class CreateTransactionFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";
    private static final String TAG = CreateTransactionFragment.class.getName();
    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;

    public CreateTransactionFragment() {
        // Required empty public constructor
    }
    public static class GrabSupplies extends Thread {
        private static final String CURRENT_SUPPLIES_URL = "/relief/api/supplies/current_supplies/";
        private static final String ITEM_TYPE_URL = "/relief/api/item-type/";
        private static final String AVAILABLE_PAX = "/relief/api/supplies/%d/available_pax/";
        private static final String SPECIFIC_ITEM_TYPE_URL = "/relief/api/item-type/%d/";
        private static final String SUPPLY_URL = "/relief/api/supplies/%d/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");


        private TransactionSupplyAdapter adapter;
        private JSONObject donationAddResponse;

        public GrabSupplies(TransactionSupplyAdapter adapter) {
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
            Request request = client.builderFromBaseUrl(CURRENT_SUPPLIES_URL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONArray requestJSONArray = new JSONArray(response.body().string());
            for (int index = 0; index < requestJSONArray.length(); index++) {
                JSONObject requestJSONObject = requestJSONArray.getJSONObject(index);
                String itemName = requestJSONObject.getString("name");
                int itemID = requestJSONObject.getInt("id");
                int itemTypeID = requestJSONObject.getInt("type");
                int pax = requestJSONObject.getInt("pax");
                Request itemTypeRequest = client.builderFromBaseUrl(
                                            String.format(SPECIFIC_ITEM_TYPE_URL, itemTypeID))
                                        .get()
                                        .build();
                Response itemTypeResponse = client.newCall(itemTypeRequest).execute();
                JSONObject itemTypeJSON = new JSONObject(itemTypeResponse.body().string());
                String itemTypeName = itemTypeJSON.getString("name");

                Request availablePaxRequest = client.builderFromBaseUrl(
                                            String.format(AVAILABLE_PAX, itemID))
                                        .get()
                                        .build();
                Response availablePaxResponse = client.newCall(availablePaxRequest).execute();
                JSONObject availablePaxJSON = new JSONObject(availablePaxResponse.body().string());
                int available = availablePaxJSON.getInt("available");

                adapter.add(new TransactionSupplyAdapter.TransactionSupply(
                                itemName, itemTypeName,
                                available, String.format(SUPPLY_URL, itemID))
                        );

            }

            //TODO: Check for errors

        }
    }
//    /**
//     * Use this factory method to create a new instance of
//     * this fragment using the provided parameters.
//     *
//     * @param param1 Parameter 1.
//     * @param param2 Parameter 2.
//     * @return A new instance of fragment CreateTransactionFragment.
//     */
//    // TODO: Rename and change types and number of parameters
//    public static CreateTransactionFragment newInstance(String param1, String param2) {
//        CreateTransactionFragment fragment = new CreateTransactionFragment();
//        Bundle args = new Bundle();
//        args.putString(ARG_PARAM1, param1);
//        args.putString(ARG_PARAM2, param2);
//        fragment.setArguments(args);
//        return fragment;
//    }
//
//    @Override
//    public void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//        if (getArguments() != null) {
//            mParam1 = getArguments().getString(ARG_PARAM1);
//            mParam2 = getArguments().getString(ARG_PARAM2);
//        }
//    }
    TransactionSupplyAdapter.TransactionSupplyCallback callback;

    FragmentCreateTransactionBinding binding;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentCreateTransactionBinding.inflate(inflater, container, false);
        assert getArguments() != null;
        String requestURL = getArguments().getString("REQUEST_URL");
        View root = binding.getRoot();
        RecyclerView supplyRecycler = root.findViewById(R.id.transactionSupplyRecycler);
        callback = new TransactionSupplyAdapter.TransactionSupplyCallback() {
            @Override
            public void respond(int position, TransactionSupplyAdapter.TransactionSupply supply, int amount) {
                //TODO: add stuff
            }
        };

        TransactionSupplyAdapter adapter = new TransactionSupplyAdapter(callback);
        GrabSupplies thread = new GrabSupplies(adapter);
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }
        supplyRecycler.setAdapter(adapter);
        supplyRecycler.setLayoutManager(new LinearLayoutManager(root.getContext()));

        return root;
    }
}