import '../App.css';
import { Component } from 'react';
import axios from "axios";
import { useFormik, Formik } from 'formik';
import * as Yup from 'yup';
import {
    Button,
    Card,
    CardHeader,
    CardBody,
    Dropdown,
    DropdownToggle,
    DropdownMenu,
    DropdownItem,
    FormGroup,
    Form,
    Input,
    InputGroupAddon,
    InputGroupText,
    InputGroup,
    Container,
    Row,
    Col,
    option
  } from "reactstrap";

  import packageJson from '../../package.json';



// Formik Tutorial: https://formik.org/docs/tutorial
// TODO: Consider using class-based handling using <Formik> (https://stackblitz.com/edit/react-formik-form-validation-gge2u7?file=App%2FRegister.jsx)
function Registration(props){
    const {history} = props;
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
            axios
                .post(baseSite + '/api/rest-auth/registration', JSON.stringify(values), {
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
        <section className="vh-100">
            <div className="container h-100">
                <div className="row d-flex justify-content-center align-items-center h-100">
                    <div className="col-xl-9">
                        <div className="card">
                            <div className="card-body">
                            <Form onSubmit={registrationForm.handleSubmit}>
                                <FormGroup className="row align-items-center pt-4 pb-3">
                                    <InputGroup className="input-group-alternative">
                                        <InputGroupAddon addonType="prepend">
                                            <InputGroupText>
                                            Username
                                            </InputGroupText>
                                        </InputGroupAddon>
                                        <Input 
                                            placeholder="Username" 
                                            id="username"
                                            type="text" 
                                            value={registrationForm.values.username}
                                            onChange={registrationForm.handleChange}/>
                                    </InputGroup>
                                </FormGroup>
                                <FormGroup>
                                    <InputGroup className="input-group-alternative">
                                    <InputGroupAddon addonType="prepend">
                                        <InputGroupText>
                                        Email
                                        </InputGroupText>
                                    </InputGroupAddon>
                                        <Input
                                            placeholder="Email"
                                            id="email"
                                            type="email" 
                                            value={registrationForm.values.email}
                                            onChange={registrationForm.handleChange}
                                        />
                                    </InputGroup>
                                </FormGroup>
                                <FormGroup>
                                    <InputGroup className="input-group-alternative">
                                    <InputGroupAddon addonType="prepend">
                                        <InputGroupText>
                                        Password
                                        </InputGroupText>
                                    </InputGroupAddon>
                                        <Input
                                            placeholder="Password"
                                            id="password1"
                                            type="password" 
                                            value={registrationForm.values.password1}
                                            onChange={registrationForm.handleChange}
                                        />
                                    </InputGroup>
                                </FormGroup>
                                <FormGroup>
                                    <InputGroup className="input-group-alternative">
                                    <InputGroupAddon addonType="prepend">
                                        <InputGroupText>
                                        Confirm Password
                                        </InputGroupText>
                                    </InputGroupAddon>
                                        <Input
                                            placeholder="Confirm Password"
                                            id="password2"
                                            type="password" 
                                            value={registrationForm.values.password2}
                                            onChange={registrationForm.handleChange}
                                        />
                                    </InputGroup>
                                </FormGroup>
                                <FormGroup>
                                    <InputGroup className="input-group-alternative">
                                    <InputGroupAddon addonType="prepend">
                                        <InputGroupText>
                                        First Name
                                        </InputGroupText>
                                    </InputGroupAddon>
                                        <Input
                                            placeholder="Confirm Password"
                                            id="first_name"
                                            type="text" 
                                            value={registrationForm.values.first_name}
                                            onChange={registrationForm.handleChange}
                                        />
                                    </InputGroup>
                                </FormGroup>
                                <FormGroup>
                                    <InputGroup className="input-group-alternative">
                                    <InputGroupAddon addonType="prepend">
                                        <InputGroupText>
                                        Last Name
                                        </InputGroupText>
                                    </InputGroupAddon>
                                        <Input
                                            placeholder="Last Name"
                                            id="last_name"
                                            type="text" 
                                            value={registrationForm.values.last_name}
                                            onChange={registrationForm.handleChange}
                                        />
                                    </InputGroup>
                                </FormGroup>
                                <FormGroup>
                                    <InputGroup className="input-group-alternative">
                                    <InputGroupAddon addonType="prepend">
                                        <InputGroupText>
                                        Role
                                        </InputGroupText>
                                    </InputGroupAddon>
                                        <Input
                                            id="role"
                                            type="number"
                                            value={registrationForm.values.role}
                                            onChange={registrationForm.handleChange}>
                                            <option value="1">
                                                Resident
                                            </option>
                                            <option value="2">
                                                Donor
                                            </option>
                                            <option value="3">
                                                Barangay
                                            </option>
                                            
                                        </Input>
                                    </InputGroup>
                                </FormGroup>

                                <div className="text-center">
                                    <Button className="my-4" color="primary" type="submit">Sign in</Button>
                                </div>
                            </Form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>


    )
  }
export default Registration;
