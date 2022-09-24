/**
=========================================================
* Material Dashboard 2 PRO React - v2.1.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-pro-react
* Copyright 2022 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Divider from "@mui/material/Divider";
import LocalShippingIcon from '@mui/icons-material/LocalShipping';

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";

// Material Dashboard 2 PRO React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import TimelineItem from "examples/Timeline/TimelineItem";

// OrderDetails page components
import Header from "layouts/suggestions/components/Header";
import OrderInfo from "layouts/suggestions/components/OrderInfo";
import TrackOrder from "layouts/suggestions/components/TrackOrder";
import PaymentDetails from "layouts/suggestions/components/PaymentDetails";
import BillingInformation from "layouts/suggestions/components/BillingInformation";
import OrderSummary from "layouts/suggestions/components/OrderSummary";

//React
import { useEffect, useState } from "react";


//AXIOS and navigation
import axiosConfig from "axiosConfig";
import LRU from 'lru-cache';
import {configure} from 'axios-hooks';
import useAxios from 'axios-hooks';
import { Navigate } from "react-router-dom";
import { Avatar, darkScrollbar, Icon } from "@mui/material";
import { Map, GoogleApiWrapper, InfoWindow, Marker } from 'google-maps-react';
import usePlacesService from "react-google-autocomplete/lib/usePlacesAutocompleteService";
import { geocodeByPlaceId } from "react-google-places-autocomplete";
import icon from "assets/theme/components/icon";

function Suggestions({ google, locations = [] }) {

  const cache = new LRU({max: 10})
  configure({axiosConfig, cache});
  // Loading item types
  const [{data, loading, error}, refetch] = useAxios("/relief/api/evacuation-center/");
  const [{data:suggestionData, loading:suggestionLoading, error:suggestionError}, suggestionRefetch] = useAxios("/relief/api/suggestions/");
  const [{data:suppliesData, loading:suppliesLoading, error:suppliesError}, suppliesRefetch] = useAxios("/relief/api/supplies/current_supplies/");
  const [disasterForm, setDisasterForm] = useState(() => {
    return "Loading...";
  });
  const [showingInfoWindow, setShowingInfoWindow] = useState(false);
  const [activeMarker, setActiveMarker] = useState({});
  const [selectedPlace, setSelectedPlace] = useState({});
  const [clickMarkerCoord, setClickMarkerCoord] = useState(null);
  const [userLatitude, setUserLatitude] = useState(null);
  const [userLongitude, setUserLongitude] = useState(null);
  const [donorSup, setDonorSup] = useState("");
  const driverMarker = new window.google.maps.Marker(
    
  )
  const {
      placesService,
      placePredictions,
      getPlacePredictions,
      isPlacePredictionsLoading,
    } = usePlacesService({
      apiKey: 'AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM',
      onPlaceSelected: (place, inputRef, autocomplete) => {
          console.log(autocomplete);
      },
      options: {
          componentRestrictions: { country: "ph" },
      }
      
  })
  console.log(clickMarkerCoord);
  console.log(placePredictions);
  console.log(data);
  const [{data: disasterArray, loading: disasterLoading, error: disasterError}, refetchTypes] = useAxios("/relief/api/disasters/");

  const onMarkerClick = (props, marker, e) =>{
    setSelectedPlace(props);
    setActiveMarker(marker);
    setShowingInfoWindow(true);
  };  

  const onMapClick = (t, map, coord) => {
      setClickMarkerCoord(coord.latLng);
  }

  const onClickMarkerDragged = (t, map, coord) => {onMapClick(t, map, coord)};

  const onClose = (props) => {
      if (this.state.showingInfoWindow) {
          setShowingInfoWindow(false);
          setActiveMarker(null);

      }
  };
// Get user position
  function getLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(showPosition);
    } else {
      alert("Geolocation is not supported by this browser.");
    }
  }
  
  function showPosition(position) {
    setUserLatitude(position.coords.latitude);
    setUserLongitude(position.coords.longitude);
    console.log(userLatitude);
    console.log(userLongitude);
  }

  useEffect(() => {
    getLocation();
    if (suppliesError) return;
    else if (!suppliesLoading && suppliesData) {
      console.log(suppliesData);
      const suppliesList = suppliesData.map(type => type.type_str);
      const suppliesQty = suppliesData.map(type => type.available_pax);
      console.log(suppliesList);
      console.log(suppliesQty.length);
      var str = "";
      for (let i = 0; i < suppliesList.length; i++) {
        str += `${suppliesList[i]}: ${suppliesQty[i]} `
      }
      setDonorSup(str);

      //setDonorSup(...donorSup, `${suppliesList[i]}: ${suppliesQty[i]}`);
    }
  }, [suppliesLoading,suppliesData,suppliesError]);

  const mapStyles = {
      position: "relative",
      width: '100%',
      height: '100%'
  };
  const evacMarkerRender = data?.map((evac_data) => {
      const [lat, lng]= evac_data.geolocation.split(',');
      const geoloc = {lat: lat, lng, lng};
      return <Marker
                  onClick={onMarkerClick}
                  name={evac_data.name}
                  position={geoloc}
                  />
  });


  const renderHeader = (
    <MDBox display="flex" justifyContent="space-between" alignItems="center">
      <MDBox>
        <MDBox mb={1}>
          <MDTypography variant="h4" fontWeight="medium">
            Dagas Recommendation
          </MDTypography>
        </MDBox>
        <MDTypography component="p" variant="button" color="text">
          Donor Supplies:
        </MDTypography>
        <MDTypography component="p" variant="h6" fontWeight="regular" color="text">
          {donorSup}
        </MDTypography>
      </MDBox>
      <MDButton variant="gradient" color="dark" >
        Accept
      </MDButton>
    </MDBox>
  )

  const renderSuggestedEvacs = (
    <>
      <MDTypography variant="h6" fontWeight="medium">
        Donations To Make
      </MDTypography>
      <MDBox mt={2}>
        <TimelineItem
          color="info"
          icon="local_shipping"
          title="Evacuation Center: Mall of Asia"
          description="Food: 1000 Water: 2000 Clothes: 100"
          dateTime="22 DEC 7:20 PM" // Deadline of delivery?
        />
        <TimelineItem
          color="info"
          icon="local_shipping"
          title="Evacuation Center: NAIA 3"
          description="Food: 200 Water: 100 Clothes: 10"
          dateTime="22 DEC 7:20 PM" // Deadline of delivery?
        />
      </MDBox>
    </>
  )

  const renderMap = (
    <MDBox p={2} >
      <Grid spacing={2} p={1} container style={{backgroundColor: '#ffffff' }}>
          <Grid xs={12} p={1} container justifyContent="center">
              <div style={{ width: 1500, height: 500 }}>
                  <Map
                      google={google}
                      zoom={14}
                      containerStyle={mapStyles}
                      center={clickMarkerCoord}
                      onClick={onMapClick}
                      initialCenter={
                          clickMarkerCoord? clickMarkerCoord :{
                              lat: userLatitude,
                              lng: userLongitude
                          }
                      }
                  >
                      {evacMarkerRender}
                      <Marker
                          position={clickMarkerCoord}
                          draggable={false}
                          />
                      <InfoWindow
                          marker={activeMarker}
                          visible={showingInfoWindow}
                          onClose={onClose}>
                          <div>
                              <h4>{selectedPlace.name}</h4>
                          </div>
                      </InfoWindow>
                  </Map>
              </div>
          </Grid>
      </Grid>
  </MDBox>
  ) 

  if (loading||suppliesLoading) return;
  if (error||suppliesError) return <Navigate to="/login"/>;
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mt={2} mb={100}>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} lg={8}>
            <Card>
              <MDBox pt={2} px={2}>
                {renderHeader}
              </MDBox>
              <Divider />
              <MDBox pb={3} px={2}>
                <MDBox mt={3}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6} lg={3}>
                    {renderSuggestedEvacs}
                    </Grid>
                    <Grid item xs={12} md={6} lg={9}>
                      {renderMap}
                    </Grid>
                  </Grid>
                </MDBox>
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default GoogleApiWrapper({
  apiKey: 'AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM'
})(Suggestions);
