import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import './index.css'

export default function Footer() {
    return <>
        <footer>
            <Box>
                {/* El pie está fijado abajo */}
                <Divider />
                <Typography variant="body2" align="center" sx={{ p: 1 }}>
                    {"Copyright © "}
                    <Link href="https://github.com/winoo19/flicks-and-picks" target="_blank">
                        DAS Final Project
                    </Link>{" "}
                    {new Date().getFullYear()}.
                </Typography>
            </Box>
        </footer>
    </>
};
