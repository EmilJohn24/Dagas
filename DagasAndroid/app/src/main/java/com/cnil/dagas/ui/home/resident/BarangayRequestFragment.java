package com.cnil.dagas.ui.home.resident;

import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.Spinner;

import com.cnil.dagas.R;
import com.cnil.dagas.data.model.LoggedInUser;
import com.cnil.dagas.databinding.FragmentBarangayRequestBinding;
import com.cnil.dagas.databinding.QrScannerBinding;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class BarangayRequestFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
//    private static final String ARG_PARAM1 = "param1";
//    private static final String ARG_PARAM2 = "param2";
//
//    // TODO: Rename and change types of parameters
//    private String mParam1;
//    private String mParam2;
    private static final String TAG = BarangayRequestFragment.class.getName();

    public BarangayRequestFragment() {
        // Required empty public constructor
    }
    class AddBarangayRequestThread extends Thread{
        private static final String ADD_URL = "/relief/api/requests/";
        private static final String ADD_ITEM_URL = "/relief/api/item-request/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        private JSONObject response; // Returns JSON data if successfully added
        //TODO: Add date required
        //TODO: Fix hardcoded amounts in the future (use ItemType table in server-side)
        private final int foodAmount, waterAmount, clothesAmount;
        private final boolean foodChecked, waterChecked, clothesChecked;
        private final int evacuationCenterId;
        AddBarangayRequestThread(int foodAmount, boolean foodChecked,
                                 int waterAmount, boolean waterChecked,
                                 int clothesAmount, boolean clothesChecked,
                                 int evacuationCenterId){
            this.foodAmount = foodAmount;
            this.waterAmount = waterAmount;
            this.clothesAmount = clothesAmount;
            this.foodChecked = foodChecked;
            this.waterChecked = waterChecked;
            this.clothesChecked = clothesChecked;
            this.evacuationCenterId = evacuationCenterId;
        }

        public void run(){
            try {
                response = addBarangayRequest();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }

        private JSONObject addBarangayRequest() throws IOException, JSONException {
            JSONObject createRequestJSON = new JSONObject();
            // JSON Form Handling:
            // https://stackoverflow.com/questions/17810044/android-create-json-array-and-json-object
            // https://stackoverflow.com/questions/23456488/how-to-use-okhttp-to-make-a-post-request
            // https://stackoverflow.com/questions/34179922/okhttp-post-body-as-json
            try {
                //TODO: Add date required
               createRequestJSON.put("evacuation_center", this.evacuationCenterId);
            } catch (JSONException e) {
                Log.e(TAG, e.getMessage());
            }

            OkHttpSingleton client = OkHttpSingleton.getInstance();
            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(ADD_URL)
                    .post(body)
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONObject responseJSON = new JSONObject(response.body().string());

            //ID for Barangay request
            int barangayRequestID = responseJSON.getInt("id");


            // Food request

            if (this.foodChecked){
                JSONObject foodRequestJSON = new JSONObject();
                try {
                    //TODO: Add date created
                    foodRequestJSON.put("type", 1);
                    foodRequestJSON.put("pax", this.foodAmount);
                    foodRequestJSON.put("barangay_request", barangayRequestID);
                    RequestBody foodRequestBody = RequestBody.create(foodRequestJSON.toString(), JSON);
                    Request foodRequest = client.builderFromBaseUrl(ADD_ITEM_URL)
                                            .post(foodRequestBody).build();
                    Response foodResponse = client.newCall(foodRequest).execute();


                } catch (JSONException e) {
                    Log.e(TAG, e.getMessage());
                }
            }

            if (this.waterChecked){
                JSONObject waterRequestJSON = new JSONObject();
                try {
                    //TODO: Add date created
                    waterRequestJSON.put("type", 2);
                    waterRequestJSON.put("pax", this.waterAmount);
                    waterRequestJSON.put("barangay_request", barangayRequestID);
                    RequestBody waterRequestBody = RequestBody.create(waterRequestJSON.toString(), JSON);
                    Request waterRequest = client.builderFromBaseUrl(ADD_ITEM_URL)
                            .post(waterRequestBody).build();
                    Response waterResponse = client.newCall(waterRequest).execute();


                } catch (JSONException e) {
                    Log.e(TAG, e.getMessage());
                }
            }

            if (this.clothesChecked){
                JSONObject clothesRequestJSON = new JSONObject();
                try {
                    //TODO: Add date created
                    clothesRequestJSON.put("type", 3);
                    clothesRequestJSON.put("pax", this.clothesAmount);
                    clothesRequestJSON.put("barangay_request", barangayRequestID);
                    RequestBody clothesRequestBody = RequestBody.create(clothesRequestJSON.toString(), JSON);
                    Request clothesRequest = client.builderFromBaseUrl(ADD_ITEM_URL)
                            .post(clothesRequestBody).build();
                    Response clothesResponse = client.newCall(clothesRequest).execute();


                } catch (JSONException e) {
                    Log.e(TAG, e.getMessage());
                }
            }
            return responseJSON;
        }
    }
    FragmentBarangayRequestBinding binding;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentBarangayRequestBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        //TODO: Modify hardcoded parts
        EditText foodAmountEdit = root.findViewById(R.id.foodNumber);
        CheckBox foodCheckbox = root.findViewById(R.id.foodCheck);
        EditText waterAmountEdit = root.findViewById(R.id.waterNumber);
        CheckBox waterCheckbox = root.findViewById(R.id.waterCheck);
        EditText clothesAmountEdit = root.findViewById(R.id.clothesNumber);
        CheckBox clothesCheckbox = root.findViewById(R.id.clothesCheck);

        Button submitButton = root.findViewById(R.id.submitButton);
        Spinner evacSpinner = root.findViewById(R.id.evacSpinner);

        EvacuationVisualMapFragment.GrabEvacsThread thread = new EvacuationVisualMapFragment.GrabEvacsThread();
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }
        ArrayList<JSONObject> centers = thread.getCenters();
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this.getContext(), android.R.layout.simple_spinner_item);

        for (JSONObject center : centers){
            try {
                String name = center.getString("name");
                adapter.add(name);
            } catch (JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }

        evacSpinner.setAdapter(adapter);

        submitButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                int foodAmount =Integer.parseInt(foodAmountEdit.getText().toString());
                boolean foodChecked = foodCheckbox.isChecked();

                int waterAmount = Integer.parseInt(waterAmountEdit.getText().toString());
                boolean waterChecked = waterCheckbox.isChecked();

                int clothesAmount = Integer.parseInt(clothesAmountEdit.getText().toString());
                boolean clothesChecked = clothesCheckbox.isChecked();

                //TODO: Link water and clothes amount
                AddBarangayRequestThread thread = null;
                try {
                    thread = new AddBarangayRequestThread(foodAmount, foodChecked,
                            waterAmount, waterChecked,
                            clothesAmount, clothesChecked,
                            centers.get(evacSpinner.getSelectedItemPosition()).getInt("id"));
                } catch (JSONException e) {
                    Log.e(TAG, e.getMessage());
                }
                assert thread != null;
                thread.start();
                try {
                    thread.join();
                } catch (InterruptedException e) {
                    Log.e(TAG, e.getMessage());
                }

            }
        });
        // Do shit

        return root;
    }
}