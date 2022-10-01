package com.cnil.dagas.placeholder;

import com.google.android.gms.maps.model.LatLng;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Helper class for providing sample content for user interfaces created by
 * Android template wizards.
 * <p>
 * TODO: Replace all uses of this class before publishing your app.
 */
public class Suggestion {

    /**
     * An array of sample (placeholder) items.
     */
    public static final List<SuggestionNode> ITEMS = new ArrayList<SuggestionNode>();

    /**
     * A map of sample (placeholder) items, by ID.
     */
    public static final Map<String, SuggestionNode> ITEM_MAP = new HashMap<String, SuggestionNode>();

    private static final int COUNT = 25;

    static {
        // Add some sample items.
//        for (int i = 1; i <= COUNT; i++) {
//            addItem(createPlaceholderItem(i));
//        }
    }

    private static void addItem(SuggestionNode item) {
        ITEMS.add(item);
        ITEM_MAP.put(item.id, item);
    }

//    private static SuggestionNode createPlaceholderItem(int position) {
//        return new SuggestionNode(String.valueOf(position), "Item " + position, makeDetails(position));
//    }

    private static String makeDetails(int position) {
        StringBuilder builder = new StringBuilder();
        builder.append("Details about Item: ").append(position);
        for (int i = 0; i < position; i++) {
            builder.append("\nMore details information here.");
        }
        return builder.toString();
    }

    /**
     * A placeholder item representing a piece of content.
     */
    public static class SuggestionNode {
        public final String id;
        public final String suggestedBarangayName;
        public final String suggestedEvacuationCenterName;
        public final Map<String, Integer> fulfillments;
        public final double distancefromprevious;
        private final LatLng evacCoordinate;

        public void addFulfillment(String itemType, Integer amount){
            fulfillments.put(itemType, amount);
        }
        public SuggestionNode(String id, String suggestedBarangayName, String suggestedEvacuationCenterName, LatLng evacCoordinate, double distance) {
            this.id = id;
            this.suggestedBarangayName = suggestedBarangayName;
            this.suggestedEvacuationCenterName = suggestedEvacuationCenterName;
            this.evacCoordinate = evacCoordinate;
            this.distancefromprevious = distance;
            fulfillments = new HashMap<>();
        }


        @Override
        public String toString() {
            return suggestedBarangayName;
        }

        public LatLng getEvacCoordinate() {
            return evacCoordinate;
        }
    }
}