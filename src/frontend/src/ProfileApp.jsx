import { Outlet, NavLink, Form, useNavigation, useLocation, redirect } from "react-router-dom";
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Button from '@mui/material/Button';
import LinearProgress from '@mui/material/LinearProgress';
import Footer from "./Footer.jsx";

export default function App() {
  const navigation = useNavigation();
  const busy = navigation.state === 'submitting' || navigation.state === 'loading';

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar variant="dense">
          <Box sx={{ flexGrow: 1 }} className="profile-box">
            <NavLink to="profile" end>
              {({ isActive }) => <BotonMenu className="profile-letter" id="to-profile-button" isActive={isActive}>Profile</BotonMenu>}
            </NavLink>
            <NavLink to="profile-update" end>
              {({ isActive }) => <BotonMenu className="profile-letter" id="to-update-profile-button" isActive={isActive}>Update Profile</BotonMenu>}
            </NavLink>
            <NavLink to="/" end>
              {({ isActive }) => <BotonMenu className="profile-letter" id="back-button" isActive={isActive}>Back to films</BotonMenu>}
            </NavLink>
          </Box>
          <Form method="post">
            <Button type="submit" id="logout-button" color="inherit">Logout</Button>
          </Form>

        </Toolbar>
        {busy && <LinearProgress color="inherit" />}
      </AppBar>
      <Outlet />
      <Footer />
    </Box>
  );
}

function BotonMenu({ isActive, children }) {
  return <Button color="inherit" sx={{ fontWeight: isActive ? "bolder" : "lighter" }}>{children}</Button>;
}