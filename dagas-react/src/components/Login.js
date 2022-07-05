import '../App.css';
import { Component } from 'react';
import axios from "axios";
import { useFormik, Formik } from 'formik';
import {
    Button,
    Card,
    CardHeader,
    CardBody,
    FormGroup,
    Form,
    Input,
    InputGroupAddon,
    InputGroupText,
    InputGroup,
    Container,
    Row,
    Col
  } from "reactstrap";

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
      <Container className="login">
        <Form onSubmit={loginForm.handleSubmit}>
            <FormGroup className="mb-3">
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
                        id="password"
                        type="password" 
                        value={loginForm.values.password}
                        onChange={loginForm.handleChange}
                    />
                </InputGroup>
            </FormGroup>
            <div className="text-center">
                <Button className="my-4" color="primary" type="submit">Sign in</Button>
            </div>
        </Form>
      </Container>
    )
  }
export default Login;
