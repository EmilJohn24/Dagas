package com.cnil.dagas.data;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.cnil.dagas.R;
import com.cnil.dagas.databinding.ActivityResidentRegisterBinding;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class ResidentRegisterActivity extends AppCompatActivity {
    private Button registerButton;
    private ActivityResidentRegisterBinding binding;


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

        registerButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Thread registerThread = new Thread(new Runnable() {
                    private String REGISTER_URL = "/api/rest-auth/registration";
                    private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
                    @Override
                    public void run() {
                        JSONObject registerJSON = new JSONObject();
                        try {
                            registerJSON.put("username", usernameTxt.getText());
                            registerJSON.put("email", emailTxt.getText());
                            registerJSON.put("password1", passwordTxt.getText());
                            registerJSON.put("password2", confirmPasswordTxt.getText());
                            registerJSON.put("first_name", firstNameTxt.getText());
                            registerJSON.put("last_name", lastNameTxt.getText());
                            registerJSON.put("role", 1);
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                        OkHttpSingleton client = OkHttpSingleton.getInstance();
                        RequestBody body = RequestBody.create(registerJSON.toString(), JSON);
                        Request request = client.builderFromBaseUrl(REGISTER_URL)
                                .post(body)
                                .build();
                        try {
                            Response response = client.newCall(request).execute();
                            int a = 3;
                        } catch (IOException e) {
                            e.printStackTrace();
                        }


                    }
                });


                try {
                    registerThread.start();
                    registerThread.join();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                Toast.makeText(ResidentRegisterActivity.this, "Registration complete", Toast.LENGTH_SHORT).show();
            }
        });
    }
}