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

import packageJson from '../../package.json';







// Formik Tutorial: https://formik.org/docs/tutorial
// TODO: Consider using class-based handling using <Formik> (https://stackblitz.com/edit/react-formik-form-validation-gge2u7?file=App%2FRegister.jsx)
function Registration(props){
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
                .then((res) => {result = res.data})
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
          return result;                     
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
                      
        })
    });

    return (

        <section className="vh-100 bg-image">
          <div className="color-overlay">
            <div className="container py-5 h-100">
                <div className="row justify-content-center align-items-center h-100">
                    <div className="col-12 col-lg-9 col-xl-7">
                        <div className="card shadow-2-strong card-registration">
                            <div className="card-body p-4 p-md-5">
                                <h3 className="mb-4 pb-2 pb-md-0 mb-md-5">Registration Form</h3>
                                <Form onSubmit={registrationForm.handleSubmit}>
                                    
                                    <div className="row">
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" htmlFor="firstName">First Name</label>
                                            <input type="text" 
                                            className="form-control form-control-sm" 
                                            placeholder="First Name" 
                                            id="first_name" 
                                            value={registrationForm.values.first_name}
                                            onChange={registrationForm.handleChange}/>
                                            
                                        </div>

                                        </div>
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" for="lastName">Last Name</label>
                                            
                                            <input type="text" 
                                            className="form-control form-control-sm" 
                                            placeholder="Last Name" 
                                            id="last_name" 
                                            value={registrationForm.values.last_name}
                                            onChange={registrationForm.handleChange}/>
                                            
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
                                            value={registrationForm.values.email}
                                            onChange={registrationForm.handleChange}/>
                                            
                                        </div>

                                        </div>
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" htmlFor="username">Username</label>
                                            <input type="text" 
                                            className="form-control form-control-sm" 
                                            placeholder="Username" 
                                            id="username" 
                                            value={registrationForm.values.username}
                                            onChange={registrationForm.handleChange}/>
                                            
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
                                            value={registrationForm.values.password1}
                                            onChange={registrationForm.handleChange}/>
                                            
                                        </div>

                                        </div>
                                        <div className="col-md-6 mb-4">

                                        <div className="form-outline">
                                            <label className="form-label" htmlFor="password2">Confirm Password</label>
                                            <input type="password" 
                                            className="form-control form-control-sm" 
                                            placeholder="Confirm Password" 
                                            id="password2" 
                                            value={registrationForm.values.password2}
                                            onChange={registrationForm.handleChange}/>
                                            
                                        </div>

                                        </div>
                                    </div>


                                    <div className="row">
                                      <div className="col-12">
                                        <label class="form-label select-label">Choose Role</label>
                                          <select className="select form-control" id="role"
                                            type="number"
                                            value={registrationForm.values.role}
                                            onChange={registrationForm.handleChange} >
                                            <option value="0" disabled>Choose option</option>
                                            <option value="1">Resident</option>
                                            <option value="2">Donor</option>
                                            <option value="3">Barangay</option>
                                          </select>
                                      </div>
                                    </div>

                                    <div className="mt-4 pt-2">
                                      <button className="btn btn-primary  gradient-custom" type="submit">Register</button>
                                    </div>
                                </Form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
          </div>
        </section>


        
        // <section className="vh-50 ">
        //     <div className="container h-50">
        //         <div className="row d-flex justify-content-center align-items-center h-50">
        //             <div className="col-xl-9">
        //                 <div className="card">
        //                     <div className="card-body">
        //                         <Form onSubmit={registrationForm.handleSubmit}>
        //                             <div className="row align-items-center pt-1 pb-1">
        //                                 <div className="col-md-3 ps-5">

        //                                     <h6 className="mb-0">Username</h6>

        //                                 </div>
        //                                 <div className="col-md-9 pe-5">
        //                                     <input type="text" 
        //                                     className="form-control form-control-sm" 
        //                                     placeholder="Username" 
        //                                     id="username" 
        //                                     value={registrationForm.values.username}
        //                                     onChange={registrationForm.handleChange}/>
        //                                 </div>
        //                             </div>

        //                             <hr className="mx-n3" />

        //                             <div className="row align-items-center pt-1 pb-1">
        //                                 <div className="col-md-3 ps-5">

        //                                     <h6 className="mb-0">Email Address</h6>

        //                                 </div>
        //                                 <div className="col-md-9 pe-5">

        //                                     <input type="email" 
        //                                     className="form-control form-control-sm" 
        //                                     placeholder="Email" 
        //                                     id="email" 
        //                                     value={registrationForm.values.email}
        //                                     onChange={registrationForm.handleChange}/>
        //                                 </div>
        //                             </div>

        //                             <hr className="mx-n3" />

        //                             <div className="row align-items-center pt-1 pb-1">
        //                                 <div className="col-md-3 ps-5">

        //                                     <h6 className="mb-0">Password</h6>

        //                                 </div>
        //                                 <div className="col-md-9 pe-5">

        //                                     <input type="password" 
        //                                     className="form-control form-control-sm" 
        //                                     placeholder="Password" 
        //                                     id="password1" 
        //                                     value={registrationForm.values.password1}
        //                                     onChange={registrationForm.handleChange}/>
        //                                 </div>
        //                             </div>

        //                             <hr className="mx-n3" />

        //                             <div className="row align-items-center pt-1 pb-1">
        //                                 <div className="col-md-3 ps-5">

        //                                     <h6 className="mb-0">Confirm Password</h6>

        //                                 </div>
        //                                 <div className="col-md-9 pe-5">

        //                                     <input type="password" 
        //                                     className="form-control form-control-sm" 
        //                                     placeholder="Confirm Password" 
        //                                     id="password2" 
        //                                     value={registrationForm.values.password2}
        //                                     onChange={registrationForm.handleChange}/>
        //                                 </div>
        //                             </div>

        //                             <hr className="mx-n3" />

        //                             <div className="row align-items-center pt-1 pb-1">
        //                                 <div className="col-md-3 ps-5">

        //                                     <h6 className="mb-0">First Name</h6>

        //                                 </div>
        //                                 <div className="col-md-9 pe-5">

        //                                     <input type="text" 
        //                                     className="form-control form-control-sm" 
        //                                     placeholder="First Name" 
        //                                     id="first_name" 
        //                                     value={registrationForm.values.first_name}
        //                                     onChange={registrationForm.handleChange}/>
        //                                 </div>
        //                             </div>

        //                             <hr className="mx-n3" />

        //                             <div className="row align-items-center pt-1 pb-1">
        //                                 <div className="col-md-3 ps-5">

        //                                     <h6 className="mb-0">Last Name</h6>

        //                                 </div>
        //                                 <div className="col-md-9 pe-5">

        //                                     <input type="text" 
        //                                     className="form-control form-control-sm" 
        //                                     placeholder="Last Name" 
        //                                     id="last_name" 
        //                                     value={registrationForm.values.last_name}
        //                                     onChange={registrationForm.handleChange}/>
        //                                 </div>
        //                             </div>

        //                             <hr className="mx-n3" />

        //                             <div className="row align-items-center pt-1 pb-1">
        //                                 <div className="col-md-3 ps-5">

        //                                     <h6 className="mb-0">Role</h6>

        //                                 </div>
        //                                 <div className="col-md-9 pe-5">

        //                                     <input id="role"
        //                                     type="number"
        //                                     value={registrationForm.values.role}
        //                                     onChange={registrationForm.handleChange}/>
        //                                     <option value="1">
        //                                         Resident
        //                                     </option>
        //                                     <option value="2">
        //                                         Donor
        //                                     </option>
        //                                     <option value="3">
        //                                         Barangay
        //                                     </option>
        //                                 </div>
        //                             </div>

        //                             <hr className="mx-n3" />


                                

        //                         <div className="text-center">
        //                             <Button className="my-4" color="primary" type="submit">Sign in</Button>
        //                         </div>
        //                     </Form>
        //                     </div>
        //                 </div>
        //             </div>
        //         </div>
        //     </div>
        // </section>


    )
  }
export default Registration;
