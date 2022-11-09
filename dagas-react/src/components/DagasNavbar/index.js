import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Offcanvas from 'react-bootstrap/Offcanvas';
import { NavLink } from 'react-router-dom';
import routes from 'routes.js'

function DagasNavbar(){
    const renderCollapse = (collapses) => {
        collapses.map(({name, collapse, route, href, key}) => {
            return (<NavDropdown.Item href='#'>
                <NavLink to={route} key={key}>{name}</NavLink>
            </NavDropdown.Item>);
        });
    }; 
    const expand = false;
    return (
        <>
          {/* {[false, 'sm', 'md', 'lg', 'xl', 'xxl'].map((expand) => ( */}
            <Navbar key={expand} bg="dark" expand={expand} className="mb-3">
              <Container fluid>
                <Navbar.Brand href="#">Dagas</Navbar.Brand>
                <Navbar.Toggle aria-controls={`offcanvasNavbar-expand-${expand}`} 
                  />
                <Navbar.Offcanvas 
                  id={`offcanvasNavbar-expand-${expand}`}
                  aria-labelledby={`offcanvasNavbarLabel-expand-${expand}`}
                  placement="start"
                >
                  <Offcanvas.Header closeButton>
                    <Offcanvas.Title 
                    id={`offcanvasNavbarLabel-expand-${expand}`}>
                      Dagas
                    </Offcanvas.Title>
                  </Offcanvas.Header>
                  <Offcanvas.Body>
                    <Nav className="justify-content-end flex-grow-1 pe-3">
                      {/* <Nav.Link href="#action1">Home</Nav.Link>
                      <Nav.Link href="#action2">Link</Nav.Link>
                      <NavDropdown
                        title="Dropdown"
                        id={`offcanvasNavbarDropdown-expand-${expand}`}
                      > */}
                        {
                            routes.map(
                                ({type, name, icon, title, collapse, noCollapse, key, href, route}) => {
                                    if (type == "collapse"){
                                        if (noCollapse){
                                            <Nav.Link href='#'>
                                                <NavLink to={route} key={key}>{name}</NavLink>
                                            </Nav.Link>
                                        } else{
                                            return(
                                            <NavDropdown title={name}>
                                                {renderCollapse(collapse)}  
                                            </NavDropdown>
                                            );
                                        }
                                            

                                    }
                                }
                            )
                        }
                        {/* <NavDropdown.Item href="#action3">Action</NavDropdown.Item>
                        <NavDropdown.Item href="#action4">
                          Another action
                        </NavDropdown.Item>
                        <NavDropdown.Divider />
                        <NavDropdown.Item href="#action5">
                          Something else here
                        </NavDropdown.Item> */}
                      {/* </NavDropdown> */}
                    </Nav>
                    
                  </Offcanvas.Body>
                </Navbar.Offcanvas>
              </Container>
            </Navbar>
          {/* ))} */}
        </>
      );
}



export default DagasNavbar;