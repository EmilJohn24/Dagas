package com.cnil.dagas;

import androidx.recyclerview.widget.RecyclerView;

import android.view.LayoutInflater;
import android.view.ViewGroup;
import android.widget.TableLayout;
import android.widget.TextView;

import com.cnil.dagas.placeholder.Suggestion.SuggestionNode;
import com.cnil.dagas.databinding.CardSuggestionNodeBinding;

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
        holder.suggestedBarangayName.setText(mValues.get(position).suggestedBarangayName);
        holder.suggestedEvacuationCenterName.setText(mValues.get(position).suggestedEvacuationCenterName);
        holder.suggestedBarangayName.setText(mValues.get(position).suggestedBarangayName);
        //TODO: Load in fulfillments here to TableLayout contentTable
    }

    @Override
    public int getItemCount() {
        return mValues.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        public final TextView suggestedBarangayName;
        public final TextView suggestedEvacuationCenterName;
        public final TableLayout contentTable;
        public SuggestionNode mItem;

        public ViewHolder(CardSuggestionNodeBinding binding) {
            super(binding.getRoot());
            suggestedBarangayName = binding.suggestedBarangayName;
            suggestedEvacuationCenterName = binding.suggestedEvacuationCenterName;
            contentTable = binding.contentTable;
        }

        @Override
        public String toString() {
            return super.toString() + " '" + suggestedBarangayName.getText() + "'";
        }
    }
}