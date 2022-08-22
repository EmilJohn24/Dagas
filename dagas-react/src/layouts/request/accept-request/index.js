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

import './AcceptRequest.css';

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
import FastfoodIcon from '@mui/icons-material/Fastfood';
import LocalDrinkIcon from '@mui/icons-material/LocalDrink';
import CheckroomIcon from '@mui/icons-material/Checkroom';
import { ListItemSecondaryAction } from "@mui/material";



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
import DefaultCell from "./components/DefaultCell";


//React
import { useEffect, useState } from "react";
import { Formik, useFormik } from "formik";
import * as Yup from 'yup';

//AXIOS and navigation
import axiosConfig from "axiosConfig";
import LRU from 'lru-cache';
import {configure} from 'axios-hooks';
import useAxios from 'axios-hooks';
import logo from 'logo.svg';
import { Navigate } from "react-router-dom";
import { Icon } from "@mui/material";
function AcceptRequest() {

  const cache = new LRU({max: 10})
  configure({axiosConfig, cache});
  const [{data, loading, error}, refetch] = useAxios("/relief/api/requests/311/");
  const [{data: dataS, loading: loadingS, error: errorS}, refetchS] = useAxios("/relief/api/supplies/current_supplies/");
  if (loading || loadingS) return;
  if (error || errorS) return <Navigate to="/login"/>;


  const supplyDataTable = {
    columns:[
      {
        Header: "Items",
        accessor: "name",
        Cell: ({value}) => {
          return(
            <DefaultCell>
              <MDTypography variant="h5" fontWeight="medium">
                {value}
              </MDTypography>
              </DefaultCell>
          )
        }
      }

    ]
  }
  supplyDataTable["rows"] = dataS
  console.log(dataS);
  // Rendering proper
  const requestDataTable = {
    columns: [
      {   
        Header: "Items", 
        accessor: "type_str",  
        Cell: ({row}) => {
          return (
          <DefaultCell>
            <MDTypography variant="h5" fontWeight="medium">
              {row.values.type_str}
              </MDTypography>
              </DefaultCell>
          )
        }
      },
      {
          Header: "Pax",
          accessor: "pax",
          Cell: ({row}) => {
            return(
              <DefaultCell>
              <MDTypography variant="h5" fontWeight="medium">
                {row.values.pax}
                </MDTypography>
              </DefaultCell>
            )
            
        }
      }
      

    ],
  
  };
  requestDataTable["rows"] = data.item_requests_serialized;
  console.log(data.item_requests_serialized);

  return (
    
    <DashboardLayout>
    <DashboardNavbar />
      <MDBox p={10}>
        <Grid spacing={3} p={2} container style={{backgroundColor: '#ffffff' }}>
          <Grid xs={12} p={3} container justifyContent="center">
              <MDTypography variant="h4" fontWeight="medium">
                  Send Supply
              </MDTypography>
          </Grid>
          <DataTable
                table={supplyDataTable}
                entriesPerPage={false}
                showTotalEntries={false}
                isSorted={false}
            />
        </Grid>
      </MDBox>
      <MDBox p={10}>
        <Grid spacing={3} p={2} container style={{backgroundColor: '#ffffff' }}>
          <Grid xs={12} p={3} container justifyContent="center">
            <MDTypography variant="h4" fontWeight="medium">
                Currently Needed
            </MDTypography>
          </Grid>
          <DataTable
                table={requestDataTable}
                entriesPerPage={false}
                showTotalEntries={false}
                isSorted={false}
              />  
          </Grid>
      </MDBox>
    <Footer />
  </DashboardLayout>
  );
}

export default AcceptRequest;


// {
//     Headers: "Items",
//     accessor: "type_str",
//     Cell: ({rows}) => {
//       console.log(rows.values.type_str)
//       return <DefaultCell>{rows.values.type_str}</DefaultCell>
//   }
// },
// {
//     Headers: "Pax",
//     accessor: "pax",
//     Cell: ({rows}) => {
//       console.log(rows.values)
//       return <DefaultCell>{rows.values.pax}</DefaultCell>
//   }
// }


