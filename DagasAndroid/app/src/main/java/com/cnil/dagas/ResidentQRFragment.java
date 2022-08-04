package com.cnil.dagas;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.RatingBar;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.fragment.app.Fragment;

import com.cnil.dagas.databinding.ResidentQrBinding;
import com.cnil.dagas.http.DagasJSONServer;
import com.cnil.dagas.ui.home.resident.EvacuationVisualMapFragment;
import com.squareup.picasso.Picasso;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

public class ResidentQRFragment extends Fragment {
    private ResidentQrBinding binding;
    private String TAG = ResidentQRFragment.class.getName();
    public ResidentQRFragment() {
        // Required empty public constructor
    }
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = ResidentQrBinding.inflate(inflater, container, false);
        ImageView qrCodeImageView = binding.residentQrCodeImageView;

        Spinner evacuationCenterSelector = binding.evacuationCenterSelector;
        RatingBar ratingBar = binding.ratingBar;
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
            String name = null;
            try {
                name = center.getString("name");

            } catch (JSONException e) {
                Log.e(TAG, e.getMessage());
            }
            adapter.add(name);
        }
        evacuationCenterSelector.setAdapter(adapter);
        evacuationCenterSelector.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {
                try {
                    JSONArray stubList = DagasJSONServer.getList("/relief/api/stubs/?request__evacuation_center__name="
                            + evacuationCenterSelector.getSelectedItem());
                    if (stubList.length() > 0){
                        JSONObject stubObject = stubList.getJSONObject(0);
                        if (stubObject != null){
                            String qrURL = stubObject.getString("qr_code");
                            Picasso.with(getContext()).load(qrURL)
                                    .into(qrCodeImageView);
                        } else{
                            Toast.makeText(ResidentQRFragment.this.getContext(),
                                    "No QR available for this evacuation center",
                                    Toast.LENGTH_SHORT).show();
                        }
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> adapterView) {

            }
        });

        ratingBar.setOnRatingBarChangeListener(new RatingBar.OnRatingBarChangeListener() {
            @Override
            public void onRatingChanged(RatingBar ratingBar, float v, boolean b) {
                int rating = (int) v;
                JSONObject ratingObject = new JSONObject();
                try {
                    ratingObject.put("value", rating);
                } catch (JSONException e) {
                    Log.e(TAG, e.getMessage());
                }
                try {
                    DagasJSONServer.put("/relief/api/ratings/rate/", ratingObject);
                } catch (Exception e) {
                    Log.e(TAG, e.getMessage());
                }
            }
        });
        return binding.getRoot();
    }
}
