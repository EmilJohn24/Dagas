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
import { useAxios } from 'axiosConfig';

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

  const [{data, loading, error}, refetch] = useAxios("/relief/api/requests/");
  const [{data: userData, loading: userLoading, error: userError}, userRefetch] = useAxios("/relief/api/users/current_user/");
  const [isAcceptingRequest, setAcceptingRequest] = useState(() => false);
  const [requestId, setRequestId] = useState(() => null);
  if (loading||userLoading) return;
  if (error||userError) return <Navigate to="/login"/>
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
            return (
              <DefaultCell value={row.values.evacuation_center_serialized.name}></DefaultCell>
            );
          } 
        },
        {
          Header: "requested_supplies",
          accessor: "item_requests_serialized",
          Cell: ({row}) => {
            const reqType = row.values.item_requests_serialized.map(type => type.type_str);
            const reqQty = row.values.item_requests_serialized.map(qty => qty.pax);
            var str = "";
            for (let i = 0; i < reqType.length; i++) {
              str += `${reqType[i]}: ${reqQty[i]} | `
            }
            return (
              <DefaultCell value={str}></DefaultCell>
            );  
          } 
        },
        {
          Header: "expected_date",
          accessor: "expected_date",
          Cell: ({value}) => {
            // console.log(row.values.evacuation_center_serialized.name);
            return (
              <DefaultCell value={value}></DefaultCell>
            );
          } 
        },
        (userData.role_verbose == "Donor")?{
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
        }:{
          Header: "action", 
          align: "center",
          accessor: "id",
          width: "10%",
          Cell: ({value}) => {
            return (
            <MDButton onClick={
              (event) => {
                console.log(`Setting request ID to: ${value}`);
                setRequestId(value);
                setAcceptingRequest(true);
              }
            } disabled="true" variant="gradient" color="info">Accept</MDButton>
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
