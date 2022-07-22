package com.cnil.dagas;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;

public class TransactionAdapter extends RecyclerView.Adapter<TransactionAdapter.ViewHolder>{
    public static class Transaction{
        private final String barangayName;
        private final String evacuationCenterName;
        private final String donorName;
        private final String id;
        public Transaction(String barangayName, String evacuationCenterName, String donorName, String id) {
            this.barangayName = barangayName;
            this.evacuationCenterName = evacuationCenterName;
            this.donorName = donorName;
            this.id = id;
        }

        public String getEvacuationCenterName() {
            return evacuationCenterName;
        }

        public String getBarangayName() {
            return barangayName;
        }

        public String getId() {
            return id;
        }

        public String getDonorName() {
            return donorName;
        }
    }
    final private ArrayList<Transaction> transactions;

    public TransactionAdapter() {
        this.transactions = new ArrayList<>();
    }

    public void add(@NonNull Transaction transaction){
        transactions.add(transaction);
        notifyItemInserted(transactions.size());
    }

    // Based on: https://stackoverflow.com/questions/41843758/how-to-clear-recyclerview-adapter-data
    public void clear(){
        int size = transactions.size();
        transactions.clear();
        notifyItemRangeRemoved(0, size);
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.card_transaction, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull TransactionAdapter.ViewHolder holder, int position) {
        CardView transactionCard = holder.getTransactionCard();
        //TODO: Move views to ViewHolder in the future
        final TextView referenceNumberTextView = transactionCard.findViewById(R.id.referenceNumber);
        final TextView donorNameTextView = transactionCard.findViewById(R.id.donorName);
        final TextView evacuationCenterNameTextView = transactionCard.findViewById(R.id.evacuationCenterName);
        final TextView barangayNameTextView = transactionCard.findViewById(R.id.barangayName);
        final Button acceptButton = transactionCard.findViewById(R.id.checkButton);
        final Transaction transaction = transactions.get(position);
        donorNameTextView.setText(transaction.getDonorName());
        barangayNameTextView.setText(transaction.getBarangayName());
        evacuationCenterNameTextView.setText(transaction.getEvacuationCenterName());
        referenceNumberTextView.setText(transaction.getId());
        acceptButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Bundle bundle = new Bundle();
                //TODO: Add URL format
                final String transaction_url = String.format("/relief/api/transactions/%s/", transaction.getId());
                bundle.putString("TRANSACTION_URL", transaction_url);
//                bundle.putInt("REQUEST_ID", barangayRequest.getId());
                Navigation.findNavController(view).navigate(R.id.action_transactionsFragment_to_nav_transaction_receipt, bundle);
            }
        });

    }

    @Override
    public int getItemCount() {
        return transactions.size();
    }

    public static class ViewHolder extends RecyclerView.ViewHolder{
        private final CardView transactionCard;
        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            //TODO: Click listener for stuff
            transactionCard = itemView.findViewById(R.id.transactionCard);
        }

        public CardView getTransactionCard() {
            return transactionCard;
        }
    }
}

