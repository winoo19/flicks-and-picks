import { useState } from "react";
import { Form, NavLink, useNavigation, useActionData } from "react-router-dom";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Alert from "@mui/material/Alert";
import TextField from "@mui/material/TextField";
import AccountBoxIcon from "@mui/icons-material/AccountBox";
import LoadingButton from "@mui/lab/LoadingButton";

export default function Register() {
  const responseError = useActionData();
  const navigation = useNavigation();
  const busy = navigation.state === "submitting" || 
               navigation.state === "loading";
  const registerError = !busy && responseError;

  const onChangePassword = (event) => {
    setPassword(event.target.value)
   }
   const onChangePassword2 = (event) => {
    setPassword2(event.target.value)
   }
  const [password, setPassword] = useState(null);
  const [password2, setPassword2] = useState(null);
  const differentPasswords = (password2 && password) && (password !== password2);

  return (
    <Stack direction="row" justifyContent="center" alignItems="center"
      sx={{ width: 1, height: "100vh" }}>
      {/* Tarjeta centrada vertical y horizontalmente */} 
      <Paper elevation={4} sx={{ p: 2, borderRadius: 2 }}>
        {/* Acción de React Router para enviar el registro */}
        <Form method="post">
          {/* Elementos del formulario apilados verticalmente */} 
          <Stack direction="column" justifyContent="center" alignItems="center">
            {/* Icono de registro */}
            <AccountBoxIcon color="action" sx={{ fontSize: 40, mb: 2 }}/>
            {/* Campos de registro: nombre, teléfono, email, password, password2 */} 
            <TextField margin="dense" size="small" required fullWidth disabled={busy}
              label="Name"
              name="username"
              id="username"
            />
            <TextField margin="dense" size="small" required fullWidth disabled={busy}
              label="Email"
              name="email"
              type="email"
              id="email"
            />
            <TextField  margin="dense" size="small" required fullWidth disabled={busy}
              label="Password"
              name="password"
              type="password"
              id="password"
              onChange={onChangePassword}
            />
            <TextField  margin="dense" size="small" required fullWidth
              label="Repeat password"
              name="password2"
              type="password"
              id="password2"
              onChange={onChangePassword2}
              error={differentPasswords}
              helperText={differentPasswords && "Las contraseñas deben coincidir"}
            />
            <Alert variant="outlined" severity="error" sx={{
              mt:1, width:"100%", py:0, visibility: registerError ? "visible" : "hidden"}}>
              {registerError && registerError.status === 409 ? "User already registered" : "Error registering" }
            </Alert>
            <LoadingButton id="submit-button" type="submit" variant="contained" fullWidth sx={{mt:2,mb:1}} 
              loading={busy} disabled={busy || differentPasswords}>
                Register
            </LoadingButton>
            <NavLink to="/login">
              <Button id="login-button" disabled ={busy}>Log In</Button>
            </NavLink>
            <NavLink to="/">
              <Button id="cancel-button" disabled={busy}>Cancel</Button>
            </NavLink>
          </Stack>
        </Form>
      </Paper>
    </Stack>
  )
}


