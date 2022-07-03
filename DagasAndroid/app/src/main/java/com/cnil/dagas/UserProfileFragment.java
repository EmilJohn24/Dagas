package com.cnil.dagas;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.fragment.app.Fragment;


import com.cnil.dagas.data.CurrentUserThread;
import com.cnil.dagas.databinding.UserProfileBinding;
import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.ui.home.HomeActivity;
import com.squareup.picasso.Picasso;

import org.json.JSONException;

public class UserProfileFragment extends Fragment {

    private final String TAG = UserProfileFragment.class.getName();
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

        return root;
    }
}