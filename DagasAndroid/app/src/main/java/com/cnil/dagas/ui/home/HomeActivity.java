package com.cnil.dagas.ui.home;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.drawerlayout.widget.DrawerLayout;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;

import com.cnil.dagas.R;
import com.cnil.dagas.data.CurrentUserThread;
import com.cnil.dagas.data.DisasterListThread;
import com.cnil.dagas.data.DisasterUpdateThread;
import com.cnil.dagas.databinding.ActivityHomeBinding;
import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.services.location.LocationService;
import com.cnil.dagas.services.notifications.DagasNotificationService;
import com.cnil.dagas.ui.login.LoginActivity;
import com.google.android.material.navigation.NavigationView;
import com.squareup.picasso.Picasso;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;


public class HomeActivity extends AppCompatActivity {

    private AppBarConfiguration mAppBarConfiguration;
    private ActivityHomeBinding binding;
    private final String TAG = HomeActivity.class.getName();
    public void updateProfilePicture(Uri imagePath){
        NavigationView navigationView = binding.navView;
        ImageView profilePictureImageView = (ImageView) navigationView.getHeaderView(0).findViewById(R.id.profilePictureImageView);
        profilePictureImageView.setImageURI(imagePath);
        //        profilePictureImageView.setImage
    }
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // TODO: Check permissions here
        binding = ActivityHomeBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        setSupportActionBar(binding.appBarHome.toolbar);
//        binding.appBarResident.fab.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View view) {
//                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
//                        .setAction("Action", null).show();
//            }
//        });
        startService(new Intent(this, LocationService.class));
        startService(new Intent(this, DagasNotificationService.class));
        DrawerLayout drawer = binding.drawerLayout;
        NavigationView navigationView = binding.navView;
        TextView nameTxt = (TextView) navigationView.getHeaderView(0).findViewById(R.id.nameTxt);
        TextView emailTxt = (TextView) navigationView.getHeaderView(0).findViewById(R.id.emailTxt);
        TextView roleTxt = (TextView) navigationView.getHeaderView(0).findViewById(R.id.roleTxt);
        ImageView profilePictureImg = (ImageView) navigationView.getHeaderView(0).findViewById(R.id.profilePictureImageView);

