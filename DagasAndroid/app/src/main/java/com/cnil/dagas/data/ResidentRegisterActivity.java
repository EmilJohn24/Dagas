package com.cnil.dagas.data;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import com.cnil.dagas.R;
import com.cnil.dagas.databinding.ActivityResidentRegisterBinding;
import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.ui.login.LoginActivity;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import okhttp3.MediaType;
import okhttp3.OkHttp;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class ResidentRegisterActivity extends AppCompatActivity {
    private Button registerButton;
    private ActivityResidentRegisterBinding binding;
    private Response response;
    private static final String TAG = ResidentRegisterActivity.class.getName();
    //thread that gets the list of username
    public static class GrabUsers extends Thread {
        private static final String USER_URL = "/relief/api/users/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");


        private final ArrayList<String> UserNames;


        public GrabUsers() {
            UserNames = new ArrayList<>();
        }



        public void run() {
            try {
                GrabUsers();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void GrabUsers() throws IOException, JSONException {
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrlAnon(USER_URL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONArray userJSONArray = new JSONArray(response.body().string());
            for (int i = 0; i < userJSONArray.length(); i++) {
                JSONObject userJSONObject = userJSONArray.getJSONObject(i);
                this.UserNames.add(userJSONObject.getString("username"));
            }

            //TODO: Check for errors

        }
        public ArrayList<String> getUserNames() {
            return UserNames;
        }
    }

    public static class GrabBarangays extends Thread {
        private static final String BARANGAY_URL = "/relief/api/users/barangays/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");


        private final ArrayList<String> barangayNames;
        private final Map<String, Integer> barangayIds;
        private JSONObject donationAddResponse;

        public GrabBarangays() {

            barangayNames = new ArrayList<>();
            barangayIds = new HashMap<>();
        }



        public void run() {
            try {
                grabBarangays();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void grabBarangays() throws IOException, JSONException {
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrlAnon(BARANGAY_URL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONArray barangayJSONArray = new JSONArray(response.body().string());
            for (int i = 0; i < barangayJSONArray.length(); i++) {
                JSONObject barangayJSONObject = barangayJSONArray.getJSONObject(i);
                this.barangayNames.add(barangayJSONObject.getString("user"));
                this.barangayIds.put(barangayJSONObject.getString("user"), barangayJSONObject.getInt("id"));
            }

            //TODO: Check for errors

        }
        public ArrayList<String> getBarangayNames() {
            return barangayNames;
        }

        public Map<String, Integer> getBarangayIds() {
            return barangayIds;
        }
    }
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityResidentRegisterBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        final Button registerButton = binding.registerButton;
        final EditText usernameTxt = binding.usernameTxt;
        final EditText emailTxt = binding.emailTxt;
        final EditText passwordTxt = binding.passwordTxt;
        final EditText confirmPasswordTxt = binding.confirmPasswordTxt;
        final EditText firstNameTxt = binding.firstNameTxt;
        final EditText lastNameTxt = binding.lastNameTxt;
        final Spinner barangaySpinner = binding.barangaySpinner;
        final CheckBox residentCheckBox = binding.residentCheckBox;
        final CheckBox donorCheckBox = binding.donorCheckBox;
        GrabBarangays thread = new GrabBarangays();
        GrabUsers userThread = new GrabUsers();
        thread.start();
        userThread.start();
        try {
            thread.join();
            ArrayAdapter<String> barangayAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item,
                                                    thread.getBarangayNames());
            barangaySpinner.setAdapter(barangayAdapter);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        try {
            userThread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        //Added text watcher to avoid empty text field and valid password
        TextWatcher afterTextChangedListener = new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
                // ignore
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                // ignore
            }

            @Override
            public void afterTextChanged(Editable s) {
                if(usernameTxt == null || usernameTxt.getText().toString().trim().isEmpty()){
                    usernameTxt.setError("Username is required!");
                    registerButton.setEnabled(false);
                }
                else if(userThread.getUserNames().contains(usernameTxt.getText().toString().trim())){
                    usernameTxt.setError("Username is already taken!");
                    registerButton.setEnabled(false);
                }
                else if(emailTxt == null || emailTxt.getText().toString().trim().isEmpty()){
                    emailTxt.setError("Email is required!");
                    registerButton.setEnabled(false);
                }
                else if(passwordTxt == null || passwordTxt.getText().toString().trim().length() < 8){
                    passwordTxt.setError("Password length must be at least 8!");
                    registerButton.setEnabled(false);
                }
                else if(confirmPasswordTxt == null || confirmPasswordTxt.getText().toString().trim().length() < 8){
                    confirmPasswordTxt.setError("Confirm Password length must be at least 8!");
                    registerButton.setEnabled(false);
                }
                else if(!passwordTxt.getText().toString().trim().equals(confirmPasswordTxt.getText().toString().trim())){
                    confirmPasswordTxt.setError("Password does not match Confirm Password!");
                    registerButton.setEnabled(false);
                }
                else if(firstNameTxt == null || firstNameTxt.getText().toString().trim().isEmpty()){
                    firstNameTxt.setError("First name is required!");
                    registerButton.setEnabled(false);
                }
                else if(lastNameTxt == null || lastNameTxt.getText().toString().trim().isEmpty()){
                    lastNameTxt.setError("Last name is required!");
                    registerButton.setEnabled(false);
                }
                else  registerButton.setEnabled(true);
            }
        };
        usernameTxt.addTextChangedListener(afterTextChangedListener);
        passwordTxt.addTextChangedListener(afterTextChangedListener);
        confirmPasswordTxt.addTextChangedListener(afterTextChangedListener);
        emailTxt.addTextChangedListener(afterTextChangedListener);
        firstNameTxt.addTextChangedListener(afterTextChangedListener);
        lastNameTxt.addTextChangedListener(afterTextChangedListener);

        //check box checker
        residentCheckBox.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if(donorCheckBox.isChecked())
                    residentCheckBox.setChecked(false);

            }
        });
        donorCheckBox.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if(residentCheckBox.isChecked())
                    donorCheckBox.setChecked(false);
            }
        });


        registerButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Thread registerThread = new Thread(new Runnable() {
                    private final String REGISTER_URL = "/api/rest-auth/registration";
                    private final String CURRENT_USER_URL = "/relief/api/users/current_user_profile/";
                    private final String USER_DETAIL_URL = "/relief/api/users/%d/";
                    private final String RESIDENT_DETAIL_URL = "/relief/api/users/residents/r/%d/";
                    private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
                    @Override
                    public void run() {
                        JSONObject registerJSON = new JSONObject();
                        JSONObject residentRegisterJSON = new JSONObject();
                        try {
                            registerJSON.put("username", usernameTxt.getText().toString());
                            registerJSON.put("email", emailTxt.getText().toString());
                            registerJSON.put("password1", passwordTxt.getText().toString());
                            registerJSON.put("password2", confirmPasswordTxt.getText().toString());
                            registerJSON.put("first_name", firstNameTxt.getText().toString());
                            registerJSON.put("last_name", lastNameTxt.getText().toString());
                            if (residentCheckBox.isChecked()) registerJSON.put("role", 1);
                            else if (donorCheckBox.isChecked()) registerJSON.put("role", 2);
                            residentRegisterJSON.put("barangay", thread.getBarangayIds().get(
                                    barangaySpinner.getSelectedItem().toString()));
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                        OkHttpSingleton client = OkHttpSingleton.getInstance();
                        RequestBody body = RequestBody.create(registerJSON.toString(), JSON);
                        Request request = client.builderFromBaseUrlAnon(REGISTER_URL)
                                .post(body)
                                .build();
                        try {
                            response = client.newCall(request).execute();
                            if (response.code() == 201 && residentCheckBox.isChecked()){
                                client.setCredentials(usernameTxt.getText().toString(), passwordTxt.getText().toString());
                                Request currentUserRequest = client.builderFromBaseUrl(CURRENT_USER_URL).get().build();
                                JSONObject currentUserJSON = new JSONObject(client.newCall(currentUserRequest)
                                                                            .execute()
                                                                            .body()
                                                                            .string());
                                int residentId = currentUserJSON.getInt("id");
                                String residentUrl = String.format(RESIDENT_DETAIL_URL, residentId);
                                RequestBody barangayEditRequestBody = RequestBody.create(residentRegisterJSON.toString(),
                                                                                        JSON);
                                Request barangayEditRequest = client.builderFromBaseUrl(residentUrl)
                                                                    .patch(barangayEditRequestBody).build();
                                Response barangayEditResponse = client.newCall(barangayEditRequest).execute();

                            }
                        } catch (IOException | JSONException e) {
                            e.printStackTrace();
                        }


                    }
                });


                try {
                    registerThread.start();
                    registerThread.join();
                    if (response == null || response.code() != 201){ //201: CREATED
                        JSONObject errors = new JSONObject(response.body().string());
                        Iterator errorIterator = errors.keys();
                        String errorKey = (String) errorIterator.next();
                        String errorMsg = errors.getString(errorKey);
                        Toast.makeText(ResidentRegisterActivity.this, errorMsg, Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(ResidentRegisterActivity.this, "Registration complete", Toast.LENGTH_SHORT).show();
                        Intent intent = new Intent(ResidentRegisterActivity.this, LoginActivity.class);
                        startActivity(intent);
                    }
                } catch (InterruptedException | JSONException | IOException e) {
                    e.printStackTrace();
                }

            }
        });
    }
}