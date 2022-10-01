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
//react 
import { useState } from "react";
import * as React from 'react';
import { Formik, useFormik } from "formik";
import * as Yup from 'yup';

// @mui material components
import Grid from "@mui/material/Grid";
import Divider from "@mui/material/Divider";
import MenuItem from "@mui/material/MenuItem";
import Autocomplete from "@mui/material/Autocomplete";
import InputLabel from '@mui/material/InputLabel';
import Select, { SelectChangeEvent } from '@mui/material/Select';

// @mui icons
import FacebookIcon from "@mui/icons-material/Facebook";
import TwitterIcon from "@mui/icons-material/Twitter";
import InstagramIcon from "@mui/icons-material/Instagram";

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";

// Material Dashboard 2 PRO React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ProfileInfoCard from "examples/Cards/InfoCards/ProfileInfoCard";
import ProfilesList from "examples/Lists/ProfilesList";
import DefaultProjectCard from "examples/Cards/ProjectCards/DefaultProjectCard";

// Overview page components
import Header from "layouts/pages/profile/components/Header";
import PlatformSettings from "layouts/pages/profile/profile-overview/components/PlatformSettings";

// Data
import profilesListData from "layouts/pages/profile/profile-overview/data/profilesListData";

// Images
import homeDecor1 from "assets/images/home-decor-1.jpg";
import homeDecor2 from "assets/images/home-decor-2.jpg";
import homeDecor3 from "assets/images/home-decor-3.jpg";
import homeDecor4 from "assets/images/home-decor-4.jpeg";
import team1 from "assets/images/team-1.jpg";
import team2 from "assets/images/team-2.jpg";
import team3 from "assets/images/team-3.jpg";
import team4 from "assets/images/team-4.jpg";

//AXIOS
import axiosConfig from "axiosConfig";
import LRU from 'lru-cache';
import {configure} from 'axios-hooks';
import useAxios from 'axios-hooks';
import { Navigate } from "react-router-dom";
import { FormControl } from "@mui/material";

