import '../App.css';
import { Component } from 'react';
import React from 'react';
import axios from "axios";
import { GoogleMap, LoadScript, Marker, useGoogleMap } from '@react-google-maps/api';
//Based on: https://react-google-maps-api-docs.netlify.app
//Properties

const google = window.google;


const containerStyle = {
  width: '1000px',
  height: '1000px'
};

const center = {
  lat: -3.745,
  lng: -38.523
};

class EvacuationCenter extends Component{
  //retrieves the attributes of the tag and initializes the object
  constructor(props){
    super(props);
    this.state = {
      viewCompleted: false,
      evacuationCenters: [],
    }    
    this.googleMap = React.createRef();
  };
  refreshEvacuationCenters = () => {
    console.log("Requesting for evacuation centers...");
    axios
      .get("/relief/api/evacuation-center/")
      .then((result) => this.setState({evacuationCenters: result.data}))
      .catch((error) => console.log(error));
  }
  renderEvacuationCenter = () => {
    if (this.state.evacuationCenters.length != 0){
      center.lat = this.state.evacuationCenters.at(0).geolocation.split(",")[0];
      center.lng = this.state.evacuationCenters.at(0).geolocation.split(",")[1];
      // useGoogleMap().panTo(center);
      // this.map({center: center});
    }
    console.log(this.googleMap);

    return this.state.evacuationCenters.map((item) => {
      console.log( parseFloat(item.geolocation.split(",")[0]));
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
  //runs when component works
  componentDidMount(){
    this.refreshEvacuationCenters();
  }

  //runs when class tag is called elsewhere
  render(){
    
    // var [x,y] = this.state.evacuationCenters.at(0).geolocation.split(",");
    // [center.lat, center.lng] = [parseFloat(x), parseFloat(y)];

    return (
      // <main className="container">
      //   <h1>Evacuation Centers</h1>
      //   <ul className="list-group">{this.renderEvacuationCenter()}</ul>
      // </main>
      <LoadScript
        googleMapsApiKey="AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM"
      >
        <GoogleMap ref={this.googleMap}
          mapContainerStyle={containerStyle}
          center={center}
          zoom={10}>
            
          { this.renderEvacuationCenter() }
          
        </GoogleMap>
      </LoadScript>
    )
  }


}
export default EvacuationCenter;
