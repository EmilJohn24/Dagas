import '../App.css';
import { Component } from 'react';
import axios from "axios";
import { useFormik, Formik } from 'formik';
import './Login.css';
import {
    Button,
    Card,
    CardHeader,
    CardBody,
    Input,
    InputGroupAddon,
    InputGroupText,
    InputGroup,
    Container,
    Row,
    Col
  } from "reactstrap";

import Form from "react-bootstrap/Form";
  

import packageJson from '../../package.json';



// Formik Tutorial: https://formik.org/docs/tutorial
// TODO: Consider using class-based handling using <Formik> (https://stackblitz.com/edit/react-formik-form-validation-gge2u7?file=App%2FRegister.jsx)
function Login(props){
    const {history} = props;
    //Formik Handling
    const loginForm = useFormik({
        initialValues: {
            username: '',
            password: '',
        },
        onSubmit: async values => {
            console.log(values);
            const data = await fetch('/api/rest-authlogin/', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify(values)
          });
          const {result} = await data.json();
          return result;                     
        },
    });

    return (
        <div className = 'bg-image'>
            <div className = 'color-overlay d-flex justify-content-center align-items-center'>
                <Form onSubmit={loginForm.handleSubmit} className="rounded p-4 p-sm-3">
                    <div className='mb-3'>
                        <img src = "logo.png" alt='logo'/>
                    </div>
                    <Form.Group className="mb-3" controlId='formUsername'>
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
                                value={loginForm.values.username}
                                onChange={loginForm.handleChange}/>
                        </InputGroup>
                    </Form.Group>

                    <Form.Group className="mb-3" controlId='formPassword'>
                        <InputGroup className="input-group-alternative">
                        <InputGroupAddon addonType="prepend">
                            <InputGroupText>
                            Password
                            </InputGroupText>
                        </InputGroupAddon>
                            <Input
                                placeholder="Password"
                                id="password"
                                type="password" 
                                value={loginForm.values.password}
                                onChange={loginForm.handleChange}
                            />
                        </InputGroup>
                    </Form.Group>
                    <Form.Group className="mb-3" controlId='formCheckbox'>
                        <Form.Check type= "checkbox" label="Remember Me"/>
                    </Form.Group>
                    <div className="text-center" controlId='formSubmitButton'>
                        <Button className="my-4" color="primary" type="submit">Sign in</Button>
                    </div>
                </Form>
            </div>
        </div>
    )
  }
export default Login;
