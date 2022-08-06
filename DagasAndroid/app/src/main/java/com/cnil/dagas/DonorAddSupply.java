package com.cnil.dagas;

import static androidx.core.content.FileProvider.getUriForFile;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;

import com.cnil.dagas.data.ImageAssistor;
import com.cnil.dagas.databinding.FragmentDonorAddSupplyBinding;
import com.cnil.dagas.http.DagasJSONServer;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
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
        private int responseSupplyId;

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
            this.responseSupplyId = supplyAddResponse.getInt("id");
//            this.donationAddResponse = new JSONObject(response.body().string());
        }

        public int getResponseSupplyId() {
            return responseSupplyId;
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
        ViewSupplyAdapter.ViewSupply supplyData = null;
        if (getArguments() != null) {
            supplyData = getArguments().getParcelable("SUPPLY_INFO");

        }

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
        int editDonationId = -1;
        JSONObject supplyLiveData = null;
        if (supplyData != null){
            try {
                supplyLiveData = DagasJSONServer.getDetail("/relief/api/supplies/", supplyData.getSupplyId());
            } catch (Exception e) {
                e.printStackTrace();
            }
            supplyName.setText(supplyData.getName());
            if (supplyLiveData != null) {
                editNumberQuantity.setText(String.valueOf(supplyLiveData.optInt("quantity")));
                editNumberPax.setText(String.valueOf(supplyLiveData.optInt("pax")));
                editDonationId = supplyLiveData.optInt("donation");
            }
            spinnerType.setSelection(thread.getTypes().indexOf(supplyData.getType()));
        }

        // Upload image button
        Button takeSupplyPictureButton = root.findViewById(R.id.takeSupplyPictureButton);
        File photoFile = null;
        ImageAssistor assistor = new ImageAssistor(this.getActivity());
        try {
            photoFile = assistor.createImageFile();
        } catch (IOException e) {
            e.printStackTrace();
        }
        final File[] finalPhotoFile = {photoFile};

        ActivityResultLauncher<Uri> mGetContent = registerForActivityResult(new ActivityResultContracts.TakePicture(),
                new ActivityResultCallback<Boolean>() {
                    @Override
                    public void onActivityResult(Boolean result) {
                        if (result) {
                            Bitmap idBitMap = BitmapFactory.decodeFile(finalPhotoFile[0].getAbsolutePath());
                        }
                        //TODO: Add placeholder for image
//                        idImageView.setImageBitmap(idBitMap);
                    }
                });
        takeSupplyPictureButton.setOnClickListener(view -> {
            // Continue only if the File was successfully created
            Uri photoURI = getUriForFile(DonorAddSupply.this.requireContext(),
                    "com.example.android.fileprovider",
                    finalPhotoFile[0]);
            mGetContent.launch(photoURI);
        });

        // Add supply button
        Button supplySubmitButton = root.findViewById(R.id.supplySubmitButton);

        ViewSupplyAdapter.ViewSupply finalSupplyData = supplyData;
        int finalEditDonationId = editDonationId;
        supplySubmitButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    //action_nav_donor_add_supply_to_nav_view_supplies
                    //TODO: Check for blanks
                    if (finalSupplyData == null) {
                        SupplyAddThread supplyThread = new SupplyAddThread(thread.getDonationID(),
                                supplyName.getText().toString(),
                                Integer.parseInt(editNumberQuantity.getText().toString()),
                                Integer.parseInt(editNumberPax.getText().toString()), spinnerType.getSelectedItemPosition());
                        supplyThread.start();
                        supplyThread.join();
                        Toast.makeText(DonorAddSupply.this.getContext(),"Added " + supplyThread.getResponseSupplyName() + "!",
                                Toast.LENGTH_SHORT).show();
                        if (finalPhotoFile[0].exists())
                            DagasJSONServer.uploadWithPut(DagasJSONServer.createDetailUrl(
                                    "/relief/api/supplies/",
                                    supplyThread.getResponseSupplyId()) + "upload_picture/", finalPhotoFile[0]);
                    } else{
                        // if editing supply
                        JSONObject supplyEdit = new JSONObject();
                        supplyEdit.put("name", supplyName.getText().toString());
                        supplyEdit.put("quantity", Integer.parseInt(editNumberQuantity.getText().toString()));
                        supplyEdit.put("pax", Integer.parseInt(editNumberPax.getText().toString()));
                        supplyEdit.put("type", spinnerType.getSelectedItemPosition() + 1);
                        supplyEdit.put("donation", finalEditDonationId);
                        DagasJSONServer.putDetail("/relief/api/supplies/", finalSupplyData.getSupplyId(), supplyEdit);
                        //action_nav_donor_add_supply_to_nav_view_supplies
                        Navigation.findNavController(view).navigate(R.id.action_nav_donor_add_supply_to_nav_view_supplies);

                    }

                    supplyName.getText().clear();
                    editNumberPax.getText().clear();
                    editNumberQuantity.getText().clear();
                    spinnerType.setSelection(0);

                } catch (JSONException | InterruptedException e) {
                    Log.e(TAG, e.getMessage());
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
        return root;

    }
}