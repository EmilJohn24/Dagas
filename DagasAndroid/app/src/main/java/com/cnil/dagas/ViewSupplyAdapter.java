package com.cnil.dagas;

import android.annotation.SuppressLint;
import android.os.Bundle;
import android.os.Parcel;
import android.os.Parcelable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.RecyclerView;

import com.cnil.dagas.http.DagasJSONServer;

import java.util.ArrayList;

public class ViewSupplyAdapter extends RecyclerView.Adapter<ViewSupplyAdapter.ViewHolder>{

    public interface ViewSupplyCallback {
        void respond(int position, ViewSupply supply, int amount);
        void removeRespond(ViewSupply supply);
        void loadPicture(ViewSupply supply);
    }

    public static class ViewSupply implements Parcelable {
        private final int supplyId;
        private final String name;
        private final String type;
        private final int available;
        private int paxTransacted;
        private boolean isTransacted;
        private String pictureUrl;



        public ViewSupply(String name, String type, int available, String supplyURL, int supplyID) {
            this.isTransacted = false;
            this.name = name;
            this.type = type;
            this.available = available;
            this.supplyId = supplyID;
        }

        protected ViewSupply(Parcel in) {
            supplyId = in.readInt();
            name = in.readString();
            type = in.readString();
            available = in.readInt();
            paxTransacted = in.readInt();
            isTransacted = in.readByte() != 0;
            pictureUrl = in.readString();
        }

        public static final Creator<ViewSupply> CREATOR = new Creator<ViewSupply>() {
            @Override
            public ViewSupply createFromParcel(Parcel in) {
                return new ViewSupply(in);
            }

            @Override
            public ViewSupply[] newArray(int size) {
                return new ViewSupply[size];
            }
        };

        public String getName() {
            return name;
        }

        public String getType() {
            return type;
        }

        public int getAvailablePax() {
            return available;
        }


        public int getSupplyId() {
            return supplyId;
        }

        public int getPaxTransacted() {
            return paxTransacted;
        }

        public void setPaxTransacted(int paxTransacted) {
            this.isTransacted = true;
            this.paxTransacted = paxTransacted;
        }

        public boolean isTransacted() {
            return isTransacted;
        }
        public boolean hasPictureUrl(){
            return pictureUrl != null;
        }
        public String getPictureUrl() {
            return pictureUrl;
        }

        public void setPictureUrl(String pictureUrl) {
            this.pictureUrl = pictureUrl;
        }

        @Override
        public int describeContents() {
            return 0;
        }

        @Override
        public void writeToParcel(Parcel parcel, int i) {
            parcel.writeInt(supplyId);
            parcel.writeString(name);
            parcel.writeString(type);
            parcel.writeInt(available);
            parcel.writeInt(paxTransacted);
            parcel.writeByte((byte) (isTransacted?1:0));
            parcel.writeString(pictureUrl);
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

    @SuppressLint("DefaultLocale")
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



        Button deleteButton = supplyCard.findViewById(R.id.supplyDeleteButton);
        deleteButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                supplies.remove(holder.getBindingAdapterPosition());
                notifyItemRemoved(holder.getBindingAdapterPosition());
                try {
                    DagasJSONServer.delete("/relief/api/supplies/", supply.getSupplyId());
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
        Button viewPictureButton = supplyCard.findViewById(R.id.viewPictureButton);
        viewPictureButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                callback.loadPicture(supply);
            }
        });

        Button editSupplyButton = supplyCard.findViewById(R.id.editSupplyButton);
        editSupplyButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //action_nav_view_supplies_to_nav_donor_add_supply
                Bundle bundle = new Bundle();
                bundle.putParcelable("SUPPLY_INFO", supply);
//                bundle.("TRANSACTION_URL", transaction_url);
//                bundle.putInt("REQUEST_ID", barangayRequest.getId());
                Navigation.findNavController(view).navigate(R.id.action_nav_view_supplies_to_nav_donor_add_supply, bundle);
            }
        });

        if (!supply.isTransacted())
            availableAmountTextView.setText(String.format("%d left", supply.getAvailablePax()));
        else {
            availableAmountTextView.setText(String.format("Pax: %d", supply.getPaxTransacted()));
            deleteButton.setEnabled(false);
            editSupplyButton.setEnabled(false);
            deleteButton.setVisibility(Button.INVISIBLE);
            editSupplyButton.setVisibility(Button.INVISIBLE);
        }

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
//            ViewSupplyAdapter.this.notifyItemRemoved()
        }

        public CardView getSupplyCard() {
            return supplyCard;
        }
    }
}
