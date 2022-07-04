package com.cnil.dagas.ui.home;

import static androidx.camera.core.CameraX.getContext;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.media.Image;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.ImageView;
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
import com.cnil.dagas.data.ResidentRegisterActivity;
import com.cnil.dagas.databinding.ActivityHomeBinding;
import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.ui.login.LoginActivity;
import com.google.android.material.navigation.NavigationView;
import com.squareup.picasso.Picasso;

import org.json.JSONException;

import java.util.HashSet;
import java.util.Set;


public class HomeActivity extends AppCompatActivity {

    private AppBarConfiguration mAppBarConfiguration;
    private ActivityHomeBinding binding;
    private final String TAG = HomeActivity.class.getName();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

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
                topLevelDestinations.add(R.id.nav_qr_scanner);
                topLevelDestinations.add(R.id.nav_barangay_request);
                topLevelDestinations.add(R.id.nav_view_requests);
                topLevelDestinations.add(R.id.nav_view_supplies);
                topLevelDestinations.add(R.id.nav_transactions);
                topLevelDestinations.add(R.id.nav_upload_id);
                topLevelDestinations.add(R.id.nav_user_profile);
                navigationView.getMenu().findItem(R.id.nav_donor_add_supply).setVisible(false);
            }
            else if(roleVerbose.equals("2")){
                roleVerbose = "Donor";
                topLevelDestinations.add(R.id.nav_home);
                topLevelDestinations.add(R.id.nav_qr_scanner);
                topLevelDestinations.add(R.id.nav_user_profile);
                topLevelDestinations.add(R.id.nav_view_requests);
                topLevelDestinations.add(R.id.nav_view_supplies);
                topLevelDestinations.add(R.id.nav_transactions);
                topLevelDestinations.add(R.id.nav_donor_add_supply);
                navigationView.getMenu().findItem(R.id.nav_barangay_request).setVisible(false);
                navigationView.getMenu().findItem(R.id.nav_upload_id).setVisible(false);
            }
            else if(roleVerbose.equals("3")){
                roleVerbose = "Barangay";
                topLevelDestinations.add(R.id.nav_home);
                topLevelDestinations.add(R.id.nav_qr_scanner);
                topLevelDestinations.add(R.id.nav_user_profile);
                topLevelDestinations.add(R.id.nav_view_requests);
                topLevelDestinations.add(R.id.nav_view_supplies);
                topLevelDestinations.add(R.id.nav_transactions);
                topLevelDestinations.add(R.id.nav_donor_add_supply);
                topLevelDestinations.add(R.id.nav_barangay_request);
                navigationView.getMenu().findItem(R.id.nav_upload_id).setVisible(false);
            }
            else if(roleVerbose.equals("4")){
                roleVerbose = "Admin";
            }
            else{
                roleVerbose = "Resident";
                topLevelDestinations.add(R.id.nav_home);
                topLevelDestinations.add(R.id.nav_qr_scanner);
                topLevelDestinations.add(R.id.nav_barangay_request);
                topLevelDestinations.add(R.id.nav_view_requests);
                topLevelDestinations.add(R.id.nav_view_supplies);
                topLevelDestinations.add(R.id.nav_transactions);
                topLevelDestinations.add(R.id.nav_upload_id);
                topLevelDestinations.add(R.id.nav_user_profile);
                navigationView.getMenu().findItem(R.id.nav_donor_add_supply).setVisible(false);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
        try {
            String baseUrl = OkHttpSingleton.getInstance().getBaseUrl();
            nameTxt.setText(currentUserThread.getUser().getString("username"));
            emailTxt.setText(currentUserThread.getUser().getString("email"));
            roleTxt.setText("Role: " + roleVerbose);
            Picasso.with(this).load(baseUrl + currentUserThread
                    .getUser().getString("profile_picture"))
                    .into(profilePictureImg);
        } catch (JSONException e) {
            Log.e(TAG, e.getMessage());
        }


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