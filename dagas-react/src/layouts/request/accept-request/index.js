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
import { useAxios } from 'axiosConfig';

import logo from 'logo.svg';
import { Navigate } from "react-router-dom";
import { Icon } from "@mui/material";
function AcceptRequest({requestId}) {

  const [{data, loading, error}, refetch] = useAxios(`/relief/api/requests/${requestId}/`);
  const [{data: dataS, loading: loadingS, error: errorS}, refetchS] = useAxios("/relief/api/supplies/current_supplies/");
  
  const [{data: postTransaction, loading: transactionPostLoading, error: transactionPostError}, executeTransactionPost] = useAxios({
    url: "/relief/api/transactions/",
    method: "POST"
  }, {  manual: true  });
  const [generatedTransactionId, setGeneratedTransactionId] = useState(() => null);
  const [transactionCompleted, setTransactionCompleted] = useState(() => false);
  const [{data: postTransactionOrder, loading: transactionOrderPostLoading, error: transactionOrderPostError}, 
    executeTransactionOrderPost] = useAxios({
      url: "/relief/api/transaction-order/",
      method: "POST"
  }, {  manual: true  });
  
  const [supplyList, setSupplyList] = useState({});
  
  useEffect(() => {
    if (generatedTransactionId != null){
      const transactionOrders = [];
      for (const [supplyId, pax] of Object.entries(supplyList)){
        const transactionOrder = {
          pax: pax,
          supply: parseInt(supplyId),
          transaction: generatedTransactionId
        };
        transactionOrders.push(transactionOrder);
      }
      executeTransactionOrderPost({
        data: transactionOrders
      });
      setTransactionCompleted(true);
    }
  }, [generatedTransactionId]);

  useEffect(() => {
      if (postTransaction)
          setGeneratedTransactionId(postTransaction.id);
      
  }, [postTransaction]);
  console.log("Re-render triggered...");

  if (loading || loadingS) return;
  if (error || errorS) return <Navigate to="/login"/>;
  if (transactionCompleted && !transactionOrderPostLoading) return <Navigate to="/transactions"/>;
  function handleSubmit(event){
    const transactionData = {
      barangay_request: requestId
    };  
    executeTransactionPost({
        data: transactionData
    });
  }

  const supplyDataTable = {
    columns:[
      // {
      //   Header: "Choose",
      //   accessor: "type",
      //   Cell: ({row}) => {
      //     return(
            
      //       <Checkbox checked={supplyList.includes(row.values.id)} onChange={(event) => {
      //         if(event.target.checked){
      //           console.log(supplyList)
      //           setSupplyList(prev => [...prev, row.values.id]);
      //         }
      //         else{
      //             setSupplyList((prev) => {
      //               const index = prev.indexOf(row.values.id);
      //               if(index > -1) prev.splice(index,1);
      //               return prev;
      //             }

      //           )
      //         }

      //       }
      //     }/>
      //     )
      //   }
      // },
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
      },
      {
        Header: "Type",
        accessor: "type_str",
        Cell: ({value}) => {
          return(
            <DefaultCell>
              <MDTypography variant="h5" fontWeight="medium">
                {value}
              </MDTypography>
            </DefaultCell>
          )
        }
      },
      {
        Header: "Available",
        accessor: "available_pax",
        Cell: ({value}) => {
          return(
            <DefaultCell>
              <MDTypography variant="h5" fontWeight="medium">
                {value}
              </MDTypography>
            </DefaultCell>
          )
        }
      },
      {
        Header: "Donation",
        accessor: "id",
        Cell: ({value}) => {
          const supply_id = value
          return(
           
              <TextField type="number" value={supplyList[supply_id]} id={value} onChange={(event) => {
                  const current_value = parseInt(event.target.value);
                  if (current_value > 0){
                    supplyList[supply_id] = current_value;
                    console.log(supplyList);
                    setSupplyList(supplyList);                
                  } else if (current_value <= 0 || event.target.value == "") {
                    delete supplyList[supply_id];
                    setSupplyList(supplyList);
                  }
              }} 
              label="Amount" fullWidth color="secondary"/> 
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
    
    // <DashboardLayout>
    // <DashboardNavbar />
    <>
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
            <MDButton onClick={handleSubmit} variant="gradient" color="info">Submit</MDButton>

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
    {/* <Footer />
  </DashboardLayout> */}
  </>
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


