import '../App.css';
import { Component, useState, useEffect } from 'react';
import React from 'react';
import axios from "axios";
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
export function RecenterMap() {
    const map = useGoogleMap();
    React.useEffect(() => {
        if (map){
                map.panTo({lat: x, lng: y});
        }
    }, [map,x,y])
}