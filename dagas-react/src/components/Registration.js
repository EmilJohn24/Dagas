import '../App.css';
import './Registration.css';
import { Component, useState } from 'react';
import axiosConfig from "../axiosConfig";
import { useFormik, Formik } from 'formik';
import * as Yup from 'yup';
// import {
//     Button,
//     Card,
//     CardHeader,
//     CardBody,
//     Dropdown,
//     DropdownToggle,
//     DropdownMenu,
//     DropdownItem,
//     FormGroup,
//     Form,
//     Input,
//     InputGroupAddon,
//     InputGroupText,
//     InputGroup,
//     Container,
//     Row,
//     Col,
//     option
//   } from "reactstrap";

import Form from 'react-bootstrap/Form';
import { useNavigate } from "react-router-dom";
import packageJson from '../../package.json';







// Formik Tutorial: https://formik.org/docs/tutorial
// TODO: Consider using class-based handling using <Formik> (https://stackblitz.com/edit/react-formik-form-validation-gge2u7?file=App%2FRegister.jsx)
function Registration(props){
    const { navigation } = props;

    const {history} = props;

    const [value, setValue] = useState('');

    const [isActive, setIsActive] = useState(false);


    function handleTextChange(text) {
        setValue(text);
      
        if (text !== '') {
          setIsActive(true);
        } else {
          setIsActive(false);
        }
      }
    //Formik Handling
  

    return (
        <>
        <Formik 
            initialValues={{
                username: '',
                email: '',
                password1: '',
                password2: '',
                first_name: '',
                last_name: '',
                role: '',
            }}
            onSubmit={async (values) => {
            console.log(JSON.stringify(values));
            const result = await axiosConfig
                .post('/api/rest-auth/registration', JSON.stringify(values))
                .then((res) => {
                    alert("Registration Successful!");
                    navigation('/login');
                })
                .catch((error) => console.log(error));                  
            }}
        validationSchema={Yup.object({
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
            role: Yup.number("Something went wrong")
            })}

        render={({ errors, status, touched, getFieldProps, handleSubmit }) => (
        <section className="vh-100 bg-image">
          <div className="color-overlay">
            <div className="container py-5 h-100">
                <div className="row justify-content-center align-items-center h-100">
                    <div className="col-12 col-lg-9 col-xl-7">
                        <div className="card shadow-2-strong card-registration">
                            <div className="card-body p-4 p-md-5">
                                <h3 className="mb-4 pb-2 pb-md-0 mb-md-5">Registration Form</h3>
                                    <div className="row">
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" htmlFor="firstName">First Name</label>
                                            <input type="text" 
                                            className="form-control form-control-sm" 
                                            placeholder="First Name" 
                                            id="first_name" 
                                            {...getFieldProps('first_name')}/>
                                            
                                        </div>

                                        </div>
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" for="lastName">Last Name</label>
                                            
                                            <input type="text" 
                                            className="form-control form-control-sm" 
                                            placeholder="Last Name" 
                                            id="last_name" 
                                            {...getFieldProps('last_name')}/>
                                            
                                        </div>

                                        </div>
                                    </div>

                                    <div className="row">
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" htmlFor="email">Email Address</label>
                                            <input type="email" 
                                            className="form-control form-control-sm" 
                                            placeholder="Email" 
                                            id="email" 
                                            {...getFieldProps('email')}/>
                                            
                                        </div>

                                        </div>
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" htmlFor="username">Username</label>
                                            <input type="text" 
                                            className="form-control form-control-sm" 
                                            placeholder="Username" 
                                            id="username" 
                                            {...getFieldProps('username')}/>
                                            
                                        </div>

                                        </div>
                                    </div>


                                    <div className="row">
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" htmlFor="password1">Password</label>
                                            <input type="password" 
                                            className="form-control form-control-sm" 
                                            placeholder="Password" 
                                            id="password1" 
                                            {...getFieldProps('password1')}/>
                                            
                                        </div>

                                        </div>
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" htmlFor="password2">Confirm Password</label>
                                            <input type="password" 
                                            className="form-control form-control-sm" 
                                            placeholder="Confirm Password" 
                                            id="password2" 
                                            {...getFieldProps('password2')}/>
                                            
                                        </div>

                                        </div>
                                    </div>


                                    <div className="row">
                                      <div className="col-12">
                                        <label class="form-label select-label">Choose Role</label>
                                          <select className="select form-control" id="role"
                                            type="number"
                                            {...getFieldProps('role')} >
                                            <option value="0" disabled>Choose option</option>
                                            <option value="1">Resident</option>
                                            <option value="2">Donor</option>
                                            <option value="3">Barangay</option>
                                          </select>
                                      </div>
                                    </div>

                                    <div className="mt-4 pt-2">
                                      <button className="btn btn-primary  gradient-custom" onClick={handleSubmit}>Register</button>
                                    </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
          </div>
        </section>)}/>
        </>
    );
  }
export default function(props) {
    const navigation = useNavigate();
    return <Registration {...props} navigation={navigation} />;
    }
