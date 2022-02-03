package com.cnil.dagas;

import android.os.Bundle;

import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.cnil.dagas.databinding.FragmentCreateTransactionBinding;
import com.cnil.dagas.databinding.FragmentViewSuppliesBinding;


public class ViewSuppliesFragment extends Fragment {




    public ViewSuppliesFragment() {
        // Required empty public constructor
    }

    FragmentViewSuppliesBinding binding;
//
//    @Override
//    public void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentViewSuppliesBinding.inflate(inflater, container, false);
        View root = binding.getRoot();
        RecyclerView supplyRecycler = root.findViewById(R.id.viewSupplyListRecycler);
        TransactionSupplyAdapter.TransactionSupplyCallback callback = new TransactionSupplyAdapter.TransactionSupplyCallback() {
            @Override
            public void respond(int position, TransactionSupplyAdapter.TransactionSupply supply, int amount) {
                //TODO: add TransactionOrder if it does not exist yet
            }

            @Override
            public void removeRespond(TransactionSupplyAdapter.TransactionSupply supply) {
            }
        };


        TransactionSupplyAdapter adapter = new TransactionSupplyAdapter(callback);
        supplyRecycler.setAdapter(adapter);
        supplyRecycler.setLayoutManager(new LinearLayoutManager(root.getContext()));
        CreateTransactionFragment.GrabSupplies thread = new CreateTransactionFragment.GrabSupplies(adapter);
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return root;
    }
}