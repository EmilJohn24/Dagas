package com.cnil.dagas;

import android.os.Bundle;

import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import com.cnil.dagas.databinding.FragmentCreateTransactionBinding;
import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;


public class CreateTransactionFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";
    private static final String TAG = CreateTransactionFragment.class.getName();
    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;

    public CreateTransactionFragment() {
        // Required empty public constructor
    }

    public static class GetRequest extends Thread{
        private final String requestURL;
        private final ArrayList<Integer> itemTypeIds;
        private final ArrayList<Integer> untransactedAmounts;

        public ArrayList<Integer> getUntransactedAmounts() {
            return untransactedAmounts;
        }

        public GetRequest(String requestURL, ArrayList<Integer> itemTypeIds) {
            this.requestURL = requestURL;
            this.itemTypeIds = itemTypeIds;
            this.untransactedAmounts = new ArrayList<>();
        }
        public void run() {
            try {
                getRequest();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void getRequest() throws IOException, JSONException{
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(requestURL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONObject requestJSONArray = new JSONObject(response.body().string());

            for (Integer typeId : itemTypeIds){
                Request typeRequest = client.builderFromBaseUrl(requestURL + "not_in_transaction/?type=" + typeId)
                                    .get()
                                    .build();
                Response typeResponse = client.newCall(typeRequest).execute();
                JSONObject typeResponseJson = new JSONObject(typeResponse.body().string());
                untransactedAmounts.add(typeResponseJson.optInt("not_in_transaction", 0));
            }
        }
    }
    public static class GrabSupplies extends Thread {
        private static final String CURRENT_SUPPLIES_URL = "/relief/api/supplies/current_supplies/";
        private static final String ITEM_TYPE_URL = "/relief/api/item-type/";
        private static final String AVAILABLE_PAX = "/relief/api/supplies/%d/available_pax/";
        private static final String SPECIFIC_ITEM_TYPE_URL = "/relief/api/item-type/%d/";
        private static final String SUPPLY_URL = "/relief/api/supplies/%d/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");


        private TransactionSupplyAdapter adapter;
        private JSONObject donationAddResponse;

        public GrabSupplies(TransactionSupplyAdapter adapter) {
            this.adapter = adapter;
        }



        public void run() {
            try {
                grabRequests();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void grabRequests() throws IOException, JSONException {
            OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(CURRENT_SUPPLIES_URL)
                    .get()
                    .build();
            Response response = client.newCall(request).execute();
            //TODO: Add success check
            JSONArray requestJSONArray = new JSONArray(response.body().string());
            for (int index = 0; index < requestJSONArray.length(); index++) {
                JSONObject requestJSONObject = requestJSONArray.getJSONObject(index);
                String itemName = requestJSONObject.getString("name");
                int itemID = requestJSONObject.getInt("id");
                int itemTypeID = requestJSONObject.getInt("type");
                int pax = requestJSONObject.getInt("pax");
                int available = requestJSONObject.getInt("available_pax");
                Request itemTypeRequest = client.builderFromBaseUrl(
                                            String.format(SPECIFIC_ITEM_TYPE_URL, itemTypeID))
                                        .get()
                                        .build();
                Response itemTypeResponse = client.newCall(itemTypeRequest).execute();
                JSONObject itemTypeJSON = new JSONObject(itemTypeResponse.body().string());
                String itemTypeName = itemTypeJSON.getString("name");

//                Request availablePaxRequest = client.builderFromBaseUrl(
//                                            String.format(AVAILABLE_PAX, itemID))
//                                        .get()
//                                        .build();
//                Response availablePaxResponse = client.newCall(availablePaxRequest).execute();
//                JSONObject availablePaxJSON = new JSONObject(availablePaxResponse.body().string());
//                int available = availablePaxJSON.getInt("available");

                adapter.add(new TransactionSupplyAdapter.TransactionSupply(
                                itemName, itemTypeName,
                                available, String.format(SUPPLY_URL, itemID), itemID)
                        );

            }

            //TODO: Check for errors

        }
    }
    public static class CreateTransaction extends Thread{
        private static final String TRANSACTION_ORDER_URL = "/relief/api/transaction-order/";
        private static final String TRANSACTION_URL = "/relief/api/transactions/";
        private static final String TRANSACTION_SPECIFIC_URL = "/relief/api/transactions/%s/";
        private Map<TransactionSupplyAdapter.TransactionSupply, TransactionSupplyAdapter.TransactionOrder> supplyOrderMap;
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        private int requestID;
        private String transactionID;


        public CreateTransaction(int requestID, Map<TransactionSupplyAdapter.TransactionSupply, TransactionSupplyAdapter.TransactionOrder> supplyOrderMap) {
            this.supplyOrderMap = supplyOrderMap;
            this.requestID = requestID;
        }
        public String getRecentTransactionURL(){
            return String.format(TRANSACTION_SPECIFIC_URL, transactionID);
        }
        public void run() {
            try {
                addTransaction();
            } catch (IOException | JSONException e) {
                Log.e(TAG, e.getMessage());
            }
        }
        private void addTransaction() throws IOException, JSONException {
            JSONObject createRequestJSON = new JSONObject();
            try {
//                createRequestJSON.put("name", supplyName);
//                createRequestJSON.put("donor", "    ");
                createRequestJSON.put("barangay_request", requestID);
                // TODO: Check type + 1 (index)

            } catch (JSONException e) {
                Log.e(TAG, e.getMessage());
            }
            OkHttpSingleton client = OkHttpSingleton.getInstance();
            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
            Request request = client.builderFromBaseUrl(TRANSACTION_URL)
                    .post(body)
                    .build();
            Response transactionResponse = client.newCall(request).execute();

            JSONObject transactionJSON = new JSONObject(transactionResponse.body().string());
            transactionID = transactionJSON.getString("id");

            for (Map.Entry<TransactionSupplyAdapter.TransactionSupply, TransactionSupplyAdapter.TransactionOrder> order :
                    supplyOrderMap.entrySet()){
                JSONObject addOrderRequestJSON = new JSONObject();
                try {
//                createRequestJSON.put("name", supplyName);
                    addOrderRequestJSON.put("pax", order.getValue().getAmount());
                    addOrderRequestJSON.put("supply", order.getValue().getSupply().getSupplyID());
                    addOrderRequestJSON.put("transaction", transactionID);

                } catch (JSONException e) {
                    Log.e(TAG, e.getMessage());
                }

                RequestBody addOrderRequestBody = RequestBody.create(addOrderRequestJSON.toString(), JSON);
                Request transactionOrderRequest = client.builderFromBaseUrl(TRANSACTION_ORDER_URL)
                        .post(addOrderRequestBody)
                        .build();

                Response transactionOrderResponse = client.newCall(transactionOrderRequest).execute();
                JSONObject transactionOrderResponseJSON = new JSONObject(transactionOrderResponse.body().string());
            }


            }

    }
    TransactionSupplyAdapter.TransactionSupplyCallback callback;

    FragmentCreateTransactionBinding binding;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentCreateTransactionBinding.inflate(inflater, container, false);
        assert getArguments() != null;
        String requestURL = getArguments().getString("REQUEST_URL");
        int requestID = getArguments().getInt("REQUEST_ID");
        View root = binding.getRoot();
        RecyclerView supplyRecycler = root.findViewById(R.id.transactionSupplyRecycler);

        TableLayout transactionTable = root.findViewById(R.id.transactionTable);
        ArrayList<TableRow> transactionRows = new ArrayList<>();
        RetrieveItemTypesThread itemTypesThread = new RetrieveItemTypesThread();
        GetRequest requestThread = null;
        try {
            itemTypesThread.start();
            itemTypesThread.join();
            requestThread = new GetRequest(requestURL, itemTypesThread.getTypeIds());
            requestThread.start();
            requestThread.join();
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }
        assert requestThread != null;
        Map<String, Integer> remainingUntransactedAmounts = new HashMap<String, Integer>();
        Map<String, TextView> amountTextViews = new HashMap<String, TextView>();
        for (int i = 0; i != itemTypesThread.getTypeIds().size(); ++i){
            String itemName = itemTypesThread.getName(i);
            Integer untransactedAmount = requestThread.getUntransactedAmounts().get(i);
            remainingUntransactedAmounts.put(itemName, untransactedAmount);
            TableRow itemRow = new TableRow(this.getContext());
            transactionRows.add(itemRow);
            itemRow.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT,
                                                                TableRow.LayoutParams.MATCH_PARENT));
            TextView typeName = new TextView(this.getContext());
            TextView untransactedAmountTextView = new TextView(this.getContext());
            typeName.setText(itemName);
//            typeName.setLayoutParams(new ViewGroup.LayoutParams(
//                                        ViewGroup.LayoutParams.WRAP_CONTENT,
//                                        ViewGroup.LayoutParams.WRAP_CONTENT));
            //TODO: Do dimensions.xml version:
            // https://stackoverflow.com/questions/9494037/how-to-set-text-size-of-textview-dynamically-for-different-screens
            typeName.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20f);
            typeName.setBackgroundResource(R.drawable.createtransactionsearch);
            untransactedAmountTextView.setText(String.valueOf(untransactedAmount));
            untransactedAmountTextView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20f);
            untransactedAmountTextView.setPaddingRelative(300,10,0,10);
            untransactedAmountTextView.setBackgroundResource(R.drawable.createtransactionsearch);
            untransactedAmountTextView.setGravity(Gravity.RIGHT);
            if(i == 0){
                TableRow headerRow = new TableRow(this.getContext());

                headerRow.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT,
                        TableRow.LayoutParams.MATCH_PARENT));
                TextView itemTypeHeader = new TextView(this.getContext());
                TextView amountHeader = new TextView(this.getContext());
                itemTypeHeader.setText("Item Type");
                itemTypeHeader.setGravity(Gravity.CENTER);
                itemTypeHeader.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20f);
                itemTypeHeader.setGravity(Gravity.CENTER);
                itemTypeHeader.setBackgroundResource(R.drawable.createtransactionsearch);
                headerRow.addView(itemTypeHeader);
                amountHeader.setText("Amount");
                amountHeader.setGravity(Gravity.CENTER);
                amountHeader.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20f);
                amountHeader.setGravity(Gravity.CENTER);
                amountHeader.setPaddingRelative(300,10,0,10);
                amountHeader.setBackgroundResource(R.drawable.createtransactionsearch);
                headerRow.addView(amountHeader);
                transactionTable.addView(headerRow);
            }
            itemRow.addView(typeName);
            itemRow.addView(untransactedAmountTextView);
            amountTextViews.put(itemName, untransactedAmountTextView);
            transactionTable.addView(itemRow);
        }


        Map<TransactionSupplyAdapter.TransactionSupply, TransactionSupplyAdapter.TransactionOrder> supplyOrderMap = new HashMap<>();
        callback = new TransactionSupplyAdapter.TransactionSupplyCallback() {
            @Override
            public void respond(int position, TransactionSupplyAdapter.TransactionSupply supply, int amount) {
                //TODO: add TransactionOrder if it does not exist yet
                supplyOrderMap.put(supply, new TransactionSupplyAdapter.TransactionOrder(amount, supply));
                Integer updatedValue = remainingUntransactedAmounts.get(supply.getType()) - amount;
                remainingUntransactedAmounts.replace(supply.getType(), updatedValue);
                Objects.requireNonNull(amountTextViews.get(supply.getType())).setText(String.valueOf(updatedValue));

            }

            @Override
            public void removeRespond(TransactionSupplyAdapter.TransactionSupply supply) {
                TransactionSupplyAdapter.TransactionOrder order = supplyOrderMap.get(supply);
                Integer updatedValue = remainingUntransactedAmounts.get(supply.getType()) + order.getAmount();
                remainingUntransactedAmounts.replace(supply.getType(), updatedValue);
                Objects.requireNonNull(amountTextViews.get(supply.getType())).setText(String.valueOf(updatedValue));
                supplyOrderMap.remove(supply);


            }
        };


        TransactionSupplyAdapter adapter = new TransactionSupplyAdapter(callback);
        supplyRecycler.setAdapter(adapter);
        supplyRecycler.setLayoutManager(new LinearLayoutManager(root.getContext()));
        GrabSupplies thread = new GrabSupplies(adapter);
        thread.start();
        try {
            thread.join();
        } catch (InterruptedException e) {
            Log.e(TAG, e.getMessage());
        }




        Button transactionSubmit = root.findViewById(R.id.transactionSubmit);

        transactionSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                CreateTransaction createTransactionThread = new CreateTransaction(requestID, supplyOrderMap);
                createTransactionThread.start();
                try {
                    createTransactionThread.join();
                } catch (InterruptedException e) {
                    Log.e(TAG, e.getMessage());
                }

                //TODO: Bring to QR page
                Bundle bundle = new Bundle();
                bundle.putString("TRANSACTION_URL", createTransactionThread.getRecentTransactionURL());
                Navigation.findNavController(view).navigate(R.id.action_nav_create_transaction_to_transactionReceiptFragment2, bundle);
            }
        });

        return root;
    }
}