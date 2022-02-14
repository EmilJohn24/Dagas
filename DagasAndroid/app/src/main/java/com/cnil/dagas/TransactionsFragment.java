package com.cnil.dagas;

import android.location.Location;
import android.os.Bundle;

import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.cnil.dagas.databinding.FragmentCreateTransactionBinding;
import com.cnil.dagas.databinding.FragmentRequestsBinding;
import com.cnil.dagas.databinding.FragmentTransactionBinding;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.Response;


public class TransactionsFragment extends Fragment {

    static private final String TAG = TransactionsFragment.class.getName();

    public TransactionsFragment() {
        // Required empty public constructor
    }

    class GrabTransactions extends Thread {
        private static final String TRANSACTION_URL = "/relief/api/transactions/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        private TransactionAdapter adapter;
//        private JSONObject donationAddResponse;

        public GrabTransactions(TransactionAdapter adapter) {
            this.adapter = adapter;
        }

        public void run() {
            try {
                grabTransactions();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }

        private void grabTransactions() throws IOException, JSONException {
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(TRANSACTION_URL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            JSONArray transactionJSONArray = new JSONArray(response.body().string());
            for (int index = 0; index < transactionJSONArray.length(); index++) {
                JSONObject transactionJSONObject = transactionJSONArray.getJSONObject(index);
                String barangayName = transactionJSONObject.getString("barangay_name");
                String donorName = transactionJSONObject.getString("donor_name");
                String evacCenterName = transactionJSONObject.getString("evac_center_name");
                String id = transactionJSONObject.getString("id");
                TransactionAdapter.Transaction transaction = new TransactionAdapter.Transaction(barangayName, evacCenterName,
                        donorName, id);
                adapter.add(transaction);
            }
        }


    }
    // TODO: Rename and change types and number of parameters

    FragmentTransactionBinding binding;
//    @Override
//    public void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentTransactionBinding.inflate(inflater, container, false);
        View root = binding.getRoot();
        RecyclerView transactionRecyclerView = root.findViewById(R.id.transactionsRecycler);
        TransactionAdapter adapter = new TransactionAdapter();
        GrabTransactions thread = new GrabTransactions(adapter);
        thread.start();
        try {
            thread.join();
            transactionRecyclerView.setAdapter(adapter);
            transactionRecyclerView.setLayoutManager(new LinearLayoutManager(root.getContext()));
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }

        return root;
    }
}