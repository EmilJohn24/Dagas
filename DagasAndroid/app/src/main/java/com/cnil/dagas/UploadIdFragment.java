package com.cnil.dagas;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;

import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.ActivityResultRegistry;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.core.content.FileProvider;
import androidx.fragment.app.Fragment;

import android.os.Environment;
import android.provider.MediaStore;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;

import com.cnil.dagas.databinding.FragmentUploadIdBinding;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;


public class UploadIdFragment extends Fragment {

    private static final int REQUEST_IMAGE_CAPTURE = 1 ;
    FragmentUploadIdBinding binding;

    //Based on: https://developer.android.com/training/camera/photobasics

    String currentPhotoPath;

    private File createImageFile() throws IOException {
        // Create an image file name
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = this.getActivity().getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        File image = File.createTempFile(
                imageFileName,  /* prefix */
                ".jpg",         /* suffix */
                storageDir      /* directory */
        );

        // Save a file: path for use with ACTION_VIEW intents
        currentPhotoPath = image.getAbsolutePath();
        return image;
    }

    private File dispatchTakePictureIntent() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

        // Ensure that there's a camera activity to handle the intent
        if (takePictureIntent.resolveActivity(this.getActivity().getPackageManager()) != null) {
            // Create the File where the photo should go
            File photoFile = null;
            try {
                photoFile = createImageFile();
            } catch (IOException ex) {
                // Error occurred while creating the File
            }
            // Continue only if the File was successfully created
            if (photoFile != null) {
                Uri photoURI = FileProvider.getUriForFile(this.getContext(),
                        "com.example.android.fileprovider",
                        photoFile);
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
            }
            return photoFile;
        } else{
            return null;
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
       binding = FragmentUploadIdBinding.inflate(inflater, container, false);
       View root = binding.getRoot();
       Button takePictureButton = root.findViewById(R.id.takePictureButton);
       ImageView idImageView = root.findViewById(R.id.idPicture);
       File photoFile = null;
       try {
            photoFile = createImageFile();
        } catch (IOException e) {
            e.printStackTrace();
        }
        File finalPhotoFile = photoFile;

        ActivityResultLauncher<Uri> mGetContent = registerForActivityResult(new ActivityResultContracts.TakePicture(),
                new ActivityResultCallback<Boolean>() {
                    @Override
                    public void onActivityResult(Boolean result) {
                        Bitmap idBitMap = BitmapFactory.decodeFile(finalPhotoFile.getAbsolutePath());
                        idImageView.setImageBitmap(idBitMap);
                    }
                });
        takePictureButton.setOnClickListener(new View.OnClickListener() {
           @Override
           public void onClick(View view) {
               // Continue only if the File was successfully created
               Uri photoURI = FileProvider.getUriForFile(UploadIdFragment.this.getContext(),
                       "com.example.android.fileprovider",
                       finalPhotoFile);
                mGetContent.launch(photoURI);


            }
       });
       return root;
    }
}