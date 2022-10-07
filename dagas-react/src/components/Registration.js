import '../App.css';
import './Registration.css';

import { Component, useState } from 'react';
import axiosConfig from "../axiosConfig";
import { useFormik, Formik } from 'formik';
import * as Yup from 'yup';
import packageJson from '../../package.json';
import { Navigate } from "react-router-dom"


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
import CoverLayout from "components/CoverLayout";
import { Col, Label, Row } from 'reactstrap';


// Formik Tutorial: https://formik.org/docs/tutorial
// TODO: Consider using class-based handling using <Formik> (https://stackblitz.com/edit/react-formik-form-validation-gge2u7?file=App%2FRegister.jsx)
function Registration(props){
    
        //Formik Handling
        const registrationForm = useFormik({
            initialValues: {
                username: '',
                email: '',
                password1: '',
                password2: '',
                first_name: '',
                last_name: '',
                role: '',
            },
            onSubmit: async values => {
                console.log(JSON.stringify(values));
                var result;
                var baseSite = packageJson.proxy;
                console.log(baseSite);
                axiosConfig
                    .post('/api/rest-auth/registration', JSON.stringify(values), {
                        "headers": {'Content-Type': 'application/json'}
                    })
                    .then((res) => {result = res.data;
                        alert("Signup successful");
                    }
                    )
                    .catch((error) => console.log(error));
                    console.log(result);
            //     const data = await fetch('/api/rest-auth/registration', {
            //       method: 'POST',
            //       headers: {
            //           'Content-Type': 'application/json'
            //       },
            //       body: JSON.stringify(values)
            //   });
            //   const {result} = await data.json();
                // return result;                     
                },

            validationSchema: Yup.object({
                username: Yup.string()
                            .max(15, 'Your username is too long')
                            .required('This field is required'),
                email: Yup.string()
                        .email('Not a valid email address')
                        .required('This field is required'),
                password1: Yup.string()
                            .required('Type a password'),
                password2: Yup.string()
                            .oneOf([Yup.ref('password1'), null], 'Passwords must match')
                            .required('Please confirm your password'),
                first_name: Yup.string()
                                .required('This field is required'),
                last_name: Yup.string()
                            .required('This field is required'),
                role: Yup.number("Something went wrong"),
                        
            }),
        });

        return (
        <CoverLayout>
            <Card>
                <MDBox pt={4} pb={3} px={3}>
                    <MDBox component="form" role="form" onSubmit={registrationForm.handleSubmit}>
                        <MDBox mb={2}>
                            <Row>
                                <Col>
                                    <MDInput type="text" label="Last Name" id="last_name" value={registrationForm.values.last_name} onChange={registrationForm.handleChange} variant="standard" />
                                </Col>
                                <Col>
                                    <MDInput type="text" label="First Name" id="first_name" value={registrationForm.values.first_name} onChange={registrationForm.handleChange} variant="standard" />
                                </Col>
                            </Row>
                        </MDBox>
                        <MDBox mb ={2}>
                            <MDInput type="text" label="Username" id="username" value={registrationForm.values.username} onChange={registrationForm.handleChange} variant="standard" fullWidth/>
                        </MDBox>
                        <MDBox mb ={2}>
                            <MDInput type="email" label="Email" id="email" value={registrationForm.values.email} onChange={registrationForm.handleChange} variant="standard" fullWidth/>
                        </MDBox>

                        <MDBox mb={2}>
                            <MDInput type="password" label="Password" id="password1" value={registrationForm.values.password1} onChange={registrationForm.handleChange} variant="standard" fullWidth/>
                        </MDBox>

                        <MDBox mb={2}>
                            <MDInput type="password" label="Confirm Password" id="password2" value={registrationForm.values.password2} onChange={registrationForm.handleChange} variant="standard" fullWidth/>
                        </MDBox>

                        <MDBox mb={2}>
                            <select className="select form-control" id="role"
                                type="number"
                                value={registrationForm.values.role}
                                onChange={registrationForm.handleChange} required>
                                <option value="">Choose a Role</option>
                                <option value="1">Resident</option>
                                <option value="2">Donor</option>
                            </select>
                        </MDBox>
                        <MDBox mt={4} mb={1}>
                            <MDButton variant="gradient" color="info" type="submit" fullWidth>
                                Register
                            </MDButton>
                        </MDBox>
                    </MDBox>
                </MDBox>
            </Card>
        </CoverLayout>
        )
    }
    
    export default function(props) {
        const navigation = useNavigate();
        return <Registration {...props} navigation={navigation} />;
        }
