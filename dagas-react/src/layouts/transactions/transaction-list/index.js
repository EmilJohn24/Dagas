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
import TransactionDetail from "../transaction-detail";
import { func } from "prop-types";
import { areArraysEqual } from "@mui/base";

function TransactionList() {
  const [menu, setMenu] = useState(null);
  
  const openMenu = (event) => setMenu(event.currentTarget);
  const closeMenu = () => setMenu(null);
  
  const renderMenu = (
    <Menu
      anchorEl={menu}
      anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
      transformOrigin={{ vertical: "top", horizontal: "left" }}
      open={Boolean(menu)}
      onClose={closeMenu}
      keepMounted
    >
      <MenuItem onClick={closeMenu}>Status: Paid</MenuItem>
      <MenuItem onClick={closeMenu}>Status: Refunded</MenuItem>
      <MenuItem onClick={closeMenu}>Status: Canceled</MenuItem>
      <Divider sx={{ margin: "0.5rem 0" }} />
      <MenuItem onClick={closeMenu}>
        <MDTypography variant="button" color="error" fontWeight="regular">
          Remove Filter
        </MDTypography>
      </MenuItem>
    </Menu>
  );
  const [transactionDetailId, setTransactionDetailId]  = useState(null);
  const [isDetail, setDetail] = useState(() => false);
  


  const openDetail = (id) => {
    console.log(id);
      setDetail(true);
      setTransactionDetailId(id);
  }

  // const listTransactions =  () => {
  //   var url = "/relief/api/transactions/"
  //   // if (query !== "" && query){
  //   //     url += "?search=" + query;
  //   // }
  //   console.log("HTTP GET on Requests...");
  //   const request = axiosConfig
  //           .get(url);
  //   return request;
  // }
   var dataTableData = {
      columns: [
        { Header: "reference id", 
          accessor: "id", 
          Cell: ({ value }) => {
            return ( 
              <MDButton onClick={(event) => {
                  openDetail(value); }}>
                  <IdCell id={value}/>
              </MDButton>
              )
            } 
        },
        {
          Header: "date",
          accessor: "created_on",
          Cell: ({ value }) => {
            // console.log(row.values.evacuation_center_serialized.name);
            const withoutMilliseconds = value.split('.')[0]
            const [date, time] = withoutMilliseconds.split('T');
            const dateStr = new Date(date).toLocaleDateString();
            return (
              <DefaultCell value={dateStr + " || " + time}></DefaultCell>
            );
          } 
        },
        {
          Header: "status",
          accessor: "received",
          Cell: ({ value }) => {
            let status;
  
            if (value === 1) {
              status = <StatusCell icon="close" color="error" status="Packaging" />;
            } else if (value === 2) {
              status = <StatusCell icon="replay" color="dark" status="In Transit" />;
            } else {
              status = <StatusCell icon="done" color="success" status="Delivered" />;
            }
  
            return status;
          },
        },
        {
            Header: "barangay",
            accessor: "barangay_name",
            Cell: ({value}) => (
              <DefaultCell value={value} />
            ),
          },
          {
            Header: "evacuation center",
            accessor: "evac_center_name",
            Cell: ({value}) => (
              <DefaultCell value={value} />
            ),
          },
        // {
        //   Header: "barangay",
        //   accessor: "barangay",
        //   Cell: ({ value: [name, data] }) => (
        //     <CustomerCell image={data.image} color={data.color || "dark"} name={name} />
        //   ),
        // },
        // {
        //   Header: "donor",
        //   accessor: "transaction_orders.supply_info",
        //   Cell: ({ value }) => {
        //     console.log(value);
        //     var name = value.name;
  
        //     return (
        //       <DefaultCell
        //         value={typeof value === "string" ? value : name}
        //         suffix={data.suffix || false}
        //       />
        //     );
        //   },
        // },
        // { Header: "revenue", accessor: "revenue", Cell: ({ value }) => <DefaultCell value={value} /> },
      ],
  
    };

    //Guide: https://www.npmjs.com/package/axios-hooks#manual-requests
    const [{data, loading, error}, refetch] = useAxios("/relief/api/transactions/");
    
    if (loading) return;
    if (error) return <Navigate to="/login"/>
    
    dataTableData["rows"] = data;
    console.log(dataTableData);
    
    var renderData = null;

    if (isDetail){
      const detailData = data.filter(item => item.id == transactionDetailId)[0];
      renderData = (
        <TransactionDetail details={detailData} />
      )
    } else{
      renderData = (
        <DataTable table={dataTableData} entriesPerPage={false} canSearch />
      );
    }
  
  
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox my={3}>
        <MDBox display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          {/* <MDButton variant="gradient" color="info">
            new order
          </MDButton> */}
          <MDBox display="flex">
            {/* <MDButton variant={menu ? "contained" : "outlined"} color="dark" onClick={openMenu}>
              filters&nbsp;
              <Icon>keyboard_arrow_down</Icon>
            </MDButton> */}
            {renderMenu}
            <MDBox ml={1}>
              {/* <MDButton variant="outlined" color="dark">
                <Icon>description</Icon>
                &nbsp;export csv
              </MDButton> */}
            </MDBox>
          </MDBox>
        </MDBox>
        <Card>
          {renderData}
        </Card>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default TransactionList;
