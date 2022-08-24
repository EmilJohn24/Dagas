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

import { useState, useEffect, useCallback } from "react";

// @mui material components
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Divider from "@mui/material/Divider";


//Components
import IdCell from "./components/IdCell";
import DefaultCell from "./components/DefaultCell";
import StatusCell from "./components/StatusCell";
import CustomerCell from "./components/CustomerCell";

//AXIOS
import axiosConfig from "axiosConfig";
import LRU from 'lru-cache';
import {configure} from 'axios-hooks';
import useAxios from 'axios-hooks';
import { Navigate } from "react-router-dom";

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";

// Material Dashboard 2 PRO React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";
import AcceptRequest from "layouts/request/accept-request";

function RequestList() {
     //Guide: https://www.npmjs.com/package/axios-hooks#manual-requests
  const cache = new LRU({max: 10})
  configure({axiosConfig, cache});
  const [{data, loading, error}, refetch] = useAxios("/relief/api/requests/");
  const [isAcceptingRequest, setAcceptingRequest] = useState(() => false);
  const [requestId, setRequestId] = useState(() => null);
  if (loading) return;
  if (error) return <Navigate to="/login"/>
   var dataTableData = {
      columns: [
        {
          Header: "barangay",
          accessor: "barangay_serialized.user",
          Cell: ({value}) =>(
              <DefaultCell value={value}></DefaultCell>
            )
        },
        {
          Header: "evacuation_center",
          accessor: "evacuation_center_serialized",
          Cell: ({row}) => {
            // console.log(row.values.evacuation_center_serialized.name);
            return (
              <DefaultCell value={row.values.evacuation_center_serialized.name}></DefaultCell>
            );
          } 
        },
        {
          Header: "action", 
          align: "center",
          accessor: "id",
          width: "20%",
          Cell: ({value}) => {
            return (
              <MDButton onClick={
                (event) => {
                  console.log(`Setting request ID to: ${value}`);
                  setRequestId(value);
                  setAcceptingRequest(true);
                }
              } variant="gradient" color="info">Accept</MDButton>
            )
          }
        },
      ],
    };

 

    dataTableData["rows"] = data;
    console.log(dataTableData);

  var renderedData = null;
  if (!isAcceptingRequest){
    renderedData = (
      <DataTable table={dataTableData} entriesPerPage={false} canSearch />
    );
  } else {
    renderedData = <AcceptRequest requestId={requestId} />
  }

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox my={3}>
        <MDBox display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <MDBox display="flex">
            <MDBox ml={1}>
              <MDButton variant="outlined" color="dark">
                <Icon>description</Icon>
                &nbsp;export csv
              </MDButton>
            </MDBox>
          </MDBox>
        </MDBox>
        <Card>
          {renderedData}
        </Card>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default RequestList;
