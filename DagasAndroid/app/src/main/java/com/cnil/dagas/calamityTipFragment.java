package com.cnil.dagas;

import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;


import com.cnil.dagas.databinding.FragmentCalamityTipBinding;
import com.squareup.picasso.Picasso;
import com.synnapps.carouselview.CarouselView;
import com.synnapps.carouselview.ImageClickListener;
import com.synnapps.carouselview.ImageListener;
import com.synnapps.carouselview.ViewListener;

public class calamityTipFragment extends Fragment {
    CarouselView carouselView;
    FragmentCalamityTipBinding binding;
    int[] sampleImages = {R.drawable.tip1, R.drawable.tip2, R.drawable.tip3, R.drawable.tip4,};

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                                Bundle savedInstanceState){
    //Based on: https://lobothijau.medium.com/create-carousel-easily-in-android-app-with-carouselview-6cbf5ef500a9
        binding = FragmentCalamityTipBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        super.onCreate(savedInstanceState);

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
