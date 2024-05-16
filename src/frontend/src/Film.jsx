import { Box, Button, IconButton, TextField } from "@mui/material";
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { NavLink, useLoaderData, useNavigation, Form } from "react-router-dom";
import RatingSquare from "./RatingSquare";
import './index.css'


function Film() {
  const filmData = useLoaderData();
  const filmDetails = filmData.filmDetails;
  const filmReviews= filmData.filmReviews;
  const filmUserReview = filmData.userReview;
  const navigation = useNavigation();
  const busy = navigation.state === 'submitting' || navigation.state === 'loading';

  console.log("details", filmDetails);
  console.log("reviews", filmReviews);
  console.log("user review", filmUserReview);
  if (!filmDetails) {
    return <div>Loading...</div>;
  }

  const isUserReview = (filmUserReview !== null && filmUserReview !== undefined);

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

  const renderReviews = () => {
    return filmReviews.reviews.map((review, index) => (
      <div key={index} className="review">
        <p>{review.content}</p>
        {<p>Rating: {review.rating}</p>}
      </div>
    ));
  };

  return (
    <div className="film-details" id="filmDetails">
      <div className="first-column-details">
        <div className="back-button">
          <NavLink to={"/"}>
            <IconButton>
              <ArrowBackIcon></ArrowBackIcon>
            </IconButton>
            <Button id="back-button" variant="text">BACK TO FILMS</Button>
          </NavLink>
        </div>
        <img className="details-image" src={filmDetails.image_url} alt="Thumbnail" />
      </div>
      <div className="info">
        <div className="first-row">
          <h1>{filmDetails.title}</h1>
          <Box className="rating-box">
            <RatingSquare rating={filmDetails.avg_rating} />
          </Box>
        </div>
        <p> <strong>Genre:</strong> {filmDetails.genre}</p>
        <p> <strong>Summary:</strong> {filmDetails.description}</p>
        <p> <strong>Director:</strong> {filmDetails.director}</p>
        <p> <strong>Length:</strong> {filmDetails.duration} min</p>
        <p> <strong>Cast:</strong> {castString}</p>
        <p> <strong>Release Date:</strong> {filmDetails.release}</p>
        <p> <strong>Reviews:</strong></p>
        <div>
          {renderReviews()}
        </div>
        <div>
          <Form method="post" className="review-section">
            <p> <strong>Review:</strong></p>
            {/* <label htmlFor="review"><strong>Review:</strong></label> */}
            <TextField margin="dense" disabled={busy}
              id="review"
              label="Your Review"
              name="content"
              multiline
              rows={3}
              defaultValue={isUserReview ? filmUserReview.review : ""}
            />
            <TextField margin="dense" size="small" disabled={busy}
              id="score"
              label="Score"
              name="rating"
              type="number"
              style={{ width: "10%" }}
              defaultValue={isUserReview ? filmUserReview.rating : ""}
              InputProps={{
                inputProps: {
                  min: 1,
                  max: 10,
                },
              }}
            />
            <input
              type="hidden"
              id="film-id"
              name="film_id"
              value={filmDetails.id}
            />
            <Button type="submit" style={{ width: "10%" }}
              variant="outlined"
              id="update-button"
              color="warning" size="small" disabled={busy} margin="dense">
              Update
            </Button>
          </Form>
        </div>
      </div>
    </div>

  );
}

export default Film;
