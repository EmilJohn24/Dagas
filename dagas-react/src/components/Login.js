import '../App.css';
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
                    <Form>
                        <div className="form-group">
                            <label htmlFor="username">Username</label>
                            <Field name="username" type="text" className={'form-control' + (errors.username && touched.username ? ' is-invalid' : '')} />
                            <ErrorMessage name="username" component="div" className="invalid-feedback" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <Field name="password" type="password" className={'form-control' + (errors.password && touched.password ? ' is-invalid' : '')} />
                            <ErrorMessage name="password" component="div" className="invalid-feedback" />
                        </div>
                        <div className="form-group">
                            <button type="submit" className="btn btn-primary mr-2">Login</button>
                            <button type="reset" className="btn btn-secondary">Reset</button>
                        </div>
                    </Form>
                )} />
                <button type="button" onClick={()=>{navigation('/register')}}> Register</button></>  
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
