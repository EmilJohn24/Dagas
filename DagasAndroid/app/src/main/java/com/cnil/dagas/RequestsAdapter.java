package com.cnil.dagas;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;

public class RequestsAdapter extends RecyclerView.Adapter<RequestsAdapter.ViewHolder>{
    public static class BarangayRequest{
        private String barangayName;
        private String evacuationCenterName;
        private String acceptURL;

        public BarangayRequest(String barangayName, String evacuationCenterName, String acceptURL) {
            this.barangayName = barangayName;
            this.evacuationCenterName = evacuationCenterName;
            this.acceptURL = acceptURL;
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
    }
    final private ArrayList<BarangayRequest> barangayRequests;

    public RequestsAdapter() {
        this.barangayRequests = new ArrayList<>();
    }

    public void add(@NonNull BarangayRequest barangayRequest){
        barangayRequests.add(barangayRequest);
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
        final TextView barangayNameTextView = requestCard.findViewById(R.id.barangayNameTextView);
        final TextView evacuationCenterNameTextView = requestCard.findViewById(R.id.evacuationCenterNameTextView);
        final TextView requestListTextView = requestCard.findViewById(R.id.requestListTextView);
        final Button acceptButton = requestCard.findViewById(R.id.acceptButton);
        final BarangayRequest barangayRequest = barangayRequests.get(position);
        barangayNameTextView.setText(barangayRequest.getBarangayName());
        evacuationCenterNameTextView.setText(barangayRequest.getEvacuationCenterName());
        acceptButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // TODO: (Jan 26) move to next fragment (transaction)
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
