package com.cnil.dagas;

import android.util.Log;

import com.cnil.dagas.http.OkHttpSingleton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.lang.reflect.Array;
import java.util.ArrayList;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

class RetrieveItemTypesThread extends Thread{
    private static final String TYPE_URL = "/relief/api/item-type/";
    private final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
    private final ArrayList<String> types;
    private final ArrayList<Integer> typeIds;
    private final ArrayList<JSONObject> typeJSONs;

    public RetrieveItemTypesThread() {
        this.typeJSONs = new ArrayList<>();
        this.types = new ArrayList<>();
        this.typeIds = new ArrayList<>();
    }

    public ArrayList<String> getTypes() {
        return this.types;
    }
    public ArrayList<Integer> getTypeIds(){ return this.typeIds;}
    public ArrayList<JSONObject> getTypeJSONs() { return this.typeJSONs; }
    public String getName(int index){return this.types.get(index);}

    public void run() {
        try {
            retrieveTypesFromServer();
        } catch (IOException | JSONException e) {
            Log.e(RetrieveItemTypesThread.class.getName(), e.getMessage());
        }
    }

    private void retrieveTypesFromServer() throws IOException, JSONException {
//            JSONObject createRequestJSON = new JSONObject();
        // JSON Form Handling:
        // https://stackoverflow.com/questions/17810044/android-create-json-array-and-json-object
        // https://stackoverflow.com/questions/23456488/how-to-use-okhttp-to-make-a-post-request
        // https://stackoverflow.com/questions/34179922/okhttp-post-body-as-json
//            try {
//                createRequestJSON.put("", "");
//            } catch (JSONException e) {
//                Log.e(TAG, e.getMessage());
//            }

        OkHttpSingleton client = OkHttpSingleton.getInstance();
//            RequestBody body = RequestBody.create(createRequestJSON.toString(), JSON);
        Request request = client.builderFromBaseUrl(TYPE_URL)
                .get()
                .build();
        Response response = client.newCall(request).execute();
        //TODO: Add success check
        JSONArray typeJSONArray = new JSONArray(response.body().string());
        for (int typeIndex = 0; typeIndex < typeJSONArray.length(); typeIndex++) {
            JSONObject typeJSONObject = typeJSONArray.getJSONObject(typeIndex);
            this.typeJSONs.add(typeJSONObject);
            this.types.add(typeJSONObject.getString("name"));
            this.typeIds.add(typeJSONObject.getInt("id"));
        }
    }

}
