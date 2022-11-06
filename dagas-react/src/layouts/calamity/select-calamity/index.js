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
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import Autocomplete from "@mui/material/Autocomplete";
import { Paper, Typography, Button } from '@mui/material';

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";

// Material Dashboard 2 PRO React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

//React
import { useEffect, useState } from "react";
import { Formik, useFormik } from "formik";
import * as Yup from 'yup';

//Carousel
import Carousel from 'react-material-ui-carousel'
import { CImage } from '@coreui/react'

//AXIOS and navigation
import { useAxios } from 'axiosConfig';
import axiosConfig from "axiosConfig";
import logo from 'logo.svg';
import { Navigate } from "react-router-dom";
import { Avatar, darkScrollbar, Icon } from "@mui/material";
import { Map, GoogleApiWrapper, InfoWindow, Marker } from 'google-maps-react';
import usePlacesService from "react-google-autocomplete/lib/usePlacesAutocompleteService";
import { geocodeByPlaceId } from "react-google-places-autocomplete";


//Image imports
import tip1 from "assets/images/tip1.png";
import tip2 from "assets/images/tip2.png";
import tip3 from "assets/images/tip3.png";
import tip4 from "assets/images/tip4.png";
import tip5 from "assets/images/tip5.png";


function Calamities({ google, locations = [] }) {

  const [disasterForm, setDisasterForm] = useState(() => {
    return "Loading...";
  });
  const [showingInfoWindow, setShowingInfoWindow] = useState(false);
  const [activeMarker, setActiveMarker] = useState({});
  const [selectedPlace, setSelectedPlace] = useState({});
  const [clickMarkerCoord, setClickMarkerCoord] = useState(null);
  const [isEditing, setEditing] = useState(() => false);
  // Loading item types
  const [{data, loading, error}, refetch] = useAxios("/relief/api/evacuation-center/");
  const [chosenDisaster, setChosenDisaster] = useState(null);
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

  const [{data: currUser, loading: currUserLoad, error: currUserError}, refetchCurrUser] = useAxios("/relief/api/users/current_user/");
  
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

  const mapStyles = {
      position: "relative",
      width: '100%',
      height: '100%'
  };
  var evacMarkerRender = null;
  if (chosenDisaster){
      evacMarkerRender = data?.map((evac_data) => {
        if (evac_data.disaster == chosenDisaster){
          const [lat, lng]= evac_data.geolocation.split(',');
          const geoloc = {lat: lat, lng, lng};
          return <Marker
                      onClick={onMarkerClick}
                      name={evac_data.name}
                      position={geoloc}
                      />
        }
      })
  } else {
    evacMarkerRender = data?.map((evac_data) => {
        const [lat, lng]= evac_data.geolocation.split(',');
        const geoloc = {lat: lat, lng, lng};
        return <Marker
                    onClick={onMarkerClick}
                    name={evac_data.name}
                    position={geoloc}
                    />
    });
  }

  // Disaster Name insertion effect
  useEffect(() =>{
    if (disasterError || currUserError) setDisasterForm("Something went wrong...");
    else if (!disasterLoading && !currUserLoad && disasterArray) {
      console.log(disasterArray);
      const disasterNames = disasterArray.map(type => type.name);
      console.log(disasterNames);
      var initVals = {
        type: disasterNames[0]
    };
    let formHeader = (
      <MDTypography variant="h4">Calamities Open for Donation</MDTypography>
    );
      const DisasterTypeWrapped = ( 
        <Formik
                enableReinitialize={true}
                initialValues={initVals}
                onSubmit={async (values, {setSubmitting}) => {
                    // var requestValues = {...values}; //copy the data to preprocess
                    console.log(values);
                    var requestValues = {};
                    requestValues["type"] = disasterArray.filter(item => item.name == values.type)[0].id;
                    console.log(JSON.stringify(requestValues));
                    //Refetch supplies
                    setSubmitting(false);
                   
                    //   return result;                     
                } }
                >
                {
                formik => (
                  <MDBox px={70}>
                      <Card sx={{ overflow: "visible" }}>
                        <MDBox p={3}>
                          {formHeader}
                        <MDBox mt={1}>
                          <Grid container spacing={1}>
                            <Grid item xs={12} sm={12}>
                              <MDBox mb={1}>
                                <MDBox mb={1} display="inline-block">
                                  <MDTypography
                                    component="label"
                                    variant="button"
                                    fontWeight="regular"
                                    color="text"
                                    textTransform="capitalize"
                                  >
                                    Calamity
                                  </MDTypography>
                                </MDBox>
                                <Autocomplete
                                  name="type"
                                  id="type"
                                  options={disasterArray}
                                  defaultValue={currUser.current_disaster}
                                  getOptionLabel={option => option.name}
                                  onChange={async (event, value) => {
                                    console.log(`Changing to ${value}...`)
                                    formik.setFieldValue('type', value.name);
                                    const result = await axiosConfig
                                      .get(`/relief/api/disasters/${value.id}/change_to_disaster/`)
                                      .then((res) => {
                                        console.log(res);
                                      })
                                      .catch((error) => console.log(error));   
                                  }}
                                  renderInput={(params) => {
                                      return (
                                        <MDBox>
                                          <MDInput {...params} onChange={formik.handleChange} variant="standard" />
                                        </MDBox>
                                      );
                                    }
                                  }
                                />
                              </MDBox>
                            </Grid>
                          </Grid>
                        </MDBox>
                      </MDBox>
                      </Card>
                  </MDBox>
                        )}
                </Formik>
          )

      setDisasterForm(DisasterTypeWrapped);
      
    }
}, [disasterLoading, disasterError, disasterArray, currUserError, currUserLoad, currUser]);

  const mapRender = (
    <MDBox p={3} >
      <Grid spacing={2} p={1} container style={{backgroundColor: '#ffffff' }}>
          <Grid xs={12} p={1} container justifyContent="center">
              <div style={{ width: 1500, height: 1000 }}>
                  <Map
                      google={google}
                      zoom={14}
                      containerStyle={mapStyles}
                      center={clickMarkerCoord}
                      onClick={onMapClick}
                      initialCenter={
                          clickMarkerCoord? clickMarkerCoord :{
                              lat: 14.546047,
                              lng: 121.069761
                          }
                      }
                  >
                      {evacMarkerRender}
                      {/* <Marker
                          position={clickMarkerCoord}
                          draggable={false}
                          onDragEnd={onClickMarkerDragged}
                          /> */}
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

  console.log(`Loading type array: ${disasterArray}`);
  if (isPlacePredictionsLoading || loading || disasterLoading) return;
  if (error || disasterError) return <Navigate to="/login"/>;
  
  //FROM https://coreui.io/react/docs/components/carousel/#how-it-works
  const carouselRender = (
    <MDBox>
      <Carousel>
        <Paper>
          <CImage className="d-block w-100" src={tip1} alt="Tip 1" />
        </Paper>
        <Paper>
          <CImage className="d-block w-100" src={tip2} alt="Tip 2" />
        </Paper>
        <Paper>
          <CImage className="d-block w-100" src={tip3} alt="Tip 3" />
        </Paper>
        <Paper>
          <CImage className="d-block w-100" src={tip4} alt="Tip 4" />
        </Paper>
        <Paper>
          <CImage className="d-block w-100" src={tip5} alt="Tip 5" />
        </Paper>
      </Carousel>
    </MDBox>
  )
  
  return (
    <DashboardLayout>
      <DashboardNavbar />
      {disasterForm}
      {mapRender}
      <MDBox mx={50}>
        {carouselRender}
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default GoogleApiWrapper({
  apiKey: 'AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM'
})(Calamities);
