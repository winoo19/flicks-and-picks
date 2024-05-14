import { Form, NavLink, useNavigation, useActionData, useLocation } from "react-router-dom";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Alert from "@mui/material/Alert";
import TextField from "@mui/material/TextField";
import LockIcon from "@mui/icons-material/Lock";
import LoadingButton from "@mui/lab/LoadingButton";
import { login } from "./common/api.js";

export default function Login() {
    // Errores del intento de login previo
    const responseError = useActionData();
    const navigation = useNavigation();
    const busy = navigation.state === "submitting" ||
        navigation.state === "loading";
    // Muestra el error de login a menos que estemos enviando algo
    const credIncorrectas = !busy && responseError;
    // Si el registro tuvo éxito, nos redirigieron a login con este query param
    
    const location = useLocation();
    const { setIsLogged } = location.state || {};
    const registrado = location.search === "?registered";

    const entry = async ({ request }) => {
        const formData = await request.formData();
        const { email, password } = Object.fromEntries(formData);
        const loginRes = await login(email, password);

        if (loginRes.ok) {
            setIsLogged(true);
            history.push("/");
            return redirect("/");
        };
    };

        return (
            <Stack direction="row" justifyContent="center" alignItems="center"
                sx={{ width: 1, height: "100vh" }}>
                {/* Tarjeta centrada vertical y horizontalmente */}
                <Paper elevation={4} sx={{ p: 2, borderRadius: 2 }}>
                    {/* Acción de React Router para enviar las credenciales */}
                    <Form method="post" onSubmit={entry}>
                        {/* Elementos del formulario apilados verticalmente */}
                        <Stack direction="column" justifyContent="center" alignItems="center">
                            {/* Icono de login */}
                            <LockIcon color="action" sx={{ fontSize: 40, mb: 2 }} />
                            {/* Campos de login: email y password */}
                            <TextField margin="dense" size="small" required fullWidth disabled={busy}
                                label="Email"
                                name="email"
                                type="email"
                            />
                            <TextField margin="dense" size="small" required fullWidth disabled={busy}
                                label="Password"
                                name="password"
                                type="password"
                            />
                            {/* Avisos durante el login */}
                            {credIncorrectas &&
                                <Alert severity="error" sx={{ mt: 1, width: "100%", py: 0 }}>
                                    Incorrect credentials.
                                </Alert>
                            }
                            {registrado && <Alert variant="outlined" sx={{ mt: 1, width: "100%", py: 0 }}>
                                Registered!
                            </Alert>}
                            <LoadingButton type="submit" variant="contained" fullWidth sx={{ mt: 2, mb: 1 }}
                                loading={busy} disabled={busy}>
                                Enter
                            </LoadingButton>
                            <NavLink to="/register"><Button fullWidth disabled={busy}>Register</Button></NavLink>
                            <NavLink to="/"><Button fullWidth disabled={busy}>Cancel</Button></NavLink>
                        </Stack>
                    </Form>
                </Paper>
            </Stack>
        )
    }


