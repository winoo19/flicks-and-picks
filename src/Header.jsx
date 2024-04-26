import { NavLink } from "react-router-dom";
import logoImage from "../favicon.png";
import { InputBase } from "@mui/material";
import { Search as SearchIcon } from "@mui/icons-material";
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import './index.css'

export default function Header({ isLogged, setIsLogged, setFilmList }) {

    const fetchFilms = async (filter) => {
        try {
          const response = await fetch(`/user/film/${filter}`);
          if (!response.ok) {
            throw new Error("Couldn't load film list");
          }
          const data = await response.json();
          setFilmList(data.films);
        } catch (error) {
          console.error("Error loading films...", error);
        }
      };

    const FilterFilms = (event) => {
        const filter = event.target.value;
        fetchFilms(filter);
    }

    return (
        <header>
            <div className="logo">
                <img src={logoImage} alt="Logo" />
            </div>
            <h1>Flicks & Picks</h1>
            <nav>
                <Stack direction="row" spacing={2}>
                    <NavLink to="/search" className="search">
                        <SearchIcon className="search-icon" />
                    </NavLink>
                    <InputBase
                        className="base-icon"
                        placeholder="Search"
                        inputProps={{ "aria-label": "search" }}
                        onChange={FilterFilms}
                        style={{ "color": "#e5dac6", "font-size": "1.5vw", "margin-left": "1vw", "maxWidth": "12vw"}} />
                    {!isLogged && (
                        <>
                            <NavLink to={{pathname: "/login", state: {setIsLogged: setIsLogged}}} className="login">
                                <Button variant="contained">Login</Button>
                            </NavLink>
                            <NavLink to="/register" className="register">
                                <Button variant="contained">Register</Button>
                            </NavLink>
                        </>
                    )}
                    {isLogged && (
                        <NavLink to={{pathname: "/register", state: {setIsLogged: setIsLogged}}} className="profile">
                            <Button variant="contained">Profile</Button>
                        </NavLink>
                    )}

                </Stack>
            </nav>

        </header>
    );
}
