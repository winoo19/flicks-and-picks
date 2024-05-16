import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import logoImage from '../favicon.png';
import { InputBase } from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import { profile } from './common/api.js';

export default function Header({ setFilmList }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Function to fetch profile info and update isLoggedIn state
    const fetchProfileInfo = async () => {
      try {
        const response = await profile();
        setIsLoggedIn(response.ok); // Update isLoggedIn based on response status
      } catch (error) {
        setIsLoggedIn(false); // Set isLoggedIn to false on error
      }
    };

    fetchProfileInfo(); // Call fetchProfileInfo when the component mounts
  }, []); // Empty dependency array ensures this effect runs only once on mount

  const handleFilterFilms = (event) => {
    const filter = event.target.value;
    fetchFilms(filter);
  };

  const fetchFilms = async (filter) => {

    const GENRE_CHOICES = [
      "Action",
      "Comedy",
      "Crime",
      "Documentary",
      "Drama",
      "Horror",
      "Romance",
      "Sci-Fi",
      "Thriller",
      "Western"
    ]

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

    // Distinguish between Number or String input
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
      dataToSend["description"] = filter;

      // Genre must be a valid one
      const filterPattern = new RegExp('.*' + escapeRegExp(filter) + '.*', 'i');
      function escapeRegExp(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      }
      let matchedGenre = null;
      for (let i = 0; i < GENRE_CHOICES.length; i++) {
        const genre = GENRE_CHOICES[i];
        if (filterPattern.test(genre)) {
          matchedGenre = genre;
          break; // Stop after finding the first matching genre
        }
      }
      const genre = matchedGenre ? matchedGenre : null;
      dataToSend["genre"] = genre;
    }

    const body = JSON.stringify(dataToSend);
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

  return (
    <header>
      <div className="logo">
        <img src={logoImage} alt="Logo" />
      </div>
      <h1>Flicks & Picks</h1>
      <nav>
        <Stack direction="row" spacing={2}>
          <SearchIcon className="search" />
          <InputBase
            id="search"
            placeholder="Search"
            inputProps={{ 'aria-label': 'search' }}
            onChange={handleFilterFilms}
            style={{ color: '#e5dac6', fontSize: '1.5vw', marginLeft: '1vw', maxWidth: '12vw' }}
          />
          {!isLoggedIn ? (
            <>
              <NavLink to="/login" className="login">
                <Button variant="contained" id="login-button">
                  Login
                </Button>
              </NavLink>
              <NavLink to="/register" className="register">
                <Button variant="contained" id="register-button">
                  Register
                </Button>
              </NavLink>
            </>
          ) : (
            <NavLink to="/profile-app/profile" className="profile">
              <Button variant="contained" id="profile-button">
                Profile
              </Button>
            </NavLink>
          )}
        </Stack>
      </nav>
    </header>
  );
}






