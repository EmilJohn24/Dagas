package com.cnil.dagas;

import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import com.cnil.dagas.databinding.FragmentDonorAddSupplyBinding;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class DonorAddSupply extends Fragment {
    private final String TAG = DonorAddSupply.class.getName();
    public DonorAddSupply() {
        // Required empty public constructor
    }

    class SupplyAddThread extends Thread{
        private static final String DONATION_URL = "/relief/api/supplies/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        private final int donationID;
        private final String supplyName;
        private final int quantity, pax;
        private final int type;
        private String responseSupplyName;

        String getResponseSupplyName(){
            return this.responseSupplyName;
        }
        SupplyAddThread(int donationID, String supplyName, int quantity, int pax, int type){
            this.donationID = donationID;
            this.supplyName = supplyName;
            this.quantity = quantity;
            this.pax = pax;
            this.type = type;
        }
        public void run(){
            try {
                addSupplyToCurrentDonation();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }

        void addSupplyToCurrentDonation() throws IOException, JSONException{
            JSONObject createRequestJSON = new JSONObject();
            try {
                createRequestJSON.put("name", supplyName);
                // TODO: Check type + 1 (index)
                createRequestJSON.put("type", type + 1);
                createRequestJSON.put("quantity", quantity);
                createRequestJSON.put("pax", pax);
                createRequestJSON.put("donation", donationID);
            } catch (JSONException e) {
                Log.e(TAG, e.getMessage());
            }
            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);


            OkHttpSingleton client = OkHttpSingleton.getInstance();
            Request request = client.builderFromBaseUrl(DONATION_URL)
                    .post(body)
                    .build();
            Response response = client.newCall(request).execute();
            JSONObject supplyAddResponse = new JSONObject(response.body().string());
            this.responseSupplyName = supplyAddResponse.getString("name");
//            this.donationAddResponse = new JSONObject(response.body().string());
        }
    }

    class DonorAddThread extends Thread {
        private static final String TYPE_URL = "/relief/api/item-type/";
        private static final String DONATION_URL = "/relief/api/donations/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        private ArrayList<String> types;
        private JSONObject donationAddResponse;

        DonorAddThread() {
            this.types = new ArrayList<>();
        }

        ArrayList<String> getTypes() {
            return this.types;
        }
        int getDonationID() throws JSONException {
            return donationAddResponse.getInt("id");
        }
        public void run() {
            try {
                addDonationToServer();
                retrieveTypesFromServer();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void addDonationToServer() throws IOException, JSONException{
            JSONObject createRequestJSON = new JSONObject();
            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            OkHttpSingleton client = OkHttpSingleton.getInstance();
            Request request = client.builderFromBaseUrl(DONATION_URL)
                    .post(body)
                    .build();
            Response response = client.newCall(request).execute();
            this.donationAddResponse = new JSONObject(response.body().string());
            //TODO: Check for errors

        }
        private void retrieveTypesFromServer() throws IOException, JSONException {
//            JSONObject createRequestJSON = new JSONObject();
            // JSON Form Handling:
            // https://stackoverflow.com/questions/17810044/android-create-json-array-and-json-object
            // https://stackoverflow.com/questions/23456488/how-to-use-okhttp-to-make-a-post-request
            // https://stackoverflow.com/questions/34179922/okhttp-post-body-as-json
//            try {
//                createRequestJSON.put("", "");
//            } catch (JSONException e) {
//                Log.e(TAG, e.getMessage());
//            }

            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(TYPE_URL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONArray typeJSONArray = new JSONArray(response.body().string());
            for (int typeIndex = 0; typeIndex < typeJSONArray.length(); typeIndex++) {
                JSONObject typeJSONObject = typeJSONArray.getJSONObject(typeIndex);
                this.types.add(typeJSONObject.getString("name"));
            }
        }
    }


    FragmentDonorAddSupplyBinding binding;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentDonorAddSupplyBinding.inflate(inflater, container, false);
        View root = binding.getRoot();


        //Load spinner content
        Spinner spinnerType = root.findViewById(R.id.spinnerType);
        DonorAddThread thread = new DonorAddThread();
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this.getContext(), android.R.layout.simple_spinner_item, thread.getTypes());
        spinnerType.setAdapter(adapter);

        // Form data
        EditText supplyName = root.findViewById(R.id.supplyName);
        EditText editNumberQuantity = root.findViewById(R.id.editNumberQuantity);
        EditText editNumberPax = root.findViewById(R.id.editNumberPax);


        // Add supply button
        Button supplySubmitButton = root.findViewById(R.id.supplySubmitButton);

        supplySubmitButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    //TODO: Check for blanks
                    SupplyAddThread supplyThread = new SupplyAddThread(thread.getDonationID(),
                            supplyName.getText().toString(),
                            Integer.parseInt(editNumberQuantity.getText().toString()),
                            Integer.parseInt(editNumberPax.getText().toString()), spinnerType.getSelectedItemPosition());
                    supplyThread.start();
                    supplyThread.join();
                    Toast.makeText(DonorAddSupply.this.getContext(),"Added " + supplyThread.getResponseSupplyName() + "!",
                            Toast.LENGTH_SHORT).show();
                    supplyName.getText().clear();
                    editNumberPax.getText().clear();
                    editNumberQuantity.getText().clear();
                    spinnerType.setSelection(0);
                } catch (JSONException | InterruptedException e) {
                    Log.e(TAG, e.getMessage());
                }
            }
        });
        return root;

    }
}