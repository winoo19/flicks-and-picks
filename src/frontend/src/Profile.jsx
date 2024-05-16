import { Form, useLoaderData, useActionData, useNavigation } from "react-router-dom";
import Stack from "@mui/material/Stack";
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Table from '@mui/material/Table';
import TableCell from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import TableContainer from '@mui/material/TableContainer';
import { Chip, TableBody } from "@mui/material";
import TextField from '@mui/material/TextField';


export default function Profile() {
  const userData = useLoaderData();
  const responseError = useActionData();
  const navigation = useNavigation();
  const busy = navigation.state === 'submitting' || navigation.state === 'loading';
  const credIncorrectas = !busy && responseError;
  return (
    <Stack direction="row" justifyContent="center" alignItems="center"  className="profile-body"
      sx={{ width: 1, p: 4 }}>
      <Card variant="outlined" sx={{minWidth: '15%'}}>
        <CardContent>
          <Typography sx={{ fontSize: 14 }}>
            Welcome,
          </Typography>
          <Typography variant="h5" component="div">
            {userData.username}
          </Typography>
          <Divider><Chip label="Profile Data" size="small" sx={{ my: 2 }}/></Divider>
          <TableContainer component={Card}>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>Email</TableCell>
                  <TableCell align="right">{userData.email}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
        <Divider/>
        <CardActions sx={{justifyContent: "center"}}>
          <Form method="put" onSubmit={
            (event) => !confirm("This will delete your user, are you sure?") && event.preventDefault()
          }>
            <TextField margin="dense" size="small" required fullWidth disabled={busy}
                label="Password"
                name="password"
                id="password"
                type="password"
              />
              {credIncorrectas &&
                <Alert severity="error" sx={{ mt: 1, width: "100%", py: 0 }}>
                  Incorrect password.
                </Alert>
              }
            <Button id="unsubscribe-button" type="submit" variant="outlined" color="error" size="small">Unsubscribe</Button>
          </Form>
        </CardActions>
      </Card>
    </Stack>
  );
}