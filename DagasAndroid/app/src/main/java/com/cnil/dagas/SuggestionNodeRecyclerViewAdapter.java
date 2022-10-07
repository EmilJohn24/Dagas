package com.cnil.dagas;

import android.view.LayoutInflater;
import android.view.ViewGroup;
import android.widget.TableLayout;
import android.widget.TextView;

import androidx.recyclerview.widget.RecyclerView;

import com.cnil.dagas.databinding.CardSuggestionNodeBinding;
import com.cnil.dagas.placeholder.Suggestion.SuggestionNode;

import java.util.List;

/**
 * {@link RecyclerView.Adapter} that can display a {@link SuggestionNode}.
 * TODO: Replace the implementation with code for your data type.
 */
public class SuggestionNodeRecyclerViewAdapter extends RecyclerView.Adapter<SuggestionNodeRecyclerViewAdapter.ViewHolder> {

    private final List<SuggestionNode> mValues;

    public SuggestionNodeRecyclerViewAdapter(List<SuggestionNode> items) {
        mValues = items;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {

        return new ViewHolder(CardSuggestionNodeBinding.inflate(LayoutInflater.from(parent.getContext()), parent, false));

    }

    @Override
    public void onBindViewHolder(final ViewHolder holder, int position) {
        holder.mItem = mValues.get(position);
        holder.suggestedBarangayName.setText("Barangay: " + mValues.get(position).suggestedBarangayName);
        holder.suggestedEvacuationCenterName.setText("Evacuation Center Name: " + mValues.get(position).suggestedEvacuationCenterName);
//        holder.suggestedBarangayName.setText(mValues.get(position).suggestedBarangayName);
        //TODO: Consider converting the table to dynamic
        holder.foodAmount.setText(mValues.get(position).fulfillments.get("Food").toString());
        holder.waterAmount.setText(mValues.get(position).fulfillments.get("Water").toString());
        holder.clothesAmount.setText(mValues.get(position).fulfillments.get("Clothes").toString());

    }

    @Override
    public int getItemCount() {
        return mValues.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        public final TextView suggestedBarangayName;
        public final TextView suggestedEvacuationCenterName;
        public final TableLayout contentTable;
        public final TextView foodAmount;
        public final TextView waterAmount;
        public final TextView clothesAmount;
        public SuggestionNode mItem;

        public ViewHolder(CardSuggestionNodeBinding binding) {
            super(binding.getRoot());
            suggestedBarangayName = binding.suggestedBarangayName;
            suggestedEvacuationCenterName = binding.suggestedEvacuationCenterName;
            contentTable = binding.contentTable;
            foodAmount = binding.foodAmount;
            waterAmount = binding.waterAmount;
            clothesAmount = binding.clothesAmount;
        }

        @Override
        public String toString() {
            return super.toString() + " '" + suggestedBarangayName.getText() + "'";
        }
    }
}