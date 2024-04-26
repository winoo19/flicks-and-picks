export function login(email, password) {
  const body = JSON.stringify({email, password});
  return fetch("/users/login", {method: "post", body});
}
export function logout() {
  return fetch("/users/logout", {method: "delete"});
}
export function register(data) {
  const body = JSON.stringify(data);
  return fetch("/users/register", {method: "post", body});
}
export function profile(data) {
  if (!data) return fetch("/users/profile");
  const body = JSON.stringify(data);
  return fetch("/api/users/me", {method: "put", body});
}
export function unsubscribe() {
  return fetch("/api/users/me", {method: "delete"});
}

export function film_details(film_id) {
  return fetch(`/user/film/${film_id}`, {method: "get"})
}

export function film_review(film_id, user_id) {
  return fetch(`/user/film-reviews/${film_id}/${user_id}`, {method: "get"})
}