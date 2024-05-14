import { NavLink } from "react-router-dom";
import logoImage from "../favicon.png";
import { InputBase } from "@mui/material";
import { ControlCameraOutlined, Search as SearchIcon } from "@mui/icons-material";
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import './index.css'

export default function Header({ isLogged, setIsLogged, setFilmList, userId, setUserId }) {
    const fetchFilms = async (filter) => {
        
        let dataToSend = {
            "film_name": null,
            "director_name": null,
            "actor_name": null,
            "genre": null,
            "description": null,
            "min_release": null,
            "max_release": null,
            "min_rating": null,
            "max_rating": null
        }

        const regex = /[a-zA-Z]/;
        const hasText = regex.test(filter);

        if (!hasText) {
            const numberMatches = filter.match(/\d+/g);
            if (numberMatches) {
                const number = parseInt(filter);
                if (number > 10) {
                    dataToSend["min_release"] = number;
                    dataToSend["max_release"] = number;
                }
                else if (0 <= number && number <= 10) {
                    dataToSend["min_score"] = number;
                    dataToSend["max_score"] = number;
                }
            }
        }
        else {
            dataToSend["film_name"] = filter;
            dataToSend["director_name"] = filter;
            dataToSend["actor_name"] = filter;
            dataToSend["genre"] = filter;
            dataToSend["description"] = filter;
        }

        const body = JSON.stringify(dataToSend);
        console.log(body);
        try {
            const response = await fetch("http://127.0.0.1:8000/films/", {
                method: "post",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: body
            });
            if (!response.ok) {
                throw new Error("Couldn't load film list");
            }
            const data = await response.json();

            setFilmList(data.films);
            
        } catch (error) {
            console.error("Error loading films...", error);
        };
    }

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
                        style={{ "color": "#e5dac6", "fontSize": "1.5vw", "marginLeft": "1vw", "maxWidth": "12vw" }} />
                    {!isLogged && (
                        <>
                            <NavLink to={{ pathname: "/login", state: { setIsLogged: setIsLogged } }} className="login">
                                <Button variant="contained">Login</Button>
                            </NavLink>
                            <NavLink to="/register" className="register">
                                <Button variant="contained">Register</Button>
                            </NavLink>
                        </>
                    )}
                    {isLogged && (
                        <NavLink to={{ pathname: "/register", state: { setIsLogged: setIsLogged } }} className="profile">
                            <Button variant="contained">Profile</Button>
                        </NavLink>
                    )}

                </Stack>
            </nav>

        </header>
    );
}

