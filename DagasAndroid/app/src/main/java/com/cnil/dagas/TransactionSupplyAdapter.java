package com.cnil.dagas;

import android.content.Context;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;

public class TransactionSupplyAdapter extends RecyclerView.Adapter<TransactionSupplyAdapter.ViewHolder>{

    public interface TransactionSupplyCallback{
        void respond(int position, TransactionSupply supply, int amount);
    }

    public static class TransactionSupply{
        private String name;
        private String type;
        private int available;
        private String supplyURL;
        public TransactionSupply(String name, String type, int available, String supplyURL) {
            this.name = name;
            this.type = type;
            this.available = available;
            this.supplyURL = supplyURL;
        }

        public String getName() {
            return name;
        }

        public String getType() {
            return type;
        }

        public int getAvailablePax() {
            return available;
        }
    }


    private ArrayList<TransactionSupply> supplies;
    private TransactionSupplyCallback callback;
    public TransactionSupplyAdapter(TransactionSupplyCallback callback){
        supplies = new ArrayList<>();
        this.callback = callback;
    }



    public void add(TransactionSupply supply){
        supplies.add(supply);
    }
    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.card_transaction_supply, parent, false);
        return new TransactionSupplyAdapter.ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        //setup

        final int currentPosition = position;
        CardView supplyCard = holder.getSupplyCard();
        CheckBox addToTransaction =  supplyCard.findViewById(R.id.addToTransaction);
        TextView transactionSupplyName = supplyCard.findViewById(R.id.transactionSupplyName);
        TextView typeTextView = supplyCard.findViewById(R.id.typeTextView);
        TextView availableAmountTextView = supplyCard.findViewById(R.id.availableAmount);
        EditText donateAmount = supplyCard.findViewById(R.id.donateAmount);
        TransactionSupply supply = supplies.get(position);
        transactionSupplyName.setText(supply.getName());
        typeTextView.setText(supply.getType());
        availableAmountTextView.setText(String.format("%d left", supply.getAvailablePax()));
        //Update UI stuff
//        donateAmount.setOnEditorActionListener(new TextView.OnEditorActionListener() {
//            @Override
//            public boolean onEditorAction(TextView textView, int i, KeyEvent keyEvent) {
//                return false;
//            }
//        });
        addToTransaction.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean checked) {
                if (checked){
                    callback.respond(currentPosition, supply,
                                Integer.parseInt(donateAmount.getText().toString()));
                }
            }
        });
    }

    @Override
    public int getItemCount() {
        return supplies.size();
    }

    public static class ViewHolder extends RecyclerView.ViewHolder{
        private final CardView supplyCard;
        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            //TODO: Click listener for stuff
            supplyCard = itemView.findViewById(R.id.supplyCard);
        }

        public CardView getSupplyCard() {
            return supplyCard;
        }
    }
}
