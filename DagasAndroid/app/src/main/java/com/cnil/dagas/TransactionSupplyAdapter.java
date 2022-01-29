package com.cnil.dagas;

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
        void removeRespond(TransactionSupply supply);
    }

    public static class TransactionSupply{
        private final String name;
        private final String type;
        private final int available;
        private final String supplyURL;
        private final int supplyID;
        public TransactionSupply(String name, String type, int available, String supplyURL, int supplyID) {
            this.name = name;
            this.type = type;
            this.available = available;
            this.supplyURL = supplyURL;
            this.supplyID = supplyID;
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

        public int getSupplyID() {
            return supplyID;
        }

        public String getSupplyURL() {
            return supplyURL;
        }
    }
    public static class TransactionOrder{
        private final int amount;
        private final TransactionSupply supply;

        public TransactionOrder(int amount, TransactionSupply supply) {
            this.amount = amount;
            this.supply = supply;
        }

        public int getAmount() {
            return amount;
        }

        public TransactionSupply getSupply() {
            return supply;
        }
    }
    private final ArrayList<TransactionSupply> supplies;
    private final TransactionSupplyCallback callback;
    public TransactionSupplyAdapter(TransactionSupplyCallback callback){
        supplies = new ArrayList<>();
        this.callback = callback;
    }

    public ArrayList<TransactionSupply> getSupplies(){ return supplies;}

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
                } else{
                    callback.removeRespond(supply);
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