        //Load current user data
        CurrentUserThread currentUserThread = new CurrentUserThread();
        currentUserThread.start();
        try {
            currentUserThread.join();
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }
        //nav drawer filter [role]
        Set<Integer> topLevelDestinations = new HashSet<>();
        String roleVerbose = null;
        try {
            roleVerbose = currentUserThread.getUser().getString("role");
            if(roleVerbose.equals("1")){
                roleVerbose = "Resident";
                topLevelDestinations.add(R.id.nav_home);
                topLevelDestinations.add(R.id.nav_transactions);
                topLevelDestinations.add(R.id.nav_upload_id);
                topLevelDestinations.add(R.id.nav_user_profile);
                navigationView.getMenu().findItem(R.id.nav_barangay_request).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_view_requests).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_view_supplies).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_donor_add_supply).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_suggestions).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_calamity_tip_fragment).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_qr_scanner).setVisible(false);
            }
            else if(roleVerbose.equals("2")){
                roleVerbose = "Donor";
                topLevelDestinations.add(R.id.nav_home);
                topLevelDestinations.add(R.id.nav_user_profile);
                topLevelDestinations.add(R.id.nav_view_requests);
                topLevelDestinations.add(R.id.nav_view_supplies);
                topLevelDestinations.add(R.id.nav_transactions);
                topLevelDestinations.add(R.id.nav_donor_add_supply);
                navigationView.getMenu().findItem(R.id.nav_barangay_request).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_upload_id).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_res_qr).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_qr_scanner).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_calamity_tip_fragment).setVisible(false);
            }
            else if(roleVerbose.equals("3")){
                roleVerbose = "Barangay";
                topLevelDestinations.add(R.id.nav_home);
                topLevelDestinations.add(R.id.nav_qr_scanner);
                topLevelDestinations.add(R.id.nav_user_profile);
                topLevelDestinations.add(R.id.nav_view_requests);
                topLevelDestinations.add(R.id.nav_transactions);
                topLevelDestinations.add(R.id.nav_barangay_request);
                navigationView.getMenu().findItem(R.id.nav_donor_add_supply).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_view_supplies).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_upload_id).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_suggestions).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_res_qr).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_calamity_tip_fragment).setVisible(false);

            }
            else if(roleVerbose.equals("4")){
                roleVerbose = "Admin";
            }
            else{
                roleVerbose = "Resident";
                topLevelDestinations.add(R.id.nav_home);
                topLevelDestinations.add(R.id.nav_barangay_request);
                topLevelDestinations.add(R.id.nav_view_requests);
                topLevelDestinations.add(R.id.nav_view_supplies);
                topLevelDestinations.add(R.id.nav_transactions);
                topLevelDestinations.add(R.id.nav_upload_id);
                topLevelDestinations.add(R.id.nav_user_profile);
                navigationView.getMenu().findItem(R.id.nav_donor_add_supply).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_suggestions).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_qr_scanner).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_calamity_tip_fragment).setVisible(false);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
        try {
            String baseUrl = OkHttpSingleton.getInstance().getBaseUrl();
            nameTxt.setText(currentUserThread.getUser().getString("username"));
            emailTxt.setText(currentUserThread.getUser().getString("email"));
            roleTxt.setText("Role: " + roleVerbose);
            Picasso.with(this).load("" + currentUserThread
                    .getUser().getString("profile_picture"))
                    .into(profilePictureImg);
        } catch (JSONException e) {
            Log.e(TAG, e.getMessage());
        }
        // Disaster Spinner loader
        if (roleVerbose.equals("Donor")) {
            DisasterListThread disasterListThread = new DisasterListThread();
            disasterListThread.start();
            try {
                disasterListThread.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            JSONArray disasterJSONArray = disasterListThread.getDisasterJSONArray();
            Map<String, Integer> disasterIDs = new HashMap<>();
            disasterIDs.put(" ", DisasterUpdateThread.NONE);
            for (int i = 0; i != disasterJSONArray.length(); i++) {
                try {
                    JSONObject disasterJSON = disasterJSONArray.getJSONObject(i);
                    disasterIDs.put(disasterJSON.getString("name"), disasterJSON.getInt("id"));
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
            Spinner disasterSpinner = (Spinner) navigationView.getHeaderView(0).findViewById(R.id.disasterSpinner);
            ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, android.R.layout.simple_spinner_item, new ArrayList<>(disasterIDs.keySet()));
            disasterSpinner.setAdapter(adapter);
            //TODO: Set initial selection to currently set disaster
            disasterSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
                @Override
                public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {
                    String disasterName = adapter.getItem(i);
                    Integer disasterId = disasterIDs.get(disasterName);
                    DisasterUpdateThread updateThread = new DisasterUpdateThread(disasterId);
                    updateThread.start();
                }

                @Override
                public void onNothingSelected(AdapterView<?> adapterView) {

                }
            });
        }
        else if (roleVerbose.equals("Resident") || roleVerbose.equals("Barangay")){
            Spinner disasterSpinner = (Spinner) navigationView.getHeaderView(0).findViewById(R.id.disasterSpinner);
            disasterSpinner.setEnabled(false);
            JSONObject currentDisaster = currentUserThread.getUser().optJSONObject("current_disaster");
            if (currentDisaster != null) {
                String disasterName = currentDisaster.optString("name", "Unknown");
                ArrayList<String> disasterNameContainer = new ArrayList<>();
                disasterNameContainer.add(disasterName);
                ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, android.R.layout.simple_spinner_item, disasterNameContainer);
                disasterSpinner.setAdapter(adapter);
            }

        }
        //End disaster spinner
        //End load current user data

        // Passing each menu ID as a set of Ids because each
        // menu should be considered as top level destinations.
        mAppBarConfiguration = new AppBarConfiguration.Builder(
//                R.id.nav_home, R.id.nav_qr_scanner)
                topLevelDestinations)
                .setOpenableLayout(drawer)
                .build();
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_home);
        NavigationUI.setupActionBarWithNavController(this, navController, mAppBarConfiguration);
        NavigationUI.setupWithNavController(navigationView, navController);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.home, menu);
        return true;
    }

    @SuppressLint("NonConstantResourceId")
    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        switch (item.getItemId()){
            case R.id.action_logout:
                Intent loginRedirect = new Intent(HomeActivity.this, LoginActivity.class);
                startActivity(loginRedirect);
                return true;
            case R.id.action_settings:
                //TODO: Navigate to settings
                return super.onOptionsItemSelected(item);
            default:
                return super.onOptionsItemSelected(item);
        }
    }

    @Override
    public boolean onSupportNavigateUp() {
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_home);
        return NavigationUI.navigateUp(navController, mAppBarConfiguration)
                || super.onSupportNavigateUp();
    }
}