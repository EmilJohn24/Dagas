import '../App.css';


import './Login.css';

import Carousel from 'react-bootstrap/Carousel';

import logo from './logo.png'





import React from 'react';
import { useFormik, Formik, Field, Form, ErrorMessage } from 'formik';
import { useNavigate } from "react-router-dom";
import packageJson from '../../package.json';
import * as Yup from 'yup';

// Formik Tutorial: https://formik.org/docs/tutorial
// Useful: https://stackoverflow.com/questions/68905266/how-to-use-react-navigation-usenavigation-hook-in-a-class-component <3
// TODO: Consider using class-based handling using <Formik> (https://stackblitz.com/edit/react-formik-form-validation-gge2u7?file=App%2FRegister.jsx)
class Login extends React.Component {
    render() {
      // Get it from props
      const { navigation } = this.props;
        return (
            <><Formik
                initialValues={{
                    username: '',
                    password: ''
                }}
                validationSchema={Yup.object().shape({
                    username: Yup.string()
                        .required('Username is required'),
                    password: Yup.string()
                        .min(6, 'Password must be at least 6 characters')
                        .required('Password is required'),
                })}
                onSubmit={async (values) => {
                    console.log(values);
                    const data = await fetch('/api/rest-authlogin/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(values)
                    });
                    //   const {result} = await data.json();
                    if (data.status == 200) {
                        alert('success!');
                        navigation('/evacuation_centers')
                    }
                    else {
                        alert('login unsuccessful! Try again');
                    }
                    //   return result;                     
                } }
                // onSubmit={fields => {
                //     alert('SUCCESS!! :-)\n\n' + JSON.stringify(fields, null, 4));
                //     history.push('/home');
                // }}
                render={({ errors, status, touched }) => (

                    <section className="h-100 bg-image">
                        <div className="color-overlay">
                            <div className="container py-5 h-100">
                                <div className="row d-flex justify-content-center align-items-center h-100">
                                    <div className="col-xl-10">
                                        <div className="card rounded-3 text-black">
                                            <div className="row g-0">
                                                <div className="col-lg-6">
                                                    <div className="card-body p-md-5 mx-md-4">
                                                        <div className="text-center">
                                                            <img className= "logoSize" src={logo} alt="logo" />
                                                            <h4 className="mt-1 mb-5 pb-1 font-group">DAGAS</h4>
                                                        </div>
                                                        <Form>
                                                            <div className="form-outline mb-4 font-group">
                                                                <label htmlFor="username">Username</label>
                                                                <Field name="username" type="text" className={'form-control' + (errors.username && touched.username ? ' is-invalid' : '')} />
                                                                <ErrorMessage name="username" component="div" className="invalid-feedback" />
                                                            </div>
                                                            <div className="form-outline mb-4 font-group">
                                                                <label htmlFor="password">Password</label>
                                                                <Field name="password" type="password" className={'form-control' + (errors.password && touched.password ? ' is-invalid' : '')} />
                                                                <ErrorMessage name="password" component="div" className="invalid-feedback" />
                                                            </div>

                                                            <div class="text-center pt-1 mb-5 pb-1 font-group">
                                                                <button className="btn btn-primary btn-block fa-lg gradient-custom mb-3" type="submit">Login</button>
                                                                <a className="text-muted" href="#!">Forgot password?</a>
                                                            </div>

                                                            <div className="d-flex align-items-center justify-content-center pb-4 font-group">
                                                                <p className="text-center mt-2 mb-0">Don't have an account? <a href="" className="text-primary" onClick={()=>{navigation('/register')}}><u>Register</u></a></p>
                                                            </div>
                                                        </Form>

                                                    </div>
                                                </div>
                                                <div className="col-lg-6 d-flex align-items-center gradient-custom">
                                                    <div className="text-white px-3 py-4 p-md-5 mx-md-4">
                                                        <h4 className="mb-4">We are more than just a company</h4>
                                                        <p className="small mb-0">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                                                        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
                                                        exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                            
                )} />
                </>  
        )
    }
}

// Wrap and export
export default function(props) {
    const navigation = useNavigate();
  
    return <Login {...props} navigation={navigation} />;
  }

// function Login(props){
//     const {history} = props;
//     //Formik Handling
//     const loginForm = useFormik({
//         initialValues: {
//             username: '',
//             password: '',
//         },
//         onSubmit: async values => {
//             console.log(values);
//             const data = await fetch('/api/rest-authlogin/', {
//               method: 'POST',
//               headers: {
//                   'Content-Type': 'application/json'
//               },
//               body: JSON.stringify(values)
//           });
//           const {result} = await data.json();
//           console.log(data);
//           return result;                     
//         },
//     });

//     return (
//       <Container className="login">
//         <Form onSubmit={loginForm.handleSubmit}>
//             <FormGroup className="mb-3">
//                 <InputGroup className="input-group-alternative">
//                     <InputGroupAddon addonType="prepend">
//                         <InputGroupText>
//                         Username
//                         </InputGroupText>
//                     </InputGroupAddon>
//                     <Input 
//                         placeholder="Username" 
//                         id="username"
//                         type="text" 
//                         value={loginForm.values.username}
//                         onChange={loginForm.handleChange}/>
//                 </InputGroup>
//             </FormGroup>
//             <FormGroup>
//                 <InputGroup className="input-group-alternative">
//                 <InputGroupAddon addonType="prepend">
//                     <InputGroupText>
//                     Password
//                     </InputGroupText>
//                 </InputGroupAddon>
//                     <Input
//                         placeholder="Password"
//                         id="password"
//                         type="password" 
//                         value={loginForm.values.password}
//                         onChange={loginForm.handleChange}
//                     />
//                 </InputGroup>
//             </FormGroup>
//             <div className="text-center">
//                 <Button className="my-4" color="primary" type="submit">Sign in</Button>
//             </div>
//         </Form>
//       </Container>
//     )
//   }
// export default Login;
