package com.cnil.dagas;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;

import com.cnil.dagas.databinding.FragmentSuccessfullyScannedBinding;
import com.cnil.dagas.http.DagasJSONServer;
import com.squareup.picasso.Picasso;

import org.json.JSONObject;

public class ResidentQrScannedFragment extends Fragment {
    private final static String TAG = ResidentQRFragment.class.getName();
    private FragmentSuccessfullyScannedBinding binding;
    public ResidentQrScannedFragment() {
        // Required empty public constructor
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentSuccessfullyScannedBinding.inflate(inflater, container, false);
        ConstraintLayout scanHeader = binding.scanHeader;
        ImageView checkImageView = binding.checkImageView;
        TextView successTextView = binding.successText;
        TextView successMessageTextView = binding.successMessage;
        TextView residentNameTextView = binding.residentName;
        ImageView profilePictureImageView = binding.profilePictureQrImageView;
        TextView barangayLocationTextView = binding.barangayLocation;
        Button approveButton = binding.qrApproveButton;
        assert getArguments() != null;
        String stubId = getArguments().getString("STUB_ID", "*");
        try {
            JSONObject stubInfo = DagasJSONServer.getDetail("/relief/api/stubs/", stubId);
            boolean isReceived = stubInfo.getBoolean("received");
            boolean isExpired = stubInfo.getBoolean("is_expired");
            JSONObject userRelatedData = stubInfo.getJSONObject("user");
            String residentProfilePictureUrl = userRelatedData
                                .optString("profile_picture");
            if (!residentProfilePictureUrl.equals("")){
                Picasso.with(getContext()).load(residentProfilePictureUrl)
                        .into(profilePictureImageView);
            }
            String residentName = userRelatedData.optString("first_name") + " "
                    + userRelatedData.optString("last_name");
            residentNameTextView.setText(residentName);
            JSONObject residentInfo = stubInfo.getJSONObject("resident");
            JSONObject barangayInfo = residentInfo.getJSONObject("barangay_info");
            String barangayName = barangayInfo.optString("user");
            barangayLocationTextView.setText(barangayName);
            approveButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    //action_nav_resident_qr_scanned_to_nav_qr_scanner
                    String receivedUrl = DagasJSONServer
                                        .createDetailUrl("/relief/api/stubs/", stubId)
                                                + "mark_as_received/";
                    try {
                        DagasJSONServer.put(receivedUrl, new JSONObject());
                        //return to QR scanner
                        Navigation.findNavController(binding.getRoot())
                                .navigate(R.id.action_nav_resident_qr_scanned_to_nav_qr_scanner);
                    } catch (Exception e) {
                        Log.e(TAG, e.getMessage());
                    }
                }
            });
            if (isReceived){
                //TODO: Set scanHeader and checkImageView to error counterparts
                successMessageTextView.setText(R.string.qrClaimed);
                successTextView.setText(R.string.invalid_text);
                checkImageView.setImageResource(R.drawable.ic_invalid_logo);
                scanHeader.setBackgroundResource(R.drawable.redbg);
                approveButton.setEnabled(false);
            } else if (isExpired){
                successMessageTextView.setText(R.string.qrExpired);
                successTextView.setText(R.string.invalid_text);
                checkImageView.setImageResource(R.drawable.ic_invalid_logo);
                scanHeader.setBackgroundResource(R.drawable.redbg);
                approveButton.setEnabled(false);
            }
        } catch (Exception e) {
            Log.e(TAG, e.getMessage());
        }
        return binding.getRoot();
    }
}
