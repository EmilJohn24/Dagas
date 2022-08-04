package com.cnil.dagas;

import static androidx.core.content.FileProvider.getUriForFile;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import android.content.Intent;
import android.os.Bundle;

import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.fragment.app.Fragment;

import com.cnil.dagas.data.ImageAssistor;
import com.cnil.dagas.data.CurrentUserThread;
import com.cnil.dagas.data.ResidentRegisterActivity;
import com.cnil.dagas.databinding.UserProfileBinding;
import com.cnil.dagas.http.DagasJSONServer;
import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.ui.login.LoginActivity;
import com.squareup.picasso.Picasso;

import org.json.JSONException;

import java.io.File;
import java.io.IOException;

public class UserProfileFragment extends Fragment {
    private final String TAG = UserProfileFragment.class.getName();
    public UserProfileFragment(){
        // Required empty public constructor
    }
    UserProfileBinding binding;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = UserProfileBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        ImageView profilePictureImageView = root.findViewById(R.id.profile_picture);
        TextView fullNameTxt = root.findViewById(R.id.full_name);
        TextView emailTxt = root.findViewById(R.id.email);
        //TextView barangayTxt = root.findViewById(R.id.barangay);
        TextView roleTxt = root.findViewById(R.id.role);
        Button selectProfilePic = root.findViewById(R.id.select_profile_picture);
        Button uploadProfilePic = root.findViewById(R.id.upload_profle_pic);

        //Load current user data
        CurrentUserThread currentUserThread = new CurrentUserThread();
        currentUserThread.start();
        try {
            currentUserThread.join();
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }
        String roleVerbose = null;
        try {
             roleVerbose = currentUserThread.getUser().getString("role");
             if(roleVerbose.equals("1")){
                 roleVerbose = "Resident";
             }
             else if(roleVerbose.equals("2")){
                 roleVerbose = "Donor";
             }
             else if(roleVerbose.equals("3")){
                 roleVerbose = "Barangay";
             }
             else if(roleVerbose.equals("4")){
                 roleVerbose = "Admin";
             }
             else{
                 roleVerbose = "Resident";
             }
        } catch (JSONException e) {
            e.printStackTrace();
        }

        try {
            String baseUrl = OkHttpSingleton.getInstance().getBaseUrl();
            fullNameTxt.setText("Full Name: " + currentUserThread.getUser().getString("last_name") + ", " + currentUserThread.getUser().getString("first_name"));
            emailTxt.setText("Email: " + currentUserThread.getUser().getString("email"));
            roleTxt.setText("Role: " + roleVerbose);
            Picasso.with(this.getContext()).load(baseUrl + currentUserThread
                    .getUser().getString("profile_picture"))
                    .into(profilePictureImageView);
        } catch (JSONException e) {
            Log.e(TAG, e.getMessage());
        }

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
        selectProfilePic.setOnClickListener(view -> {
            // Continue only if the File was successfully created
            Uri photoURI = getUriForFile(UserProfileFragment.this.requireContext(),
                    "com.example.android.fileprovider",
                    finalPhotoFile[0]);
            mGetContent.launch(photoURI);
            uploadProfilePic.setEnabled(true);
        });
        uploadProfilePic.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    if (finalPhotoFile[0].exists())
                        DagasJSONServer.uploadWithPut(
                                "/relief/api/users/upload_profile_picture/", finalPhotoFile[0]);

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