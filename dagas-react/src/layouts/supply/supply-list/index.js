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
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';

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
import ProductImages from "./components/ProductImages";
import ProductInfo from "./components/ProductInfo";
import DefaultCell from "./components/DefaultCell";
import ProductCell from "./components/ProductCell"
import FormField from "./components/FormField";

//React
import { useEffect, useState } from "react";
import { Formik, useFormik } from "formik";
import * as Yup from 'yup';

//AXIOS and navigation
import { useAxios } from 'axiosConfig';

import logo from 'logo.svg';
import { Navigate } from "react-router-dom";
import { Icon } from "@mui/material";
function SupplyList() {

  const [supplyForm, setSupplyForm] = useState(() => {
    return "Loading...";
  });
  const [{data, loading, error}, refetch] = useAxios("/relief/api/supplies/current_supplies/");
    // Loading item types
  const [{data: typeArray, loading: typeLoading, error: typeError}, refetchTypes] = useAxios("/relief/api/item-type/");
  const [{data: postSupply, loading: postLoading, error: postError}, executeSupplyPost] = useAxios({
        url: "/relief/api/supplies/",
        method: "POST"
  }, {  manual: true  });

  const [deleteSupplyId, setDeleteSupplyId] = useState("");
  const [isDeleting, setDeleting] = useState(false);
  const [{data: deleteSupply, loading: deleteLoading, error: deleteError}, executeSupplyDelete] = useAxios({
    url: `/relief/api/supplies/${deleteSupplyId}`,
    method: "DELETE"
  }, {manual: true})

  const [editSupplyId, setEditSupplyId] = useState(() => "");
  const [isEditing, setEditing] = useState(() => false);
  const [{data: editSupply, loading: editLoading, error: editError}, executeSupplyEdit] = useAxios({
    url: `/relief/api/supplies/${editSupplyId}/`,
    method: "PATCH"
  }, {manual: true});


  const [typeDescriptionRender, setTypeDescriptionRender] = useState(null);
  
 
  //Deleting effect
  useEffect(() => {
    async function deleteSupplyFunc(){
      if (isDeleting) {
        await executeSupplyEdit();
        await refetch();
      }
  }
  deleteSupplyFunc();
    
  }, [isDeleting]);

  // Supply type insertion effect
  useEffect(() =>{
    console.log(`Re-rendering form with edit state ${isEditing}...`);
    if (typeError) setSupplyForm("Something went wrong...");
    else if (!typeLoading && typeArray) {
      console.log(typeArray);
      const typeNames = typeArray.map(type => type.name);
      console.log(typeNames);
      var initVals = {
        name: '',
        type: typeNames[0],
        pax: ''

    };
    let formHeader = (
      <MDTypography variant="h5">Add New Supply</MDTypography>
    );
      if (isEditing) {
        const supplyData = data.filter(supply => supply.id == editSupplyId)[0];
        initVals.name = supplyData.name;
        initVals.type = supplyData.type_str;
        initVals.pax = supplyData.pax;
        
        console.log(initVals);
        formHeader = (
          <MDTypography variant="h5">Editing {supplyData.name}</MDTypography>
        );
      } 
      const SupplyFormWrapped = ( 
        <Formik
                enableReinitialize={true}
                initialValues={initVals}
                validationSchema={Yup.object().shape({
                    name: Yup.string()
                        .required('Supply name is required'),
                    type: Yup.string()
                        .required('This value is required'),
                    pax: Yup
                        .number()
                        .min(1, 'Should have a pax of one or more')
                })}
                onSubmit={async (values, {setSubmitting}) => {
                    // var requestValues = {...values}; //copy the data to preprocess
                    console.log(values);
                    var requestValues = {};
                    requestValues["name"] = values.name;
                    requestValues["pax"] = values.pax;
                    requestValues["quantity"] = values.pax;
                    requestValues["type"] = typeArray.filter(item => item.name == values.type)[0].id;
                    console.log(JSON.stringify(requestValues));
                    if (isEditing){
                        await executeSupplyEdit({
                          data: requestValues
                        });
                        setEditing(false);
                    } else{
                        executeSupplyPost({
                          data: requestValues
                        });
                    }

                    //Refetch supplies
                    refetch();
                    setSubmitting(false);
                   
                    //   return result;                     
                } }
                // onSubmit={fields => {
                //     alert('SUCCESS!! :-)\n\n' + JSON.stringify(fields, null, 4));
                //     history.push('/home');
                // }}
                >
                {
                formik => (
                  <MDBox py={3}>
                      <Card sx={{ overflow: "visible" }}>
                        <MDBox p={3}>
                          {formHeader}
                          <MDBox mt={3}>
                            <Grid container spacing={3}>
                              <Grid item xs={12} sm={6}>
                                <FormField id="name" type="text" label="Supply Description" {...formik.getFieldProps('name')} />
                              </Grid>
                              <Grid item xs={12} sm={6}>
                                <FormField type="number" name="number" label="Quantity/Pax" {...formik.getFieldProps('pax')}/>
                              </Grid>
                            </Grid>
                          </MDBox>
                        <MDBox mt={2}>
                          <Grid container spacing={3}>
                          
                            <Grid item xs={6} sm={6}>
                              <MDBox mb={3}>
                                <MDBox mb={1} display="inline-block">
                                  <MDTypography
                                    component="label"
                                    variant="button"
                                    fontWeight="regular"
                                    color="text"
                                    textTransform="capitalize"
                                  >
                                    Category
                                  </MDTypography>
                                </MDBox>
                                <Autocomplete
                                  name="type"
                                  id="type"
                                  options={typeNames}
                                  onChange={(event, value) => {
                                    console.log(`Changing to ${value}...`)
                                    formik.setFieldValue('type', value);
                                    // <TextField 
                                    // type='text' 
                                    // defaultValue='lord help me'
                                    // id='itemTypeDescription'
                                    // fullWidth
                                    // // variant='outlined'
                                    // inputProps={
                                    //   { readOnly: true, }
                                    // }
                                    // ></TextField>
                                  //   <List sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
                                  //   <ListItem>
                                  //     <ListItemAvatar>
                                  //     </ListItemAvatar>
                                  //     <ListItemText primary="Photos" secondary="Jan 9, 2014" />
                                  //   </ListItem>
                                  //   <ListItem>
                                  //     <ListItemAvatar>
                                  //     </ListItemAvatar>
                                  //     <ListItemText primary="Work" secondary="Jan 7, 2014" />
                                  //   </ListItem>
                                  //   <ListItem>
                                  //     <ListItemAvatar>
                                  //     </ListItemAvatar>
                                  //     <ListItemText primary="Vacation" secondary="July 20, 2014" />
                                  //   </ListItem>
                                  // </List>
                                    const supplyDescriptions = {
                                      "Food": [
                                        {primary: "Rice", secondary: "1-2 kilo/s"},
                                        {primary: "Cup noodles", secondary: "2 cups"},
                                        {primary: "Canned Goods (i.e. Sardines, Corned Beef, Meatloaf)", secondary: "2 cans"}
                                      ],
                                      "Water": [
                                        {primary: "Bottled Water", secondary: "500mL - 1L"}
                                      ],
                                      "Clothes": [{primary: "Blanket", secondary: "Adult sized"}]
                                    };
                                    console.log(supplyDescriptions[value]);
                                    const supplyDescriptionListRender = supplyDescriptions[value].map(({primary, secondary}) => (
                                      <ListItem>
                                        <ListItemText primary={primary} secondary={secondary}/>
                                      </ListItem>
                                    ));
                                    setTypeDescriptionRender((
                                      // <List sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
                                        <List dense={true}>
                                          {supplyDescriptionListRender}
                                      </List>
                                    ));
                                  }}
                                  renderInput={(params) => {
                                      return (
                                        <MDBox>
                                          <Icon size="xl">{params.value}</Icon>
                                          <MDInput {...params} onChange={formik.handleChange} variant="standard" />
                                        </MDBox>
                                      );
                                    }
                                  }
                                />
                                  <MDButton variant="gradient" color="light" type="submit" onClick={formik.handleSubmit}>
                                  Submit
                                </MDButton>
                              </MDBox>
                            </Grid>
                            <Grid item xs={6} sm={6}>
                              <MDBox mb={3}>
                                <MDBox mb={2}>
                                  <MDTypography
                                    component="label"
                                    variant="button"
                                    fontWeight="regular"
                                    color="text"
                                    textTransform="capitalize"
                                  >
                                    Add at least:
                                  </MDTypography>
                                </MDBox>
                                <MDBox>
                                    {typeDescriptionRender}
                                  {/* <TextField 
                                    type='text' 
                                    defaultValue='lord help me'
                                    id='itemTypeDescription'
                                    fullWidth
                                    // variant='outlined'
                                    inputProps={
                                      { readOnly: true, }
                                    }
                                    >
                                  </TextField> */}
                                </MDBox>
                              </MDBox> 
                            </Grid>
                          </Grid>
                        </MDBox>
                      </MDBox>
                      </Card>
                  </MDBox>
                        )}
                </Formik>
          )

      setSupplyForm(SupplyFormWrapped);
      
    }
}, [typeLoading, typeError, typeArray, isEditing, editSupplyId, typeDescriptionRender]);
  
  console.log(`Loading type array: ${typeArray}`);
  if (loading || deleteLoading) return;
  if (error) return <Navigate to="/login"/>;


  // Rendering proper
  const dataTableData = {
    columns: [
      {   
        Header: "product", 
        accessor: "picture", 
        width: "50%", 
        
        Cell: ({row}) => {
          if (!row.values.picture) return <ProductCell image={logo} name={row.original.name} />;
          else return <ProductCell image={row.values.picture} name={row.original.name} />;
        }
      },
      /* { 
        Header: "pax", 
        accessor: "pax", 
        width: "10%", 
        Cell: ({value}) => {
          return <DefaultCell>{value}</DefaultCell>
        }
      }, */
      // { Header: "review", accessor: "review", align: "center" },
      { Header: "availability", 
        accessor: "available_pax", 
        align: "center", 
        width: "40%",
        Cell: ({row}) => {
          const percent = (row.values.available_pax / row.original.pax) * 100;
          return (
          <MDBox width="8rem">
             <MDProgress variant="gradient" value={percent} color="success" />
             <DefaultCell>{row.values.available_pax}</DefaultCell>
           </MDBox>
          );
        } 
      },
      
      { Header: "id", accessor: "id", align: "center" },
      {
        Header: "actions", 
        align: "center",
        Cell: ({row}) => {
          return (
            <DefaultCell>

              <MDButton onClick={(event) => {
                setDeleteSupplyId(row.values.id);
                setDeleting(true);
              }}>
                  <Icon fontSize="small">delete</Icon>
              </MDButton>
              <MDButton onClick={(event) => {
                setEditSupplyId(row.values.id);
                setEditing(true);
              }}>
                  <Icon fontSize="small">edit</Icon>
              </MDButton>
            </DefaultCell>
          )
        }
      }
    ],
  
  };
  dataTableData["rows"] = data;
  console.log(data);

  const supplyDataTableRender = (
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
                  Supplies
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
  )

  return (
    <DashboardLayout>
      <DashboardNavbar />
      {supplyForm}

      {/* Supply Table */}
      {isEditing? "" : supplyDataTableRender}
      <Footer />
    </DashboardLayout>
  );
}

export default SupplyList;
