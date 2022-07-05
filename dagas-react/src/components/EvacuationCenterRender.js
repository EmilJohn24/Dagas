import '../App.css';
import { Component, useState, useEffect } from 'react';
import React from 'react';
import axios from "axios";
import { GoogleMap, LoadScript, Marker, useGoogleMap, useJsApiLoader } from '@react-google-maps/api';
import { wait } from '@testing-library/user-event/dist/utils';
import Select from 'react-select'
import { getCenterX, getCenterY, RecenterMap, recenterMap, refreshEvacuationCenters, setCoords } from './EvacuationCenterHelper';
//Based on: https://react-google-maps-api-docs.netlify.app
//Properties


const containerStyle = {
  width: '1000px',
  height: '1000px'
};

const options = {
  zoomControlOptions: {
    // position: window.google.maps.ControlPosition.RIGHT_CENTER // 'right-center' ,
    // ...otherOptions
  }
}

const center = {
  lat: -3.745,
  lng: -38.523
};

function InternalEvacuationCenter() {

  var updateCount = 0;
  const [evacuationCenters, setEvacuationCenters] = useState([]);
  const [isEvacuationCenterLoading, setLoading] = useState(true);
  const [evacuationSelectInput, changeEvacuationSelectInput] = useState(null);
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: "AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM" // ,
    // ...otherOptions
  })

  
 const refreshEvacuationCenters = () => {
    console.log("Requesting for evacuation centers...");
    axios
      .get("/relief/api/evacuation-center/")
      .then((result) => {
        setEvacuationCenters(result.data);
        setLoading(false);
      })
      .catch((error) => console.log(error));
  }
  
//   };
  useEffect(() => {
    refreshEvacuationCenters();
  
  }, [])    
  //Use Default value
  useEffect(() => {
    if (evacuationCenters && evacuationCenters.length > 0){
      setCoords(parseFloat(evacuationCenters.at(0).geolocation.split(",")[0]), parseFloat(evacuationCenters.at(0).geolocation.split(",")[1]));
      // RecenterMap();
    }
  }, [evacuationCenters])
  
  //Respond to changes in drop down
  // useEffect(() => {
  //   console.log(evacuationSelectInput);
  //   if (evacuationSelectInput)
  //     setCoords(parseFloat(evacuationSelectInput.value.split(",")[0]), parseFloat(evacuationSelectInput.value.split(",")[1]));
  //   console.log("New X: " + getCenterX());
  //   console.log("New Y: " + getCenterY());
  // }, [evacuationSelectInput]);




  const renderEvacuationCenter = () => {
    return  evacuationCenters.map((item) => {
      // console.log( item.geolocation);
      return(<Marker
        icon={{
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 7,
        }}
        label={item.name}
        position={{lat: parseFloat(item.geolocation.split(",")[0]), 
                  lng: parseFloat(item.geolocation.split(",")[1])}}
        />
      )
    })
  }
  

  // const useMap = () => {
    // wrapping to a function is useful in case you want to access `window.google`
    // to eg. setup options or create latLng object, it won't be available otherwise
    // feel free to render directly if you don't need that
    updateCount += 1;
    const onLoad = React.useCallback(
      function onLoad (mapInstance) {
        // do something with map Instance
        // mapInstance.data = evacuationCenters;
        
      }
    )
    const retrieveOptions = () => {
      console.log("Loading selector items...");
      console.log(evacuationCenters);
      var optionArray = Array.from(evacuationCenters, (evacuationCenter) => {
        return {'value': evacuationCenter.geolocation, 'label': evacuationCenter.name};
      });
      console.log(optionArray);
      return optionArray;
    }

    const handleSelectorChange = (selectedOption) => {
      changeEvacuationSelectInput(selectedOption);
      if (selectedOption)
        setCoords(parseFloat(selectedOption.value.split(",")[0]), parseFloat(selectedOption.value.split(",")[1]));
      console.log("New X: " + getCenterX());
      console.log("New Y: " + getCenterY());
      console.log("New Selected Name: " + selectedOption.label);
      console.log("Selected: " + selectedOption.toString());
    }
    
    if (isEvacuationCenterLoading && !isLoaded) return <div className="map">Loading...</div>
    // Documentation for react-select: https://react-select.com/home
    else return (
    // <LoadScript googleMapsApiKey="AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM">
    <div className="map_container">
      <GoogleMap
        mapContainerStyle={containerStyle}
        zoom={20}
        center={center}
        options={options}
        onLoad={onLoad}>
        {
          // ...Your map components
          renderEvacuationCenter()
        }
        <RecenterMap/>
        <Select 
          options={retrieveOptions()} 
          onChange={handleSelectorChange}
        />

      </GoogleMap>

      </div>

    // </LoadScript>
    )
  // }

  // if (loadError) {
  //   return <div>Map cannot be loaded right now, sorry.</div>
  // }
  // return useMap();
  // return isLoaded ? useMap() : <Spinner />
}
export default InternalEvacuationCenter;
