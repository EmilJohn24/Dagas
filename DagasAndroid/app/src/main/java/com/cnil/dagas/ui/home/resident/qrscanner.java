package com.cnil.dagas.ui.home.resident;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.LinearLayoutManager;

import com.budiyev.android.codescanner.CodeScanner;
import com.budiyev.android.codescanner.CodeScannerView;
import com.budiyev.android.codescanner.DecodeCallback;
import com.cnil.dagas.R;
import com.cnil.dagas.TransactionAdapter;
import com.cnil.dagas.TransactionsFragment;
import com.cnil.dagas.databinding.EvacuationcentervisualmapBinding;
import com.cnil.dagas.databinding.QrScannerBinding;
import com.cnil.dagas.http.OkHttpSingleton;
import com.google.zxing.Result;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.Response;


public class qrscanner extends Fragment {

    boolean isTransaction = false;

    class GrabTransaction extends Thread {
        private static final String TRANSACTION_URL = "/relief/api/transactions/";
        private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        private String transactionID;
//        private JSONObject donationAddResponse;

        public GrabTransaction(String transactionID) {
            this.transactionID = transactionID;
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
                String id = transactionJSONObject.getString("id");
                if (id.equals(this.transactionID)) {
                    isTransaction = true;
                    break;
                }
            }
        }


    }

//    private final static int CAMERA_REQUEST_CODE = 101;

    private QrScannerBinding binding;
    private CodeScanner mCodeScanner;
    private final String TAG = qrscanner.class.getName();
    public View onCreateView(@NonNull LayoutInflater inflater,
                             @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        final Activity activity = getActivity();
        binding = QrScannerBinding.inflate(inflater, container, false);
        View root = binding.getRoot();
//        if(ContextCompat.checkSelfPermission(activity.getApplicationContext(),Manifest.permission.READ_PHONE_STATE) != PackageManager.PERMISSION_GRANTED) {
//            ActivityCompat.requestPermissions(activity, new String[]{Manifest.permission.READ_PHONE_STATE}, 1);
//        }
//        int result = ContextCompat.checkSelfPermission(activity.getApplicationContext(), Manifest.permission.READ_PHONE_STATE);
//        if (result == 0){
        // function which uses the permission
            CodeScannerView scannerView = root.findViewById(R.id.scanner_view);
            mCodeScanner = new CodeScanner(activity, scannerView);
            mCodeScanner.setDecodeCallback(new DecodeCallback() {
                @Override
                public void onDecoded(@NonNull final Result result) {
                    activity.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            GrabTransaction thread = new GrabTransaction(result.getText());
                            thread.start();
                            try {
                                thread.join();
                            } catch (InterruptedException e) {
                                Log.e(TAG, e.getMessage());
                            }
                            //Toast.makeText(activity, result.getText(), Toast.LENGTH_SHORT).show();
                            if(isTransaction){
                                isTransaction = false;
                                Bundle bundle = new Bundle();
                                //TODO: Add URL format
                                final String transaction_url = String.format("/relief/api/transactions/%s/", result.getText());
                                bundle.putString("TRANSACTION_URL", transaction_url);
                                Toast.makeText(activity, result.getText(), Toast.LENGTH_SHORT).show();
                                Navigation.findNavController(root).navigate(R.id.action_nav_qr_scanner_to_nav_transaction_receipt, bundle);
                            }
                            else mCodeScanner.startPreview();
                        }
                    });
                }
            });
            scannerView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    mCodeScanner.startPreview();
                }
            });
//        }

        return root;
    }



    @Override
    public void onResume() {
        super.onResume();
        mCodeScanner.startPreview();
    }

    @Override
    public void onPause() {
        mCodeScanner.releaseResources();
        super.onPause();
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }

}