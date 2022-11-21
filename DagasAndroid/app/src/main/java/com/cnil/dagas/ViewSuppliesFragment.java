package com.cnil.dagas;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.cnil.dagas.databinding.FragmentViewSuppliesBinding;
import com.cnil.dagas.databinding.NextPreviousBinding;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.Response;


public class ViewSuppliesFragment extends Fragment {

    private static final String TAG = ViewSuppliesFragment.class.getName();

    public static class GrabSupplies extends Thread {
        private static final String CURRENT_SUPPLIES_URL = "/relief/api/supplies/current_supplies/";
        private static final String ITEM_TYPE_URL = "/relief/api/item-type/";
        private static final String AVAILABLE_PAX = "/relief/api/supplies/%d/available_pax/";
        private static final String SPECIFIC_ITEM_TYPE_URL = "/relief/api/item-type/%d/";
        private static final String SUPPLY_URL = "/relief/api/supplies/%d/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");


        private ViewSupplyAdapter adapter;

        public GrabSupplies(ViewSupplyAdapter adapter) {
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
                int available = requestJSONObject.getInt("available_pax");

                String itemTypeName = requestJSONObject.getString("type_str");
                //CHANGE: Removing unnecessary request for available pax
                /*
                    Request availablePaxRequest = client.builderFromBaseUrl(
                            String.format(AVAILABLE_PAX, itemID))
                            .get()
                            .build();
                    Response availablePaxResponse = client.newCall(availablePaxRequest).execute();
                    JSONObject availablePaxJSON = new JSONObject(availablePaxResponse.body().string());
                    int available = availablePaxJSON.getInt("available");
                */
                String supplyPictureUrl = requestJSONObject.optString("picture");
                String expiration;
                if (itemTypeName.equals("Clothes")) expiration= "";
                else{
                    String[] originalFormExpiration = requestJSONObject.getString("expiration_date").split("T");
                    expiration = originalFormExpiration[0];
                }
                ViewSupplyAdapter.ViewSupply supply = new ViewSupplyAdapter.ViewSupply(
                        itemName, itemTypeName,
                        available, String.format(SUPPLY_URL, itemID), itemID, expiration);
                if (supplyPictureUrl != ""){
                    supply.setPictureUrl(supplyPictureUrl);
                }
                adapter.add(supply);
            }

            //TODO: Check for errors

        }
    }


    public ViewSuppliesFragment() {
        // Required empty public constructor
    }

    FragmentViewSuppliesBinding binding;
//
//    @Override
//    public void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentViewSuppliesBinding.inflate(inflater, container, false);
        View root = binding.getRoot();
        RecyclerView supplyRecycler = root.findViewById(R.id.viewSupplyListRecycler);
        NextPreviousBinding navigatorBar = binding.navigatorBar;
        navigatorBar.nextButton.setOnClickListener(view -> {
            Navigation.findNavController(view).navigate(R.id.action_nav_view_supplies_to_nav_suggestions);
        });

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

        ViewSupplyAdapter adapter = new ViewSupplyAdapter(callback);
        supplyRecycler.setAdapter(adapter);
        supplyRecycler.setLayoutManager(new LinearLayoutManager(root.getContext()));
        GrabSupplies thread = new GrabSupplies(adapter);
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return root;
    }
}