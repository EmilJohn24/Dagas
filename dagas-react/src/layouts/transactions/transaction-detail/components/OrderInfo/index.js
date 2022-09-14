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

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import MDAvatar from "components/MDAvatar";
import MDBadge from "components/MDBadge";

//React
import { useEffect, useState } from "react";
import { Formik, useFormik } from "formik";
import * as Yup from 'yup';
import React from "react";

//AXIOS and navigation
import axiosConfig from "axiosConfig";
import LRU from 'lru-cache';
import {configure} from 'axios-hooks';
import useAxios from 'axios-hooks';
import { Navigate } from "react-router-dom";

function OrderInfo({orderID, qrImage, status, received, isExpired, checkRole}) {

  const cache = new LRU({max: 10})
  configure({axiosConfig, cache});
  const [{data: putTransaction, loading: transactionPutLoading, error: transactionPutError}, executeTransactionPut] = useAxios({
    url: `/relief/api/transactions/${orderID}/quick_update_status/`,
    method: "PUT"
  }, {  manual: true  });

  const [currentStatus, setCurrentStatus] = useState(() => status);
  const [currentReceived, setCurrentReceived] = useState(() => received);

  useEffect(() => {
    if (putTransaction){
      setCurrentStatus(putTransaction.status_string);
      setCurrentReceived(putTransaction.received);
      console.log(putTransaction);
    }
  }, [putTransaction, transactionPutLoading])

  function handlePackage(event){
    executeTransactionPut({});
  }


  if (transactionPutLoading) return;
  if (transactionPutError) return <Navigate to="/login"/>;
  console.log(status);

  const statusColors = ["error", "error", "warning", "success"]
  return (
    <Grid container spacing={3} alignItems="center">
      <Grid item xs={12} md={6}>
        <MDBox display="flex" alignItems="center">
          <MDBox mr={2}>
            <MDAvatar size="xxl" src={qrImage} alt="QR Code" />
          </MDBox>
          <MDBox lineHeight={1}>
            <MDTypography variant="h6" fontWeight="medium">
             Status
            </MDTypography>
            <MDBox mb={2}>
            </MDBox>
            <MDBadge
              variant="gradient"
              color={isExpired?"error" : statusColors[currentReceived]}
              size="xs"
              badgeContent={currentStatus}
              container
            />
          </MDBox>
        </MDBox>
      </Grid>
      {checkRole == 3 && currentStatus == "Incoming"? <Grid item xs={12} md={6} sx={{ textAlign: "right" }}>
        <MDButton onClick={handlePackage} variant="gradient" color="light" size="small">
          Received
        </MDButton>
        <MDBox mt={0.5}>
          <MDTypography variant="subtitle2" color="text">
            Recieved donation? Click here!
          </MDTypography>
        </MDBox>
      </Grid>:
      checkRole == 2 && currentStatus == "Packaging"? 
      <Grid item xs={12} md={6} sx={{ textAlign: "right" }}>
        <MDButton onClick={handlePackage} variant="gradient" color="light" size="small">
          Packaged
        </MDButton>
        <MDBox mt={0.5}>
          <MDTypography variant="subtitle2" color="text">
            Packaged your donation? Click here!
          </MDTypography>
        </MDBox>
      </Grid>:null
      }
    </Grid>
  );
}

export default OrderInfo;
