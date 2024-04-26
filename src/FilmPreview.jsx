import { Box } from '@mui/material';
import { NavLink } from 'react-router-dom';
import RatingSquare from './RatingSquare';
import { useState } from 'react'


function FilmPreview({ film, isLogged }) {
    const [isHovered, setIsHovered] = useState(false);
  
    const handleMouseEnter = () => {
      setIsHovered(true);
    };
  
    const handleMouseLeave = () => {
      setIsHovered(false);
    };
  
    return (
      <div className="film-details" id="filmDetails">
        <NavLink to={isLogged ? `film/${film.id}` : "/login"}>
          <img
            src={film.image_url}
            alt="Thumbnail"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={{
              transition: "transform 0.3s ease",
              transform: isHovered ? "scale(1.08)" : "scale(1)", // Scale up when hovered
            }}
          />
        </NavLink>
        <div className="info">
          <div className="first-row">
            {/* <NavLink to={isLogged ? `film/${film.id}` : "/login"} className="film-title">
              <h2 id="title">{film.title}</h2>
            </NavLink> */}
            <NavLink to={"film/1"} className="film-title">
              <h2 id="title">{film.title}</h2>
            </NavLink>
            <Box className="rating-box">
              <RatingSquare rating={film.rating} />
            </Box>
          </div>
  
          <p>
            <strong>Genre:</strong> {film.genre}
          </p>
          <p>
            <strong>Summary:</strong> {film.summary}
          </p>
  
        </div>
      </div>
    );
  }

export default FilmPreview;