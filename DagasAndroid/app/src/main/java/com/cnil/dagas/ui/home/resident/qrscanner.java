package com.cnil.dagas.ui.home.resident;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;

import com.budiyev.android.codescanner.CodeScanner;
import com.budiyev.android.codescanner.CodeScannerView;
import com.budiyev.android.codescanner.DecodeCallback;
import com.cnil.dagas.R;
import com.cnil.dagas.databinding.EvacuationcentervisualmapBinding;
import com.cnil.dagas.databinding.QrScannerBinding;
import com.google.zxing.Result;

import java.util.ArrayList;


public class qrscanner extends Fragment {

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
                            Toast.makeText(activity, result.getText(), Toast.LENGTH_SHORT).show();
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