import { useLoaderData, useNavigation, Form, useActionData } from "react-router-dom";
import Stack from "@mui/material/Stack";
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Divider from '@mui/material/Divider';
import AccountBoxIcon from '@mui/icons-material/AccountBox';

export default function UpdateProfile() {
  const responseError = useActionData();
  const userData = useLoaderData();
  const navigation = useNavigation();
  const busy = navigation.state === 'submitting' || navigation.state === 'loading';
  const credIncorrectas = !busy && responseError;

  return (
    <Stack direction="row" justifyContent="center" alignItems="center"
      sx={{ width: 1, p: 4 }}>
      <Card variant="outlined" sx={{ minWidth: '15%' }}>
        <Form method="put">
          <CardContent>
            <Stack direction="column" justifyContent="center" alignItems="center">
              <AccountBoxIcon color="action" sx={{ fontSize: 40, mb: 2 }} />
              <TextField margin="dense" size="small" fullWidth disabled={busy}
                label="Name"
                name="username"
                id="username"
                defaultValue={userData.username}
              />
              <TextField margin="dense" size="small" fullWidth disabled={busy}
                label="Email"
                name="email"
                type="email"
                id="email"
                defaultValue={userData.email}
              />
              <TextField margin="dense" size="small" required fullWidth disabled={busy}
                label="Current Password"
                name="current_password"
                id="current-password"
                type="password"
              />
              <TextField margin="dense" size="small" required fullWidth disabled={busy}
                label="New Password"
                name="new_password"
                id="new-password"
                type="password"
              />
              {credIncorrectas &&
                <Alert severity="error" sx={{ mt: 1, width: "100%", py: 0 }}>
                  Incorrect credentials.
                </Alert>
              }
            </Stack>
          </CardContent>
          <Divider />
          <CardActions sx={{ justifyContent: "center" }}>
            {/* Botón para enviar los datos del usuario */}
            <Button id="update-button" type="submit" variant="outlined" color="warning" size="small" disabled={busy}>
              Update
            </Button>
          </CardActions>
        </Form>
      </Card>
    </Stack>
  );
}
