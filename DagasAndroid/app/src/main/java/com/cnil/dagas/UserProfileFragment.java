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
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;

import com.cnil.dagas.data.CurrentUserThread;
import com.cnil.dagas.data.ImageAssistor;
import com.cnil.dagas.databinding.FragmentCalamityTipBinding;
import com.cnil.dagas.databinding.UserProfileBinding;
import com.cnil.dagas.http.DagasJSONServer;
import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.ui.home.HomeActivity;
import com.squareup.picasso.Picasso;
import com.synnapps.carouselview.CarouselView;
import com.synnapps.carouselview.ImageClickListener;
import com.synnapps.carouselview.ImageListener;

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
        CarouselView carouselView;
        int[] sampleImages = { R.drawable.tip3, R.drawable.tip1, R.drawable.tip2, R.drawable.tip4, R.drawable.tip5,};
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
        int role = 0;
        String roleVerbose = "";
        try {
            role = currentUserThread.getUser().getInt("role");
            carouselView = binding.carouselView;
             if(role == 1){
                 roleVerbose = "Resident";
                 carouselView.setVisibility(View.GONE);
             }
             else if(role == 2){
                 roleVerbose = "Donor";
                 carouselView.setVisibility(View.VISIBLE);
                 carouselView.setPageCount(sampleImages.length);
                 ImageListener imageListener = new ImageListener() {
                     @Override
                     public void setImageForPosition(int position, ImageView imageView) {
                         imageView.setImageResource(sampleImages[position]);
                     }
                 };
                 carouselView.setImageListener(imageListener);
                 carouselView.setImageClickListener(new ImageClickListener() {
                     @Override
                     public void onClick(int position) {
                         if (position == 3)
                             Navigation.findNavController(root).navigate(R.id.action_nav_calamity_tip_fragment_to_nav_home);
                     }
                 });
             }
             else if(role == 3){
                 roleVerbose = "Barangay";
                 carouselView.setVisibility(View.GONE);
             }
             else if(role == 4){
                 roleVerbose = "Admin";
                 carouselView.setVisibility(View.GONE);
             }
             else{
                 roleVerbose = "Resident";
                 carouselView.setVisibility(View.GONE);
             }
        } catch (JSONException e) {
            e.printStackTrace();
        }

        try {
            String baseUrl = OkHttpSingleton.getInstance().getBaseUrl();
            fullNameTxt.setText(String.format("%s, %s", currentUserThread.getUser().optString("last_name"), currentUserThread.getUser().optString("first_name")));
            emailTxt.setText(currentUserThread.getUser().getString("email"));
            roleTxt.setText(roleVerbose);
//            Picasso.with(this.getContext()).load("" + currentUserThread
//                    .getUser().getString("profile_picture"))
//                    .into(profilePictureImageView);
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
        final Uri[] photoURI = {null};
        selectProfilePic.setOnClickListener(view -> {
            // Continue only if the File was successfully created
             photoURI[0] = getUriForFile(UserProfileFragment.this.requireContext(),
                    "com.example.android.fileprovider",
                    finalPhotoFile[0]);
            mGetContent.launch(photoURI[0]);
            uploadProfilePic.setEnabled(true);
        });
        uploadProfilePic.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    if (finalPhotoFile[0].exists()) //only refreshes the image once
                        DagasJSONServer.uploadWithPut( //TODO add server response check
                                "/relief/api/users/upload_profile_picture/", finalPhotoFile[0]);
                        HomeActivity homeActivity = (HomeActivity) getActivity();
//                        profilePictureImageView.setImageURI(photoURI[0]);
                        if (homeActivity != null)
                            homeActivity.updateProfilePicture(photoURI[0]);
                        Toast.makeText(UserProfileFragment.this.getContext(),"Uploaded successfully!",
                            Toast.LENGTH_SHORT).show();

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