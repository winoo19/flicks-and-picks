import { Form, NavLink, useNavigation, useActionData, useLocation } from "react-router-dom";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Alert from "@mui/material/Alert";
import TextField from "@mui/material/TextField";
import LockIcon from "@mui/icons-material/Lock";
import LoadingButton from "@mui/lab/LoadingButton";


export default function Login() {
    const responseError = useActionData();
    const navigation = useNavigation();
    const busy = navigation.state === "submitting" || navigation.state === "loading";
    const credIncorrectas = !busy && responseError;

    const location = useLocation();
    // console.log(location);
    // // console.log(location.aboutProps);
    // const { setIsLogged } = location.state || {};
    const registrado = location.search === "?registered";

    return (
        <Stack direction="row" justifyContent="center" alignItems="center"
            sx={{ width: 1, height: "100vh" }}>
            <Paper elevation={4} sx={{ p: 2, borderRadius: 2 }}>
                <Form method="post">
                    <Stack direction="column" justifyContent="center" alignItems="center">
                        <LockIcon color="action" sx={{ fontSize: 40, mb: 2 }} />
                        <TextField margin="dense" size="small" required fullWidth disabled={busy}
                            label="Username"
                            name="username"
                            type="text"
                            id="username"
                        />
                        <TextField margin="dense" size="small" required fullWidth disabled={busy}
                            label="Password"
                            name="password"
                            type="password"
                            id="password"
                        />
                        {credIncorrectas &&
                            <Alert severity="error" sx={{ mt: 1, width: "100%", py: 0 }}>
                                Incorrect credentials.
                            </Alert>
                        }
                        {registrado && <Alert variant="outlined" sx={{ mt: 1, width: "100%", py: 0 }}>
                            Registered!
                        </Alert>}
                        <LoadingButton id="submit-button" type="submit" variant="contained" fullWidth sx={{ mt: 2, mb: 1 }}
                            loading={busy} disabled={busy}>
                            Enter
                        </LoadingButton>
                        <NavLink to="/register"><Button id="register-button" fullWidth disabled={busy}>Register</Button></NavLink>
                        <NavLink to="/"><Button id="cancel-button" fullWidth disabled={busy}>Cancel</Button></NavLink>
                    </Stack>
                </Form>
            </Paper>
        </Stack>
    )
}


