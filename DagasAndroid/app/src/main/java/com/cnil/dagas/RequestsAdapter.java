package com.cnil.dagas;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.RecyclerView;

import com.cnil.dagas.data.CurrentUserThread;
import com.cnil.dagas.ui.home.HomeActivity;

import org.json.JSONException;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class RequestsAdapter extends RecyclerView.Adapter<RequestsAdapter.ViewHolder>{
    private static final String TAG = RequestsAdapter.class.getName();
//    private static String role_verbose;
    public static class BarangayRequest{
        private final String barangayName;
        private final String evacuationCenterName;
        private final double evacuationCenterDistance;
        private final String acceptURL;
        private final int id;
        private final HashMap itemRequestMap;
        private final String roleVerbose;
        public BarangayRequest(String barangayName, String evacuationCenterName, double evacuationCenterDistance, String acceptURL, int id, HashMap itemRequest, String roleVerbose) {
            this.barangayName = barangayName;
            this.evacuationCenterName = evacuationCenterName;
            this.acceptURL = acceptURL;
            this.evacuationCenterDistance = evacuationCenterDistance;
            this.id = id;
            this.itemRequestMap = itemRequest;
            this.roleVerbose = roleVerbose;
        }


        public String getEvacuationCenterName() {
            return evacuationCenterName;
        }

        public String getBarangayName() {
            return barangayName;
        }

        public String getAcceptURL() {
            return acceptURL;
        }

        public int getId() {
            return id;
        }

        public String getRoleVerbose() {
        return roleVerbose;
    }

        public double getEvacuationCenterDistance() {
            return evacuationCenterDistance;
        }

        public HashMap<String, Integer> getItemRequestMap(){ return itemRequestMap; }
    }
    final private ArrayList<BarangayRequest> barangayRequests;

    public RequestsAdapter() {
        this.barangayRequests = new ArrayList<>();
    }

    public void add(@NonNull BarangayRequest barangayRequest){
        barangayRequests.add(barangayRequest);
        notifyItemInserted(barangayRequests.size());
    }
    // Based on: https://stackoverflow.com/questions/41843758/how-to-clear-recyclerview-adapter-data
    public void clear(){
        int size = barangayRequests.size();
        barangayRequests.clear();
        notifyItemRangeRemoved(0, size);
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.card_request, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull RequestsAdapter.ViewHolder holder, int position) {
        CardView requestCard = holder.getRequestCard();
        //TODO: Move views to ViewHolder in the future
        final TextView barangayNameTextView = requestCard.findViewById(R.id.barangayNameTextView);
        final TextView evacuationCenterNameTextView = requestCard.findViewById(R.id.evacuationCenterNameTextView);
        final TextView distanceTextView = requestCard.findViewById(R.id.requestListTextView);
        final TextView foodTextView = requestCard.findViewById(R.id.foodTextView);
        final TextView waterTextView = requestCard.findViewById(R.id.waterTextView);
        final TextView clothesTextView = requestCard.findViewById(R.id.clothesTextView);
        final Button acceptButton = requestCard.findViewById(R.id.acceptButton);
        final BarangayRequest barangayRequest = barangayRequests.get(position);
        barangayNameTextView.setText(barangayRequest.getBarangayName());
        evacuationCenterNameTextView.setText(barangayRequest.getEvacuationCenterName());
        HashMap<String, Integer> itemRequestMap = barangayRequest.getItemRequestMap();
        for (Map.Entry<String, Integer> entry: itemRequestMap.entrySet()){
            if(entry.getKey().equals("Food")){
                foodTextView.setText("Food: " + entry.getValue().toString());
            } else if (entry.getKey().equals("Water")){
                waterTextView.setText("Water: " + entry.getValue().toString());
            } else clothesTextView.setText("Clothes: " + entry.getValue().toString());
        }
//        requestListTextView.setText()
        if(barangayRequest.getRoleVerbose().equals("Barangay")) acceptButton.setVisibility(View.INVISIBLE);
        distanceTextView.setText(String.valueOf(Math.round(barangayRequest.getEvacuationCenterDistance() / 1000)) + " km away");
        acceptButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Bundle bundle = new Bundle();
                bundle.putString("REQUEST_URL", barangayRequest.getAcceptURL());
                bundle.putInt("REQUEST_ID", barangayRequest.getId());
                Navigation.findNavController(view).navigate(R.id.action_nav_view_requests_to_createTransactionFragment, bundle);
            }
        });

    }

    @Override
    public int getItemCount() {
        return barangayRequests.size();
    }

    public static class ViewHolder extends RecyclerView.ViewHolder{
        private final CardView requestCard;
        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            //TODO: Click listener for stuff
            requestCard = itemView.findViewById(R.id.requestCard);
        }

        public CardView getRequestCard() {
            return requestCard;
        }
    }
}
