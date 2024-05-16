import React from "react"
import ReactDOM from "react-dom/client"
import ListPage from "./ListPage.jsx"
import {
  login, logout, register, profile, updateProfile, unsubscribe,
  filmDetails, filmReviews, userReviews, updateReviewData,
  deleteReviewData
} from "./common/api.js";
import App from "./App.jsx"
import Film from "./Film.jsx"
import Error from "./Error.jsx"
import Login from "./Login.jsx"
import Register from "./Register.jsx"
import Profile from "./Profile.jsx"
import ProfileApp from "./ProfileApp.jsx"
import UpdateProfile from "./UpdateProfile.jsx"
import "./index.css"
import { createBrowserRouter, RouterProvider, redirect } from "react-router-dom";


const router = createBrowserRouter([{
  path: "/",
  element: <App />,
  children: [{
    path: "",
    element: <ListPage />
  }, {
    path: "film/:filmId",
    element: <Film />,
    errorElement: <Error />,
    loader: ({ params }) => loadFilmReview(params.filmId),
    action: updateReview
  }],
}, {
  path: "/login",
  element: <Login />,
  action: entry
}, {
  path: "/register",
  element: <Register />,
  action: registerUser
}, {
  path: "/profile-app",
  element: <ProfileApp />,
  action: logoutUser,
  children: [{
    path: "profile",
    element: <Profile />,
    loader: loadUser,
    action: unsubscribeUser
  }, {
    path: "profile-update",
    element: <UpdateProfile />,
    loader: loadUser,
    action: updateUser
  }]
}]);


ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)

// Functions
async function loadFilmReview(filmId) {
  try {
    const [filmDetailsRes, filmReviewsRes, userReviewsRes] = await Promise.all([
      filmDetails(filmId),
      filmReviews(filmId),
      userReviews()
    ]);

    if (filmDetailsRes.ok && filmReviewsRes.ok && userReviewsRes.ok) {
      const filmDetailsData = await filmDetailsRes.json();
      const filmReviewsData = await filmReviewsRes.json();
      const userReviewsData = await userReviewsRes.json();
      console.log(userReviewsData);
      const review = userReviewsData.reviews.find(review => review.film_id === filmId);

      const aggregatedData = {
        filmDetails: filmDetailsData,
        filmReviews: filmReviewsData,
        userReview: review
      };
      console.log(aggregatedData);

      return aggregatedData;
    }
  } catch (error) {
    console.error("Error loading film review:", error);
    redirect("/");
  }
}

async function entry({ request }) {
  const formData = await request.formData();
  const user = Object.fromEntries(formData);
  const registerRes = await login(user);
  if (registerRes.ok) return redirect("/");
  return { status: registerRes.status };
}

async function registerUser({ request }) {
  const formData = await request.formData();
  const user = Object.fromEntries(formData);
  const registerRes = await register(user);
  if (registerRes.ok) return redirect("/login/?registered");
  return { status: registerRes.status };
}

async function updateReview({ request }) {
  const formData = await request.formData();
  const data = Object.fromEntries(formData);

  if (data.review || data.rating) {
    const updatedReviewRes = await updateReviewData(data);
    if (updatedReviewRes.ok) return redirect("/");
    return { status: updatedReviewRes.status };
  } else {
    const filmIdData = { film_id: data.filmId };
    const updatedReviewRes = await deleteReviewData(filmIdData);
    if (updatedReviewRes.ok) return redirect("/");
    return { status: updatedReviewRes.status };
  }
}

async function loadUser() {
  const profileRes = await profile();
  if (profileRes.ok) {
    const profileData = await profileRes.json();
    return profileData;
  }
  return redirect("/");
}

async function unsubscribeUser({ request }) {
  const formData = await request.formData();
  const data = Object.fromEntries(formData);

  await unsubscribe(data);
  return redirect("/");
}

async function logoutUser() {
  const logoutRes = await logout();
  if (logoutRes.ok) {
    return redirect("/");
  };
  return { status: logoutRes.status };
};

async function updateUser({ request }) {
  const formData = await request.formData();
  const data = Object.fromEntries(formData);
  const updatedProfileRes = await updateProfile(data);
  if (updatedProfileRes.ok) return redirect("/profile-app/profile");
  return redirect("/");
}
