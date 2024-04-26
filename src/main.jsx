import React, { useState } from "react"
import ReactDOM from "react-dom/client"
import ListPage from "./ListPage.jsx"
import { login, logout, register, profile, unsubscribe, film_details, film_review } from "./common/api.js";
import App from "./App.jsx"
import Film from "./Film.jsx"
import Error from "./Error.jsx"
import Login from "./Login.jsx"
import Register from "./Register.jsx"
import "./index.css"
import { createBrowserRouter, RouterProvider } from "react-router-dom";


const router = createBrowserRouter([{
  path: "/",
  element: <App />,
  children: [{
    path: "",
    element: <ListPage />
  },{
    path: "film/1",
    element: <Film />,
    errorElement: <Error />,
    // loader: ({ params }) => load_film_review(params.filmId, params.userId),
    // action: update_review
  // }
  }],
}, {
  path: "/login",
  element: <Login />,
  // action: entry
}, {
  path: "/register",
  element: <Register />,
  action: registerUser
}]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)

// Functions

async function load_film_review(film_id, user_id) {
  try {
    const [filmDetails, filmReview] = await Promise.all([
      film_details(film_id),
      film_review(film_id, user_id)
    ]);

    if (filmDetails.ok && filmReview) {
      return { filmDetails, filmReview };
    } else {
      redirect("/");
    }
  } catch (error) {
    console.error("Error loading film review:", error);
    redirect("/");
  }
}

async function registerUser({ request }) {
  const formData = await request.formData();
  const usuario = Object.fromEntries(formData);
  const registerRes = await register(usuario);
  if (registerRes.ok) return redirect("/?registered");
  return { status: registerRes.status };
}

async function exit() {
  const logoutRes = await logout();
  if (logoutRes.ok) return redirect("/");
  return { status: logoutRes.status };
}

async function loadUser() {
  const profileRes = await profile();
  if (profileRes.ok) return profileRes;
  return redirect("/");
}

async function unsubscribeUser() {
  await unsubscribe();
  return redirect("/");
}

async function updateUser({ request }) {
  const formData = await request.formData();
  const data = Object.fromEntries(formData);
  const updatedProfileRes = await profile(data);
  if (updatedProfileRes.ok) return redirect("/app/perfil");
  return redirect("/");
}
