import '../App.css';
import { Component, useState, useEffect } from 'react';
import React from 'react';
import axiosConfig from "../axiosConfig";
import { useGoogleMap } from '@react-google-maps/api';
import { wait } from '@testing-library/user-event/dist/utils';


//  export  const  refreshEvacuationCenters = async () => {
//     console.log("Requesting for evacuation centers...");
//     var evacuationCenters;
//     const result = await axios
//       .get("/relief/api/evacuation-center/");
//     //   .then((result) => {evacuationCenters = result.data})
//     //   .catch((error) => console.log(error));
//     evacuationCenters = await result.data;
//     console.log(result.data);
//     return evacuationCenters;
    
//   };
var x = 0;
var y = 0;
export function setCoords(newX, newY){
    x = newX;
    y = newY;
}

export function getCenterX(){
    return x;
}

export function getCenterY(){
    return y;
}

// export function useNewMarkerLatLng(lat, lng){
//     const [newMarkerLat, changeMarkerLat] = useState(lat);
//     const [newMarkerLng, changeMarkerLng] = useState(lng);
//     return {lat: newMarkerLat, lng: newMarkerLng};
// }

export function RecenterMap() {
    const map = useGoogleMap();
    useEffect(() => {
        console.log("Recentering map...");
        if (map){
                map.panTo({lat: x, lng: y});
        }
    }, [map,x,y])
}