function Overview() {
  const [evacCenter, setEvacCenter] = useState('');
  const cache = new LRU({max: 10})
  configure({axiosConfig, cache});
  const [{data, loading, error}, refetch] = useAxios("/relief/api/users/current_user/");
  const [{data: evacData, loading: evacLoading, error: evacError}, refetchEvac] = useAxios("/relief/api/evacuation-center/");
  const [isEvacChosen, setEvacChosen] = useState(() => false);
  const [{data: evacQRData, loading: evacQRLoading, error: evacQRError}, refetchEvacQR] = useAxios("/relief/api/stubs/?request__evacuation_center__name=");
  if(loading||evacLoading||evacQRLoading) return;
  if (error||evacError) return <Navigate to="/login"/>

  const evacNames = evacData.map((evac) => {
      return <MenuItem value={evac.name}>{evac.name}</MenuItem>
    }
  );

  const handleChange = (event) => {
    console.log("handling change...")
    setEvacCenter(event.target.value);
    setEvacChosen(true);
    const qrUrl = `/relief/api/stubs/?request__evacuation_center__name=${event.target.value}`;
    refetchEvacQR({url: qrUrl});
  };


  //QR Code
  var qrRender = "";
  if (!evacQRLoading && isEvacChosen && evacQRData[0]){
    console.log(`Re-rending QR with URL ${evacQRData[0].qr_code} `);
     qrRender = (
      <img src={evacQRData[0].qr_code} />
    );
  } else{
    console.log(`Failure, unable to render QR for ${evacCenter}`);
  }

  const residentQRRender = (
    <Grid direction="column" item xs={12} md={5} xl={5} sx={{ display: "flex" }}>
                <Grid item ml={1} xs={12} md={12} xl={12} mb={2} sx={{ display: "flex" }}>
                  <MDTypography variant="h6" fontWeight="medium">
                      Resident QR
                  </MDTypography> 
                </Grid>
                  <Grid item ml={1} xs={12} md={6} xl={6} sx={{ display: "flex" }}>
                    <Grid item xs={12} md={6} xl={6} sx={{ display: "flex" }}>
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
                              {evacNames}
                          </Select> 
                        </FormControl>
                      </Grid>
                    </Grid>
                    <Grid item xs={12} md={12} xl={12} sx={{ display: "flex" }}>
                      {qrRender}
                   </Grid>
                  <br/>
                  
              <Divider orientation="vertical" sx={{ mx: 0 }} />

            </Grid>
  )

  console.log(data);
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mb={2} />
      <Header>
        <MDBox mt={5} mb={3}>
          <Grid container spacing={1}>
            {/* <Grid item xs={12} md={6} xl={4}>
              <PlatformSettings />
            </Grid> */}
            <Grid item xs={12} md={7} xl={7} sx={{ display: "flex" }}>
              <Divider orientation="vertical" sx={{ ml: -2, mr: 1 }} />
              <ProfileInfoCard
                title="profile information"
                description="Hi, I’m Alec Thompson, Decisions: If you can’t decide, the answer is no. If two equally difficult paths, choose the one more painful in the short term (pain avoidance is creating an illusion of equality)."
                info={{
                  username: data.username,
                  firstName: data.first_name, 
                  lastName: data.last_name,
                  email: data.email,
                  role: data.role_verbose,
                }}
                social={[
                  {
                    link: "https://www.facebook.com",
                    icon: <FacebookIcon />,
                    color: "facebook",
                  },
                  {
                    link: "https://twitter.com",
                    icon: <TwitterIcon />,
                    color: "twitter",
                  },
                  {
                    link: "https://www.instagram.com",
                    icon: <InstagramIcon />,
                    color: "instagram",
                  },
                ]}
                action={{ route: "", tooltip: "Edit Profile" }}
                shadow={false}
              />
              <Divider orientation="vertical" sx={{ mx: 0 }} />
            </Grid>
            {(data.role_verbose=="Resident")? residentQRRender: ""}
            {/* <Grid item xs={12} xl={6}>
              <ProfilesList title="conversations" profiles={profilesListData} shadow={false} />
            </Grid> */}
          </Grid>
        </MDBox>
        {/* <MDBox pt={2} px={2} lineHeight={1.25}>
          <MDTypography variant="h6" fontWeight="medium">
            Projects
          </MDTypography>
          <MDBox mb={1}>
            <MDTypography variant="button" color="text">
              Architects design houses
            </MDTypography>
          </MDBox>
        </MDBox>
        <MDBox p={2}>
          <Grid container spacing={6}>
            <Grid item xs={12} md={6} xl={3}>
              <DefaultProjectCard
                image={homeDecor1}
                label="project #2"
                title="modern"
                description="As Uber works through a huge amount of internal management turmoil."
                action={{
                  type: "internal",
                  route: "/pages/profile/profile-overview",
                  color: "info",
                  label: "view project",
                }}
                authors={[
                  { image: team1, name: "Elena Morison" },
                  { image: team2, name: "Ryan Milly" },
                  { image: team3, name: "Nick Daniel" },
                  { image: team4, name: "Peterson" },
                ]}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <DefaultProjectCard
                image={homeDecor2}
                label="project #1"
                title="scandinavian"
                description="Music is something that everyone has their own specific opinion about."
                action={{
                  type: "internal",
                  route: "/pages/profile/profile-overview",
                  color: "info",
                  label: "view project",
                }}
                authors={[
                  { image: team3, name: "Nick Daniel" },
                  { image: team4, name: "Peterson" },
                  { image: team1, name: "Elena Morison" },
                  { image: team2, name: "Ryan Milly" },
                ]}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <DefaultProjectCard
                image={homeDecor3}
                label="project #3"
                title="minimalist"
                description="Different people have different taste, and various types of music."
                action={{
                  type: "internal",
                  route: "/pages/profile/profile-overview",
                  color: "info",
                  label: "view project",
                }}
                authors={[
                  { image: team4, name: "Peterson" },
                  { image: team3, name: "Nick Daniel" },
                  { image: team2, name: "Ryan Milly" },
                  { image: team1, name: "Elena Morison" },
                ]}
              />
            </Grid>
            <Grid item xs={12} md={6} xl={3}>
              <DefaultProjectCard
                image={homeDecor4}
                label="project #4"
                title="gothic"
                description="Why would anyone pick blue over pink? Pink is obviously a better color."
                action={{
                  type: "internal",
                  route: "/pages/profile/profile-overview",
                  color: "info",
                  label: "view project",
                }}
                authors={[
                  { image: team4, name: "Peterson" },
                  { image: team3, name: "Nick Daniel" },
                  { image: team2, name: "Ryan Milly" },
                  { image: team1, name: "Elena Morison" },
                ]}
              />
            </Grid>
          </Grid>
        </MDBox> */}
      </Header>
      <Footer />
    </DashboardLayout>
  );
}

export default Overview;
