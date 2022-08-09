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

// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDProgress from "components/MDProgress";
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

//AXIOS
import axiosConfig from "axiosConfig";
import LRU from 'lru-cache';
import {configure} from 'axios-hooks';
import useAxios from 'axios-hooks';
import logo from 'logo.svg';
function ProductPage() {

  const dataTableData = {
    columns: [
      {   
        Header: "product", 
        accessor: "picture", 
        width: "50%", 
        
        Cell: ({row}) => {
          console.log(row.values.picture);
          if (!row.values.picture) return <ProductCell image={logo} name={row.original.name} />;
          else return <ProductCell image={row.values.picture} name={row.original.name} />;
        }
      },
      { 
        Header: "pax", 
        accessor: "pax", 
        width: "10%", 
        Cell: ({value}) => {
          return <DefaultCell>{value}</DefaultCell>
        }
      },
      // { Header: "review", accessor: "review", align: "center" },
      { Header: "availability", 
        accessor: "available_pax", 
        align: "center", 
        width: "40%",
        Cell: ({row}) => {
          const percent = (row.values.available_pax / row.values.pax) * 100;
          return (
          <MDBox width="8rem">
             <MDProgress variant="gradient" value={percent} color="success" />
             <DefaultCell>{row.values.available_pax}</DefaultCell>
           </MDBox>
          );
        } 
      },
      
      { Header: "id", accessor: "id", align: "center" },
    ],
  
    // rows: [
    //   {
    //     product: <ProductCell image={blackChair} name="Christopher Knight Home" />,
    //     price: <DefaultCell>$89.53</DefaultCell>,
    //     review: <ReviewCell rating={4.5} />,
    //     availability: (
    //       <MDBox width="8rem">
    //         <MDProgress variant="gradient" value={80} color="success" />
    //       </MDBox>
    //     ),
    //     id: <DefaultCell>230019</DefaultCell>,
    //   },
  
  };

  const cache = new LRU({max: 10})
  configure({axiosConfig, cache});
  const [{data, loading, error}, refetch] = useAxios("/relief/api/supplies/current_supplies/");

  if (loading) return;
  
  dataTableData["rows"] = data;
  console.log(dataTableData);
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Card sx={{ overflow: "visible" }}>
          <MDBox p={3}>
            {/* <MDBox mb={3}>
              <MDTypography variant="h5" fontWeight="medium">
                Product Details
              </MDTypography>
            </MDBox>

            <Grid container spacing={3}>
              <Grid item xs={12} lg={6} xl={5}>
                <ProductImages />
              </Grid>
              <Grid item xs={12} lg={5} sx={{ mx: "auto" }}>
                <ProductInfo />
              </Grid>
            </Grid> */}

            <MDBox mt={8} mb={2}>
              <MDBox mb={1} ml={2}>
                <MDTypography variant="h5" fontWeight="medium">
                  Other Products
                </MDTypography>
              </MDBox>
              <DataTable
                table={dataTableData}
                entriesPerPage={false}
                showTotalEntries={false}
                isSorted={false}
              />
            </MDBox>
          </MDBox>
        </Card>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default ProductPage;
