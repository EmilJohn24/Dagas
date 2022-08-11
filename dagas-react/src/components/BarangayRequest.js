import { useState } from "react";

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Checkbox from '@mui/material/Checkbox';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';

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

function BarangayRequest() {
  const [foodAmount, setFoodAmount] = useState(0);
  const [waterAmount, setWaterAmount] = useState(0);
  const [ClothesAmount, setClothesAmount] = useState(0);

  return (
    <DashboardLayout>
      <DashboardNavbar />
        <MDBox p={10}>
          <Grid spacing={3} p={2} container style={{backgroundColor: '#ffffff' }}>
            <Grid xs={12} p={3} container justifyContent="center">
              <MDTypography variant="h4" fontWeight="medium">
                  Request Items
              </MDTypography>
            </Grid>
            <Grid xs={1} p={1} container justifyContent="center">
              <Checkbox id="foodCheckBox"/>
            </Grid>
            <Grid xs={1} container justifyContent="center" style={{paddingTop: 11 }}>
              {/* <img src="../assets/images/drake.jpg" alt="Italian Trulli"  width="50%" height="50%"/> */}
              <FastfoodIcon></FastfoodIcon>
            </Grid>
            <Grid xs={4} container justifyContent="center" style={{paddingTop: 10 }}>
              <MDTypography variant="h5" fontWeight="medium">
                  Food
              </MDTypography>
            </Grid>
            <Grid xs={6}>
              <TextField id="foodAmount" label="Amount" fullWidth color="secondary"/>
            </Grid>
            <Grid xs={1}  p={1} container justifyContent="center">
              <Checkbox id="waterCheckBox"/>
            </Grid>
            <Grid xs={1} container justifyContent="center"  style={{paddingTop: 11 }}>
              {/* <img src="../assets/images/drake.jpg" alt="Italian Trulli"  width="50%" height="50%"/> */}
              <LocalDrinkIcon></LocalDrinkIcon>
            </Grid>
            <Grid xs={4} container justifyContent="center"  style={{paddingTop: 10 }}>
              <MDTypography variant="h5" fontWeight="medium">
                  Water
              </MDTypography>
            </Grid>
            <Grid xs={6}>
              <TextField id="waterAmount" label="Amount" fullWidth color="secondary"/>
            </Grid>
            <Grid xs={1} p={1} container justifyContent="center">
              <Checkbox id="clothesCheckBox"/>
            </Grid>
            <Grid xs={1} container justifyContent="center"  style={{paddingTop: 11 }}>
              {/* <img src="../assets/images/drake.jpg" alt="Italian Trulli"  width="50%" height="50%"/> */}
              <CheckroomIcon></CheckroomIcon>
            </Grid>
            <Grid xs={4} container justifyContent="center"  style={{paddingTop: 10 }}>
              <MDTypography variant="h5" fontWeight="medium">
                  Clothes
              </MDTypography>
            </Grid>
            <Grid xs={6}>
              <TextField id="clothesAmount" label="Amount" fullWidth color="secondary" />
            </Grid>
            <Grid xs={12}  p={1} container justifyContent="center">
              <Button id="requestSubmitButton" variant="contained" color="primary">Submit Request</Button>
            </Grid>
          </Grid>
        </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default BarangayRequest;
