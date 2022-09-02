//react 
import { useState, useEffect } from "react";
import * as React from 'react';
import { Formik, useFormik } from "formik";
import * as Yup from 'yup';

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Checkbox from '@mui/material/Checkbox';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import Tooltip from "@mui/material/Tooltip";

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 PRO React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";


import FastfoodIcon from '@mui/icons-material/Fastfood';
import LocalDrinkIcon from '@mui/icons-material/LocalDrink';
import CheckroomIcon from '@mui/icons-material/Checkroom';

//AXIOS and navigation
import axiosConfig from "axiosConfig";
import LRU from 'lru-cache';
import {configure} from 'axios-hooks';
import useAxios from 'axios-hooks';
import { Navigate } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { darkScrollbar } from "@mui/material";

function BarangayRequest(props) {
  const [foodAmount, setFoodAmount] = useState(0);
  const [waterAmount, setWaterAmount] = useState(0);
  const [ClothesAmount, setClothesAmount] = useState(0);
  const [EvacuationCenterID, setEvacuationCenterID] = useState([]);
  const { navigation } = props;
 
  const [evacCenter, setEvacCenter] = React.useState('');

  const cache = new LRU({max: 10})
  configure({axiosConfig, cache});
  const [{data, loading, error}, refetch] = useAxios("/relief/api/evacuation-center/current_evac/");

  const [{data: postRequest, loading: postLoading, error: postError}, executeRequestPost] = useAxios({
    url: "/relief/api/requests/",
    method: "POST"
  }, {  manual: true  });
  
  const [{data: postFoodRequest, loading: postFoodLoading, error: postFoodError}, executeFoodRequestPost] = useAxios({
    url: "/relief/api/item-request/",
    method: "POST"
  }, {  manual: true  });

  const [{data: postWaterRequest, loading: postWaterLoading, error: postWaterError}, executeWaterRequestPost] = useAxios({
    url: "/relief/api/item-request/",
    method: "POST"
  }, {  manual: true  });

  const [{data: postClothesRequest, loading: postClothesLoading, error: postClothesError}, executeClothesRequestPost] = useAxios({
    url: "/relief/api/item-request/",
    method: "POST"
  }, {  manual: true  });

  // const handleFoodChange = (event) => {
  //   console.log(event.target.value);
  //   setFoodAmount(event.target.value);
  // };

  // const handleWaterChange = (event) => {
  //   console.log(event.target.value);
  //   setWaterAmount(event.target.value);
  // };

  // const handleClothesChange = (event) => {
  //   console.log(event.target.value);
  //   setClothesAmount(event.target.value);
  // };

  const handleChange = (event) => {
    console.log(event.target.value);
    setEvacCenter(event.target.value);
  };
  
  useEffect(() => {
    console.log("Triggered effect for handling post");
    console.log(postLoading);
    if (!postRequest || postLoading) return;
    console.log("Accepted post loaded condition...");
      var requestValues = {};
      requestValues["type"] = 1;
      requestValues["pax"] = foodAmount;
      requestValues["barangay_request"] = postRequest.id;
      console.log(requestValues);

      executeFoodRequestPost({
          data: requestValues
    });

      requestValues["type"] = 2;
      requestValues["pax"] = waterAmount;
      console.log(JSON.stringify(requestValues));
      
      executeWaterRequestPost({
          data: requestValues
      });
    
      requestValues["type"] = 3;
      requestValues["pax"] = ClothesAmount;
      console.log(JSON.stringify(requestValues));

      executeClothesRequestPost({
          data: requestValues
      });

  }, [postLoading, postRequest])
//   const handleSubmit = (event) => {

    
// };

  if (loading) return;
  if (error) return <Navigate to="/login"/>;

  const listEvacuationCenters = data.map((data) =>
    <MenuItem value={data.id}>{data.name}</MenuItem>,
  );
  
  const formikRender = (
      <Formik
              initialValues={{
                'food': 0,
                'water': 0,
                'clothes': 0
              }}
              validationSchema={Yup.object().shape({
                food: Yup
                    .number()
                    .optional()
                    .min(1, 'Should have a pax of one or more'),
                water: Yup
                    .number()
                    .optional()
                    .min(1, 'Should have a pax of one or more'),
                clothes: Yup
                    .number()
                    .optional()
                    .min(1, 'Should have a pax of one or more')
            })}
            onSubmit={
              (values, {setSubmitting}) => {
                var evacValues ={};
                evacValues["evacuation_center"] = evacCenter;
                executeRequestPost({
                  data: evacValues
                });
                console.log(typeof postRequest);

                // set values
                setFoodAmount(values.food);
                setWaterAmount(values.water);
                setClothesAmount(values.clothes);
                
                alert("Supplies Requested!")
                navigation('/requests');
              }
            }>{
                (formik) => (
                    <MDBox p={10}>
                      <Grid spacing={3} p={2} container style={{backgroundColor: '#ffffff' }}>
                        <Grid xs={12} p={3} container justifyContent="center">
                          <MDTypography variant="h4" fontWeight="medium">
                              Request Items
                          </MDTypography>
                        </Grid>
                        <Grid xs={2} container justifyContent="center" style={{paddingTop: 15 }}>
                          {/* <img src="../assets/images/drake.jpg" alt="Italian Trulli"  width="50%" height="50%"/> */}
                          <FastfoodIcon></FastfoodIcon>
                        </Grid>
                        <Grid xs={4} container justifyContent="center" style={{paddingTop: 15 }}>
                          <MDTypography variant="h5" fontWeight="medium">
                              Food
                          </MDTypography>
                        </Grid>
                        <Grid xs={6} pl={5} pr={5} pt={1}>
                          <Tooltip title="help me God">
                            <TextField id="foodAmount" label="Amount" fullWidth color="secondary" type='number' {...formik.getFieldProps('food')}/>
                          </Tooltip>
                        </Grid>
                        <Grid xs={2} container justifyContent="center"  style={{paddingTop: 15 }}>
                          {/* <img src="../assets/images/drake.jpg" alt="Italian Trulli"  width="50%" height="50%"/> */}
                          <LocalDrinkIcon></LocalDrinkIcon>
                        </Grid>
                        <Grid xs={4} container justifyContent="center"  style={{paddingTop: 15 }}>
                          <MDTypography variant="h5" fontWeight="medium">
                              Water
                          </MDTypography>
                        </Grid>
                        <Grid xs={6} pl={5} pr={5} pt={1}>
                          <Tooltip title="help me God">
                            <TextField id="waterAmount" label="Amount" fullWidth color="secondary" type='number'  {...formik.getFieldProps('water')}/>
                          </Tooltip> 
                        </Grid>
                        <Grid xs={2} container justifyContent="center"  style={{paddingTop: 15 }}>
                          {/* <img src="../assets/images/drake.jpg" alt="Italian Trulli"  width="50%" height="50%"/> */}
                          <CheckroomIcon></CheckroomIcon>
                        </Grid>
                        <Grid xs={4} container justifyContent="center"  style={{paddingTop: 15 }}>
                          <MDTypography variant="h5" fontWeight="medium">
                              Clothes
                          </MDTypography>
                        </Grid>
                        <Grid xs={6} pl={5} pr={5} pt={1}>
                          <Tooltip title="help me God">
                           <TextField id="clothesAmount" label="Amount" fullWidth color="secondary" type='number'  {...formik.getFieldProps('clothes')}/>
                          </Tooltip>
                        </Grid>
                        <Grid xs={12} container justifyContent="center" pl={15} pr={15} pt={2} pb={2}>
                          <FormControl fullWidth>
                            <InputLabel id="evacuationCenterSelectLabel">Evacuation Center</InputLabel>
                              <Select
                                style={{paddingTop: 10, paddingBottom: 10}}
                                labelId="evacuationCenterSelectLabel"
                                id="evacuationCenterSelect"
                                value={evacCenter}
                                label="Evacuation Center"
                                onChange={handleChange}
                              >
                                {listEvacuationCenters}
                                {/* <MenuItem value={"10"}>Ten</MenuItem>
                                <MenuItem value={"20"}>Twenty</MenuItem>
                                <MenuItem value={"30"}>Thirty</MenuItem> */}
                              </Select>
                          </FormControl>
                        </Grid>
                        <Grid xs={12}  p={3} container justifyContent="center">
                          <Button id="requestSubmitButton" variant="contained" color="primary" onClick={formik.handleSubmit}>Submit Request</Button>
                        </Grid>
                      </Grid>
                    </MDBox>
            )}</Formik>
  )
  return (
    <DashboardLayout>
      <DashboardNavbar />

            {formikRender}
      <Footer />
    </DashboardLayout>
  );
}

export default function(props) {
  const navigation = useNavigate();
  return <BarangayRequest {...props} navigation={navigation} />;
  }
