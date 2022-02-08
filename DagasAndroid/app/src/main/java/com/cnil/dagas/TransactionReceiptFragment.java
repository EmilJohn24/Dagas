package com.cnil.dagas;

import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import com.cnil.dagas.databinding.FragmentTransactionReceiptBinding;
import com.cnil.dagas.http.OkHttpSingleton;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapView;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;
import com.squareup.picasso.Picasso;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.Request;
import okhttp3.Response;


public class TransactionReceiptFragment extends Fragment  implements OnMapReadyCallback {
    static private final String TAG = TransactionReceiptFragment.class.getName();



    public static class RetrieveTransactionInfo extends Thread{
        private String transactionURL;
        private JSONObject transactionJSON;
        private JSONObject evacuationCenterJSON;

        public RetrieveTransactionInfo(String transactionURL) {
            this.transactionURL = transactionURL;
        }

        public void run(){
            try {
                retrieveTransaction();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }

        void retrieveTransaction() throws IOException, JSONException{
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(transactionURL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            this.transactionJSON = new JSONObject(response.body().string());


            Request evacuationCenterRequest = client.builderFromBaseUrl(transactionURL + "evacuation_center/")
                    .get()
                    .build();
            Response evacuationCenterResponse = client.newCall(evacuationCenterRequest).execute();

            this.evacuationCenterJSON = new JSONObject(evacuationCenterResponse.body().string());
        }

        public JSONObject getTransactionJSON() {
            return transactionJSON;
        }

        public JSONObject getEvacuationCenterJSON() {
            return evacuationCenterJSON;
        }
    }

    public TransactionReceiptFragment() {
        // Required empty public constructor
    }

    private MapView evacuationCenterMapView;
    private GoogleMap map;
    FragmentTransactionReceiptBinding binding;


    @Override
    public void onMapReady(@NonNull GoogleMap googleMap) {
        map = googleMap;
        View root = binding.getRoot();
        assert getArguments() != null;
        String transactionURL = getArguments().getString("TRANSACTION_URL");
        //TODO: Implement mapview and recyclerview
        //TODO: Add transaction status
        evacuationCenterMapView = root.findViewById(R.id.evacMapView);
        ImageView qrCodeImageView = root.findViewById(R.id.qrCodeImageView);
        TextView referenceNumberTextView = root.findViewById(R.id.referenceNumberTextView);
        TextView donorNameTextView = root.findViewById(R.id.donorNameTextView);
        RetrieveTransactionInfo thread = new RetrieveTransactionInfo(transactionURL);
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        try {
            String qrURL = thread.getTransactionJSON().getString("qr_code");
            Picasso.with(getContext()).load(qrURL)
                    .into(qrCodeImageView);
            referenceNumberTextView.setText(thread.getTransactionJSON().getString("id"));
            donorNameTextView.setText(thread.getTransactionJSON().getString("donor_name"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        // TODO: Convert to function (See EvacuationVisualMapFragment.java)
        JSONObject evacuationCenterJSON = thread.getEvacuationCenterJSON();
        try {
            String coord = evacuationCenterJSON.getString("geolocation");
            String name = evacuationCenterJSON.getString("name");
            String[] splitCoord = coord.split(",");
            double latitude = Float.parseFloat(splitCoord[0]);
            double longtitude = Float.parseFloat(splitCoord[1]);
            LatLng evacLatLng = new LatLng(latitude, longtitude);

            map.addMarker(new MarkerOptions()
                            .position(evacLatLng)
                            .title(name));
            map.animateCamera(CameraUpdateFactory.newLatLngZoom(evacLatLng, 20));
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        View root = binding.getRoot();
        evacuationCenterMapView = root.findViewById(R.id.evacMapView);
        evacuationCenterMapView.onCreate(savedInstanceState);
        evacuationCenterMapView.onResume();
        evacuationCenterMapView.getMapAsync(this);
    }
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentTransactionReceiptBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }
}