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
import TextField from "@mui/material/TextField";
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDProgress from "components/MDProgress";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

// Material Dashboard 2 PRO React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";
// ProductPage page components
import ProductImages from "./components/ProductImages";
import ProductInfo from "./components/ProductInfo";
import DefaultCell from "./components/DefaultCell";
import ProductCell from "./components/ProductCell"
import FormField from "./components/FormField";

//React
import { useEffect, useState } from "react";
import { Formik, useFormik } from "formik";
import * as Yup from 'yup';

//Carousel
import { CCarousel } from '@coreui/react'
import { CCarouselItem } from '@coreui/react'
import { CImage } from '@coreui/react'

//AXIOS and navigation
import axiosConfig from "axiosConfig";
import LRU from 'lru-cache';
import {configure} from 'axios-hooks';
import useAxios from 'axios-hooks';
import logo from 'logo.svg';
import { Navigate } from "react-router-dom";
import { Icon } from "@mui/material";

//Image imports
import tip1 from "assets/images/tip1.png";
import tip2 from "assets/images/tip2.png";
import tip3 from "assets/images/tip3.png";
import tip4 from "assets/images/tip4.png";
import tip5 from "assets/images/tip5.png";


function Calamities() {

  const [disasterForm, setDisasterForm] = useState(() => {
    return "Loading...";
  });

  const cache = new LRU({max: 10})
  configure({axiosConfig, cache});
  const [{data, loading, error}, refetch] = useAxios("/relief/api/supplies/current_supplies/");
    // Loading item types
  const [{data: disasterArray, loading: disasterLoading, error: disasterError}, refetchTypes] = useAxios("/relief/api/disasters/");

  // Disaster Name insertion effect
  useEffect(() =>{
    if (disasterError) setDisasterForm("Something went wrong...");
    else if (!disasterLoading && disasterArray) {
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
                    refetch();
                    setSubmitting(false);
                   
                    //   return result;                     
                } }
                >
                {
                formik => (
                  <MDBox py={3} px={70}>
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
                                  options={disasterNames}
                                  onChange={(event, value) => {
                                    console.log(`Changing to ${value}...`)
                                    formik.setFieldValue('type', value);
                                  }}
                                  renderInput={(params) => {
                                      return (
                                        <MDBox>
                                          <Icon size="xl">{params.value}</Icon>
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
}, [disasterLoading, disasterError, disasterArray]);
  
  console.log(`Loading type array: ${disasterArray}`);
  if (loading || disasterLoading) return;
  if (error) return <Navigate to="/login"/>;
  
//FROM https://coreui.io/react/docs/components/carousel/#how-it-works
  const carouselRender = (
    <MDBox>
      <CCarousel controls indicators>
        <CCarouselItem>
          <CImage className="d-block w-100" src={tip1} alt="Tip 1" />
        </CCarouselItem>
        <CCarouselItem>
          <CImage className="d-block w-100" src={tip2} alt="Tip 2" />
        </CCarouselItem>
        <CCarouselItem>
          <CImage className="d-block w-100" src={tip3} alt="Tip 3" />
        </CCarouselItem>
        <CCarouselItem>
          <CImage className="d-block w-100" src={tip4} alt="Tip 4" />
        </CCarouselItem>
        <CCarouselItem>
          <CImage className="d-block w-100" src={tip5} alt="Tip 5" />
        </CCarouselItem>
      </CCarousel>
    </MDBox>
  )
  
  return (
    <DashboardLayout>
      <DashboardNavbar />
      {disasterForm}
      <MDBox mx={50}>
        {carouselRender}
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Calamities;
