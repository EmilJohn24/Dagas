import '../App.css';
import { Component, useState, useEffect } from 'react';
import React from 'react';
import axios from "axios";
import { GoogleMap, LoadScript, Marker, useGoogleMap, useJsApiLoader } from '@react-google-maps/api';
import Select from 'react-select'
import { Form, Formik, Field } from 'formik';

import { getCenterX, getCenterY, RecenterMap, recenterMap, refreshEvacuationCenters, setCoords } from './EvacuationCenterHelper';
import {
  Button,
  Card,
  CardHeader,
  CardBody,
  Form as StrapForm,
  FormGroup,
  Input,
  InputGroupAddon,
  InputGroupText,
  InputGroup,
  Container,
  Row,
  Col
} from "reactstrap";
import packageJson from '../../package.json';

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

function InternalEvacuationCenter(props) {

  var updateCount = 0;
  const [evacuationCenters, setEvacuationCenters] = useState([]);
  const [isEvacuationCenterLoading, setLoading] = useState(true);
  const [evacuationSelectInput, changeEvacuationSelectInput] = useState(null);
  const [newMarkerLat, changeMarkerLat] = useState(0);
  const [newMarkerLng, changeMarkerLng] = useState(0);
  const [newMarker, changeMarker] = useState(null);
  var setFieldValueRef = null;
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
    changeMarker({lat: newMarkerLat, lng: newMarkerLng});
  }, [newMarkerLat, newMarkerLng]);

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
      // console.log("New X: " + getCenterX());
      // console.log("New Y: " + getCenterY());
      // console.log("New Selected Name: " + selectedOption.label);
      // console.log("Selected: " + selectedOption.toString());
    }

    const handleMapClick = async (e) => {
      const latLng = e.latLng;
      changeMarkerLat(latLng.lat());
      changeMarkerLng(latLng.lng());
      if (setFieldValueRef)
        setFieldValueRef('geolocation', latLng.lat() + ',' + latLng.lng());
      console.log("Moving new marker");
    }

    
  
    
    if (isEvacuationCenterLoading && !isLoaded) return <div className="map">Loading...</div>
    // Documentation for react-select: https://react-select.com/home
    // Use this for information on Fields: https://formik.org/docs/api/field
    // 

    else return (
    // <LoadScript googleMapsApiKey="AIzaSyBqxOriSUSwlm8HEZ0W6gkQj3fazIbegDM">
    <div className="map_container">
      <Container>
        <Row>
          <Col>
            <GoogleMap
              mapContainerStyle={containerStyle}
              zoom={20}
              center={center}
              options={options}
              onClick={handleMapClick}
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
                <Marker
                icon={{
                  path: window.google.maps.SymbolPath.CIRCLE,
                  scale: 7,
                }}
                draggable={true}
                position={newMarker}
                onDragEnd={handleMapClick}/>
            </GoogleMap>
          </Col>
          <Col>
            <Formik
              initialValues={{
                name: '',
                address: '',
                geolocation: ''
              }}
              
              onSubmit={
                  async values => {
                    console.log(values);
                    axios
                      .post(packageJson.proxy + '/relief/api/evacuation-center/', JSON.stringify(values), {
                          "headers": {'Content-Type': 'application/json'},
                          "credentials": "include"
                      })
                      .catch((error) => console.log(error));
                    // const data = await fetch(packageJson.proxy + '/relief/api/evacuation-center/', {
                    //   method: 'POST',
                    //   headers: {
                    //       'Content-Type': 'application/json'
                    //   },
                    //   body: JSON.stringify(values)
                    // });
                    // const {result} = await data.json();
                    // return result;                     
                  }
              }

              > 
              {
                ({values, setFieldValue}) => {
                  setFieldValueRef = setFieldValue;
                  return (
                <Form>
                      <FormGroup className="mb-3">
                          <InputGroup className="input-group-alternative">
                              <InputGroupAddon addonType="prepend">
                                  <InputGroupText>
                                    Name
                                  </InputGroupText>
                              </InputGroupAddon>
                              <Field id="name" name="name" type="text" placeholder="Name">
                              </Field>
                          </InputGroup>
                      </FormGroup>
                      <FormGroup>
                          <InputGroup className="input-group-alternative">
                          <InputGroupAddon addonType="prepend">
                              <InputGroupText>
                              Geolocation
                              </InputGroupText>
                          </InputGroupAddon>
                              {/* <Field id="tmp-geolocation" value={newMarkerLat + "," + newMarkerLng} 
                                    name="tmp-geolocation" type="text" placeholder="Geolocation"
                                    onChange={(e) => {
                                    console.log(e.target.value);
                                    setFieldValue('geolocation', e.target.value);}}>
                              </Field> */}
                              <Field id="geolocation" name="geolocation" type="text" />
                              
                          </InputGroup>
                      </FormGroup>
                      <FormGroup>
                          <InputGroup className="input-group-alternative">
                          <InputGroupAddon addonType="prepend">
                              <InputGroupText>
                              Address
                              </InputGroupText>
                          </InputGroupAddon>
                              <Field id="address" name="address" placeholder="Address">
                              </Field>
                          </InputGroup>
                      </FormGroup>
                      <div className="text-center">
                          <Button className="my-4" color="primary" type="submit">Sign in</Button>
                      </div>
                  </Form>
                )
                }
              }
                </Formik>
           </Col>
        </Row>
      </Container>

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
