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

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";

// Material Dashboard 2 PRO React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// OrderDetails page components
import Header from "./components/Header";
import OrderInfo from "./components/OrderInfo";
import TrackOrder from "./components/TrackOrder";
import PaymentDetails from "./components/PaymentDetails";
import BillingInformation from "./components/BillingInformation";
import OrderSummary from "./components/OrderSummary";

//AXIOS
import { useAxios } from 'axiosConfig';

import { Navigate } from "react-router-dom";

//react 
import { useState, useEffect } from "react";
import * as React from 'react';

function TransactionDetail({details}) {
  const [roleCheck, setRole] = useState();

  const [{data, loading, error}, refetch] = useAxios("/relief/api/users/current_user/");
  

  useEffect(() => {
    console.log("Triggered effect for handling post");
    if (data) {
      if (data.role_verbose == "Barangay") setRole(3);
      else if (data.role_verbose == "Donor") setRole(2);
      else if (data.role_verbose == "Resident") setRole(1);
    }
    
  }, [data, roleCheck])

  if (loading) return;
  if (error) return <Navigate to="/login"/>


  console.log(details);
  return (
      <MDBox my={6}>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} lg={8}>
            <Card>
              <MDBox pt={2} px={2}>
                <Header transactionID={details.id} evacuationCenterName={details.evac_center_name} 
                      barangayName={details.barangay_name} donorName={details.donor_name} />
              </MDBox>
              <Divider />
              <MDBox pt={1} pb={3} px={2}>
                <MDBox mb={3}>
                  <OrderInfo orderID={details.id} qrImage={details.qr_code} status={details.status_string} 
                          received={details.received} isExpired={details.is_expired} checkRole={roleCheck}/>
                </MDBox>
                <Divider />
                <MDBox mt={3}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6} lg={3}>
                      <TrackOrder transactionId={details.id} status={details.received}/>
                    </Grid>
                   
                    <Grid item xs={12} lg={9} sx={{ ml: "auto" }}>
                      <OrderSummary orders={details.transaction_orders}/>
                    </Grid>
                  </Grid>
                </MDBox>
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
  );
}

export default TransactionDetail;
