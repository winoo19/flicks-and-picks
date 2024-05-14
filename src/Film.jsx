import { Box, Button, IconButton, TextField } from "@mui/material";
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { NavLink, useLoaderData, useNavigation, Form } from "react-router-dom";
import RatingSquare from "./RatingSquare";
import './index.css'


function Film() {
  // const { filmDetails, filmReview } = useLoaderData();
  const filmDetails = {
    "id": 7,
    "title": "Forrest Gump",
    "genre": "Drama",
    "length": 142,
    "director": "Robert Zemeckis",
    "cast": ["Tom Hanks", "Robin Wright", "Gary Sinise"],
    "summary": "The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate, and other historical events unfold from the perspective of an Alabama man with an IQ of 75, whose only desire is to be reunited with his childhood sweetheart.",
    "image_url": "https://m.media-amazon.com/images/M/MV5BZTY4NjcxNDctZmVjMC00NzM0LWIxYTctNjdhNzdlN2VkNjNiXkEyXkFqcGdeQXVyMDM2NDM2MQ@@._V1_.jpg",
    "year": 1994,
    "rating": 8
  };


  let filmReview = {
    "score": 4,
    "review": "Very good."
  }

  const navigation = useNavigation();
  const busy = navigation.state === 'submitting' ||
    navigation.state === 'loading';

  if (!filmDetails) {
    return <div>Loading...</div>;
  }

  let castString = "";
  const castLength = filmDetails.cast.length;
  for (const [index, actor] of filmDetails.cast.entries()) {
    console.log(index);
    if (index < castLength - 1) {
      castString += actor + ", ";
    } else {
      castString += " and " + actor + ".";
    }
  };

  return (
    <div className="film-details" id="filmDetails">
      <div className="first-column-details">
        <div className="back-button">
          <NavLink to={"/"}>
            <IconButton>
              <ArrowBackIcon></ArrowBackIcon>
            </IconButton>
            <Button variant="text">BACK TO FILMS</Button>
          </NavLink>
        </div>
        <img className="details-image" src={filmDetails.image_url} alt="Thumbnail" />
      </div>
      <div className="info">
        <div className="first-row">
          <h1>{filmDetails.title}</h1>
          <Box className="rating-box">
            <RatingSquare rating={filmDetails.rating} />
          </Box>
        </div>
        <p> <strong>Genre:</strong> {filmDetails.genre}</p>
        <p> <strong>Summary:</strong> {filmDetails.summary}</p>
        <p> <strong>Director:</strong> {filmDetails.director}</p>
        <p> <strong>Length:</strong> {filmDetails.length}</p>
        <p> <strong>Cast:</strong> {castString}</p>
        <p> <strong>Year:</strong> {filmDetails.year}</p>
        <div>
          <Form method="put" className="review-section">
            <p> <strong>Review:</strong></p>
            {/* <label htmlFor="review"><strong>Review:</strong></label> */}
            <TextField margin="dense" disabled={busy}
              label="Review"
              name="review"
              multiline
              rows={3}
              fullWidth="false"
              defaultValue={filmReview.review ? filmReview.review : ""}
            />
            <TextField margin="dense" size="small" disabled={busy}
              label="Score"
              name="score"
              type="number"
              style={{ width: "10%" }}
              defaultValue={filmReview.score ? filmReview.score : ""}
              InputProps={{
                inputProps: {
                  min: 1,
                  max: 10,
                },
              }}
            />
            <Button type="submit" style={{ width: "10%" }} variant="outlined" color="warning" size="small" disabled={busy} margin="dense">
              Update
            </Button>
          </Form>
        </div>
      </div>
    </div>

  );
}

export default Film;
