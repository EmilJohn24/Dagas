//react 
import { useState, useEffect } from "react";
import * as React from 'react';
import { Formik, useFormik } from "formik";
import * as Yup from 'yup';

// @mui material components
import Grid from "@mui/material/Grid";

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 PRO React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

//AXIOS and navigation
import axiosConfig from "axiosConfig";
import { useAxios } from 'axiosConfig';

import { Navigate } from "react-router-dom";
import { Avatar, darkScrollbar, Icon, List, ListItem, ListItemAvatar, ListItemButton, ListItemText, TextField } from "@mui/material";

import { Map, GoogleApiWrapper, InfoWindow, Marker } from 'google-maps-react';

import FormField from "./components/FormField";
import MDButton from "components/MDButton";
import usePlacesService from "react-google-autocomplete/lib/usePlacesAutocompleteService";
import { geocodeByPlaceId } from "react-google-places-autocomplete";

// Documentation: https://developers.google.com/maps/documentation/javascript/react-map
function EvacuationMap({ google, locations = [] }){
        const [showingInfoWindow, setShowingInfoWindow] = useState(false);
        const [activeMarker, setActiveMarker] = useState({});
        const [selectedPlace, setSelectedPlace] = useState({});
        const [clickMarkerCoord, setClickMarkerCoord] = useState(null);
        const [{data, loading, error}, refetch] = useAxios("/relief/api/evacuation-center/");
        const [{data: profileData, loading: profileLoading, error: profileError}, refetchProfile] = useAxios("/relief/api/users/current_user/");
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

        const [{data: postEvacuationCenter, loading: postLoading, error: postError}, executeEvacuationCenter] = useAxios({
            url: "/relief/api/evacuation-center/",
            method: "POST"
        }, {  manual: true  });

        console.log(clickMarkerCoord);
        console.log(placePredictions);
        console.log(data);
        if (loading || profileLoading) return;
        if (error || profileError) return <Navigate to="/login"/>;
        
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

        const mapStyles = {
            position: "relative",
            width: '100%',
            height: '100%'
        };
        const evacMarkerRender = data.map((evac_data) => {
            const [lat, lng]= evac_data.geolocation.split(',');
            const geoloc = {lat: lat, lng, lng};
            return <Marker
                        onClick={onMarkerClick}
                        name={<>
                            <h4>{evac_data.barangay_name}</h4>
                            <h5>{evac_data.name}</h5>
                            </>}
                        position={geoloc}
                        />
        });
        
        const formikRender = (
            <Formik
                    initialValues={{
                      'name': '',
                      'address': '',
                    }}
                    validationSchema={Yup.object().shape({
                        name: Yup
                          .string()
                          .required(),
                        address: Yup
                          .string()
                          .required(),
                  })}
                  onSubmit={
                    (values, {setSubmitting}) => {
                        console.log(values);
                        console.log(clickMarkerCoord);
                        var requestValues = {};
                        requestValues["name"] = values.name;
                        requestValues["address"] = values.address;
                        requestValues["geolocation"] = clickMarkerCoord.lat + "," + clickMarkerCoord.lng;

                        executeEvacuationCenter({
                            data: requestValues
                        });

                        //Refetch evacuation centers
                        refetch();
                        // setSubmitting(false);
                    }
                  }>{
                      (formik) => (
                            <>
                                <MDTypography variant="h4" fontWeight="medium">
                                    Evacuation Details
                                </MDTypography>
                                <FormField id="name" type="text" label="Name" {...formik.getFieldProps('name')} />
                                {/* <ReactGoogleAutocomplete
                                    id="address"
                                    
                                    {...formik.getFieldProps('address')}
                                /> */}
                                <FormField id="address" type="text" 
                                    label="Address" 
                                    {...formik.getFieldProps('address')} 
                                    onChange={(event) => {
                                        formik.handleChange(event);
                                        getPlacePredictions({ input: event.target.value });
                                    }} 
                                    loading={isPlacePredictionsLoading}/>
                                    <List sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
                                        {
                                            placePredictions.map(({structured_formatting, description, place_id}) => {
                                                return (
                                    
                                                <ListItemButton onClick={(event) => {
                                                    console.log(description);
                                                    formik.setFieldValue('address', description);
                                                    geocodeByPlaceId(place_id)
                                                        .then(results => {
                                                            const coord = {lat: results[0].geometry.location.lat(), 
                                                                        lng: results[0].geometry.location.lng()};
                                                            setClickMarkerCoord(coord);
                                                        });
                                                }}>
                                                    <ListItemAvatar>
                                                        <Avatar>
                                                        <Icon>map marker</Icon>
                                                        </Avatar>
                                                    </ListItemAvatar>
                                                    <ListItemText primary={structured_formatting.main_text} secondary={structured_formatting.secondary_text} />
                                                </ListItemButton>)
                                            })
                                        }
                                </List>
                                <MDButton variant="gradient" color="info" type="submit" onClick={formik.handleSubmit}>
                                    Add
                                </MDButton>
                            </>
                  )}</Formik>
        );

        console.log(profileData.role_verbose);
        console.log(profileData.role_verbose == 'Barangay');
        return profileData.role_verbose == 'Barangay' ? (
            <DashboardLayout>
                <DashboardNavbar />
                    <MDBox p={10} mr={2}>
                        <Grid spacing={2} p={2} container style={{backgroundColor: '#ffffff' }}>
                            <Grid xs={9} p={3} container justifyContent="center">
                                <div style={{ width: 1000, height: 1000 }}>
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
                                        {/* <Marker
                                            onClick={onMarkerClick}
                                            name={'Kenyatta International Convention Centre'}
                                        /> */}
                                        {evacMarkerRender}
                                        <Marker
                                            position={clickMarkerCoord}
                                            draggable={true}
                                            onDragEnd={onClickMarkerDragged}
                                            />
                                        <InfoWindow
                                            marker={activeMarker}
                                            visible={showingInfoWindow}
                                            onClose={onClose}>
                                            <div>
                                                <h5>{selectedPlace.name}</h5>
                                            </div>
                                        </InfoWindow>
                                    </Map>
                                </div>
                            </Grid>
                            <Grid xs={3} p={1}>
                                {formikRender}
                            </Grid>
                        </Grid>
                    </MDBox>
                <Footer />
            </DashboardLayout>
        ) : (
            <DashboardLayout>
                <DashboardNavbar />
                    <MDBox p={10} mr={2}>
                        <Grid spacing={1} p={2} container style={{backgroundColor: '#ffffff' }}>
                            <Grid xs={12} p={3} container justifyContent="center">
                                <div style={{ width: 1000, height: 1000 }}>
                                    <Map
                                        google={google}
                                        zoom={14}
                                        containerStyle={mapStyles}
                                        center={clickMarkerCoord}
                                        initialCenter={
                                            clickMarkerCoord? clickMarkerCoord :{
                                                lat: 14.546047,
                                                lng: 121.069761
                                            }
                                        }
                                    >
                                        {/* <Marker
                                            onClick={onMarkerClick}
                                            name={'Kenyatta International Convention Centre'}
                                        /> */}
                                        {evacMarkerRender}
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
                <Footer />
            </DashboardLayout>
        );
    
}

export default GoogleApiWrapper({
    apiKey: 'AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM'
})(EvacuationMap);