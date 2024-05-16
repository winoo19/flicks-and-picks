export function login(data) {
  const body = JSON.stringify(data);
  return fetch(`http://127.0.0.1:8000/users/login/`, {
    method: "post",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include",
    body: body
  });
}

export function logout() {
  return fetch(`http://127.0.0.1:8000/users/logout/`, {
    method: "delete",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include"
  });
}

export function register(data) {
  const body = JSON.stringify(data);
  return fetch("http://127.0.0.1:8000/users/register/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include",
    body: body
  });
}

export function profile() {
  return fetch("http://127.0.0.1:8000/users/profile-info/", {
    method: "get",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include",
  });
}

export function updateProfile(data) {
  const body = JSON.stringify(data);
  return fetch("http://127.0.0.1:8000/users/profile-update/", {
    method: "put",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include",
    body: body
  });
}

export function unsubscribe(data) {
  const body = JSON.stringify(data);
  return fetch(`http://127.0.0.1:8000/users/delete/`, {
    method: "put",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include",
    body: body
  });
}

export function filmDetails(filmId) {
  return fetch(`http://127.0.0.1:8000/films/${filmId}/`, {
    method: "get",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include"
  });
}

export function filmReviews(filmId) {
  return fetch(`http://127.0.0.1:8000/films/${filmId}/reviews/`, {
    method: "get",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include"
  });
}

export function userReviews() {
  return fetch("http://127.0.0.1:8000/users/history/", {
    method: "get",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include"
  });
}

export function updateReviewData(data) {
  const body = JSON.stringify(data);
  return fetch("http://127.0.0.1:8000/users/add-review/", {
    method: "post",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include",
    body: body
  });
}

export function deleteReviewData(data) {
  const body = JSON.stringify(data);
  return fetch("http://127.0.0.1:8000/users/delete-review/", {
    method: "put",
    headers: {
      "Content-Type": "application/json"
    },
    credentials: "include",
    body: body
  });
}
