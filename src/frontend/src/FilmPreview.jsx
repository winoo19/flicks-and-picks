import { Box } from '@mui/material';
import { NavLink } from 'react-router-dom';
import RatingSquare from './RatingSquare';
import { useState, useEffect } from 'react';
import { profile } from './common/api.js';

function FilmPreview({ film }) {
  const [isHovered, setIsHovered] = useState(false);
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

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return (
    <div className="film-details" id={film.id}>
      <NavLink to={isLoggedIn ? `film/${film.id}` : '/login'}>
        <img
          src={film.image_url}
          alt="Thumbnail"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          style={{
            transition: 'transform 0.3s ease',
            transform: isHovered ? 'scale(1.08)' : 'scale(1)', // Scale up when hovered
          }}
          id="thumbnail"
        />
      </NavLink>
      <div className="info">
        <div className="first-row">
          <NavLink to={isLoggedIn ? `film/${film.id}` : '/login'} className="film-title">
            <h2 id="title">{film.name}</h2>
          </NavLink>
          <Box className="rating-box">
            <RatingSquare rating={film.avg_rating} />
          </Box>
        </div>
        <p>
          <strong>Genre:</strong> {film.genre}
        </p>
        <p>
          <strong>Summary:</strong> {film.description}
        </p>
      </div>
    </div>
  );
}

export default FilmPreview;
