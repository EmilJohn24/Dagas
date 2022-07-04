import '../App.css';
import { Component } from 'react';
import axios from "axios";
import { Wrapper, Status } from "@googlemaps/react-wrapper";
//Based on standard implementation on: https://developers.google.com/maps/documentation/javascript/react-map#javascript_3

const ref = React.useRef(null);
const [map, setMap] = React.useState();

//effects
React.useEffect(() => {
  if (ref.current && !map) {
    setMap(new window.google.maps.Map(ref.current, {}));
  }
}, [ref, map]);

React.useEffect(() => {
    if (map) {
      ["click", "idle"].forEach((eventName) =>
        google.maps.event.clearListeners(map, eventName)
      );
      if (onClick) {
        map.addListener("click", onClick);
      }
  
      if (onIdle) {
        map.addListener("idle", () => onIdle(map));
      }
    }
  }, [map, onClick, onIdle]);

const Marker = (options) => {
    const [marker, setMarker] = React.useState();

    React.useEffect(() => {
        if (!marker) {
        setMarker(new google.maps.Marker());
        }

        // remove marker from map on unmount
        return () => {
        if (marker) {
            marker.setMap(null);
        }
        };
    }, [marker]);


    React.useEffect(() => {
        if (marker) {
        marker.setOptions(options);
        }
    }, [marker, options]);
    return null;
};


useDeepCompareEffectForMaps(() => {
    if (map) {
      map.setOptions(options);
    }
  }, [map, options]);