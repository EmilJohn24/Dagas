package com.cnil.dagas;

import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;


import com.cnil.dagas.data.CurrentUserThread;
import com.cnil.dagas.data.DisasterListThread;
import com.cnil.dagas.data.DisasterUpdateThread;
import com.cnil.dagas.databinding.FragmentCalamityTipBinding;
import com.squareup.picasso.Picasso;
import com.synnapps.carouselview.CarouselView;
import com.synnapps.carouselview.ImageClickListener;
import com.synnapps.carouselview.ImageListener;
import com.synnapps.carouselview.ViewListener;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class CalamityTipFragment extends Fragment {
    CarouselView carouselView;
    FragmentCalamityTipBinding binding;
    int[] sampleImages = {R.drawable.tip1, R.drawable.tip2, R.drawable.tip3, R.drawable.tip4, R.drawable.tip5,};

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                                Bundle savedInstanceState){
    //Based on: https://lobothijau.medium.com/create-carousel-easily-in-android-app-with-carouselview-6cbf5ef500a9
        binding = FragmentCalamityTipBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        super.onCreate(savedInstanceState);
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
        Spinner calamitySpinner = root.findViewById(R.id.calamitySpinner);
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(getActivity(), android.R.layout.simple_spinner_item, new ArrayList<>(disasterIDs.keySet()));
        calamitySpinner.setAdapter(adapter);
        //TODO: Set initial selection to currently set disaster
        calamitySpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
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

        carouselView = binding.carouselView;
        carouselView.setPageCount(sampleImages.length);
        carouselView.setImageListener(imageListener);
        carouselView.setImageClickListener(new ImageClickListener() {
            @Override
            public void onClick(int position) {
                if (position == 3)
                    Navigation.findNavController(root).navigate(R.id.action_nav_calamity_tip_fragment_to_nav_home);
            }
        });
        return root;
    }

    ImageListener imageListener = new ImageListener() {
        @Override
        public void setImageForPosition(int position, ImageView imageView) {
            imageView.setImageResource(sampleImages[position]);
        }
    };


}
