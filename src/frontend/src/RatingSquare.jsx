import { Box } from "@mui/material";

const RatingSquare = ({ rating }) => {
  const getColor = (rating) => {
    if (rating >= 8.5) {
      return "#4caf50";
    } else if (rating >= 5) {
      return "#ff9800";
    } else {
      return "#f44336";
    }
  };

  return (
    <Box
      sx={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: "40px",
        height: "40px",
        borderRadius: "4px",
        backgroundColor: getColor(rating),
        color: "#ffffff",
        fontWeight: "bold",
        fontSize: "16px",
      }}
    >
      {rating}
    </Box>
  );
};

export default RatingSquare;