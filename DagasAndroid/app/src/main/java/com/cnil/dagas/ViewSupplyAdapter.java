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

public class ViewSupplyAdapter extends RecyclerView.Adapter<ViewSupplyAdapter.ViewHolder>{

    public interface ViewSupplyCallback {
        void respond(int position, ViewSupply supply, int amount);
        void removeRespond(ViewSupply supply);
    }

    public static class ViewSupply{
        private final String name;
        private final String type;
        private final int available;
        public ViewSupply(String name, String type, int available, String supplyURL, int supplyID) {
            this.name = name;
            this.type = type;
            this.available = available;
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
    public static class TransactionOrder{
        private final int amount;
        private final ViewSupply supply;

        public TransactionOrder(int amount, ViewSupply supply) {
            this.amount = amount;
            this.supply = supply;
        }

        public int getAmount() {
            return amount;
        }

        public ViewSupply getSupply() {
            return supply;
        }
    }
    private final ArrayList<ViewSupply> supplies;
    private final ViewSupplyCallback callback;
    public ViewSupplyAdapter(ViewSupplyCallback callback){
        supplies = new ArrayList<>();
        this.callback = callback;
    }

    public ArrayList<ViewSupply> getSupplies(){ return supplies;}

    public void add(ViewSupply supply){
        supplies.add(supply);
    }
    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.card_view_supply, parent, false);
        return new ViewSupplyAdapter.ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        //setup
        CardView supplyCard = holder.getSupplyCard();
        TextView transactionSupplyName = supplyCard.findViewById(R.id.supplyName);
        TextView typeTextView = supplyCard.findViewById(R.id.typeTextView);
        TextView availableAmountTextView = supplyCard.findViewById(R.id.availableAmount);
        ViewSupply supply = supplies.get(position);
        transactionSupplyName.setText(supply.getName());
        typeTextView.setText(supply.getType());
        availableAmountTextView.setText(String.format("%d left", supply.getAvailablePax()));
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
            supplyCard = itemView.findViewById(R.id.view_supplyCard);
        }

        public CardView getSupplyCard() {
            return supplyCard;
        }
    }
}
