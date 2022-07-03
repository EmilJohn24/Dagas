package com.cnil.dagas;

import static android.app.Activity.RESULT_OK;

import static androidx.core.content.FileProvider.getUriForFile;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;

import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.ActivityResultRegistry;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
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
import com.cnil.dagas.http.OkHttpSingleton;
import com.cnil.dagas.ui.home.HomeActivity;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;


public class UploadIdFragment extends Fragment {
    private static final String UPLOAD_ID_URL = "/relief/api/users/residents/r/upload_id/";
    static class UploadId extends Thread{
        private File idImage;
        public UploadId(File idImage){
            this.idImage = idImage;
        }

        public void run(){
            try {
                upload();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }


        private void upload() throws IOException {
            RequestBody requestBody = new MultipartBody.Builder().setType(MultipartBody.FORM)
                    .addFormDataPart("file", idImage.getName(),
                            RequestBody.create(idImage, MediaType.parse("image/*")))
                    .addFormDataPart("some-field", "some-value")
                    .build();
            OkHttpSingleton client = OkHttpSingleton.getInstance();
            Request request = client.builderFromBaseUrl(UPLOAD_ID_URL)
                    .put(requestBody)
                    .build();
            Response response = client.newCall(request).execute();
        }
    }
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

    public static void copyStream(InputStream input, OutputStream output) throws IOException {
        byte[] buffer = new byte[1024];
        int bytesRead;
        while ((bytesRead = input.read(buffer)) != -1) {
            output.write(buffer, 0, bytesRead);
        }
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
                Uri photoURI = getUriForFile(this.getContext(),
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
       Button uploadButton = root.findViewById(R.id.uploadButton);
       Button albumButton = root.findViewById(R.id.albumButton);
       ImageView idImageView = root.findViewById(R.id.idPicture);
       File photoFile = null;
       try {
            photoFile = createImageFile();
        } catch (IOException e) {
            e.printStackTrace();
        }
        final File[] finalPhotoFile = {photoFile};

        ActivityResultLauncher<Uri> mGetContent = registerForActivityResult(new ActivityResultContracts.TakePicture(),
                new ActivityResultCallback<Boolean>() {
                    @Override
                    public void onActivityResult(Boolean result) {
                        Bitmap idBitMap = BitmapFactory.decodeFile(finalPhotoFile[0].getAbsolutePath());
                        idImageView.setImageBitmap(idBitMap);
                    }
                });
        takePictureButton.setOnClickListener(new View.OnClickListener() {
           @Override
           public void onClick(View view) {
               // Continue only if the File was successfully created
               Uri photoURI = getUriForFile(UploadIdFragment.this.getContext(),
                       "com.example.android.fileprovider",
                       finalPhotoFile[0]);
                mGetContent.launch(photoURI);


            }
       });

//        // GetContent creates an ActivityResultLauncher<String> to allow you to pass
//        // in the mime type you'd like to allow the user to select
//        ActivityResultLauncher<String> gGetContent = registerForActivityResult(new ActivityResultContracts.GetContent(),
//                new ActivityResultCallback<Uri>() {
//                    @Override
//                    public void onActivityResult(Uri uri) {
//                        idImageView.setImageURI(uri);
//                    }
//                });
        //Based on: https://stackoverflow.com/questions/67156608/how-get-image-from-gallery-in-fragmentjetpack-navigation-component
        ActivityResultLauncher<Intent> startForResultFromGallery = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
                new ActivityResultCallback<ActivityResult>() {
            @Override
            public void onActivityResult(ActivityResult result) {
                if (result.getResultCode() == Activity.RESULT_OK){
                    if (result.getData() != null){
                        Uri selectedImageUri = result.getData().getData();
//                        File galleryPhotoFile = new File(selectedImageUri.getPath());
                        try {
                            InputStream inputStream = getActivity().getContentResolver().openInputStream(selectedImageUri);
                            FileOutputStream fileOutputStream = new FileOutputStream(finalPhotoFile[0]);
                            copyStream(inputStream,  fileOutputStream);
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
//                        finalPhotoFile[0] = new File(selectedImageUri.getPath());
                        idImageView.setImageURI(selectedImageUri);
                    }
                }
            }
        });
        albumButton.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v) {
//                gGetContent.launch("images/*");
//                  Uri photoURI =FileProvider.getUriForFile(UploadIdFragment.this.getContext(),
//                        "com.example.android.fileprovider",
//                        finalPhotoFile);
                  Intent intent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
//                  intent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                  startForResultFromGallery.launch(intent);
            }
        });


        uploadButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                UploadId thread = new UploadId(finalPhotoFile[0]);
                thread.start();
            }
        });
       return root;
    }
}