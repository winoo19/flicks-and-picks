import json
from datetime import datetime
from apps.users.models import User, Film, Director, Actor, Review
from django.http.response import HttpResponse
from django.test import TestCase, Client

# from rest_framework.test import APIClient as Client
from django.urls import reverse
from apps.users.models import (
    User,
    Film,
    Director,
    Actor,
    Review,
)


class TestRegisterViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data: dict[str, str] = {
            "username": "testuser",
            # "email": "test@test.com",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.register_url: str = reverse("user_register")

    def test_register_view_correct_POST(self) -> None:
        response: HttpResponse = self.client.post(
            self.register_url, json.dumps(self.data), content_type="application/json"
        )

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=(
                f"Response is {response.status_code}, ",
                f"expected 201. Response content: {response.content}",
            ),
        )

        # Check if the user is created
        self.assertEqual(
            User.objects.count(),
            1,
            msg=f"There are {User.objects.count()} users and there should be 1.",
        )

        # Check if the user is created with the correct data
        user: User | None = User.objects.first()
        self.assertEqual(
            user.username,
            self.data["username"],
            msg=f"User is {user.username}, expected {self.data['username']}",
        )
        self.assertEqual(
            user.email,
            self.data["email"],
            msg=f"Email is {user.email}, expected {self.data['email']}",
        )
        self.assertTrue(
            user.check_password(self.data["password"]),
            msg="Password is not saved correctly",
        )

    def test_register_view_POST_no_data(self) -> None:
        response: HttpResponse = self.client.post(self.register_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, expected 400. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the user is not created
        self.assertEqual(
            User.objects.count(),
            0,
            msg=f"There are {User.objects.count()} users and there should be 0.",
        )

    def test_register_view_POST_existing_user(self) -> None:
        self.client.post(
            self.register_url, json.dumps(self.data), content_type="application/json"
        )
        response: HttpResponse = self.client.post(
            self.register_url, json.dumps(self.data), content_type="application/json"
        )

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, expected 400. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the user is not created
        self.assertEqual(
            User.objects.count(),
            1,
            msg=f"There are {User.objects.count()} users and there should be 1.",
        )


class TestLoginViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data: dict[str, str] = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.login_url: str = reverse("user_login")
        self.client.post(
            reverse("user_register"),
            json.dumps(self.data),
            content_type="application/json",
        )
        self.data.pop("email")

    def test_login_view_correct_POST(self) -> None:
        response: HttpResponse = self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check cookie is set
        self.assertTrue("session" in response.cookies, msg="Cookie should be set")

    def test_login_view_POST_no_data(self) -> None:
        response: HttpResponse = self.client.post(self.login_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            401,
            msg=(
                f"Response is {response.status_code}, expected 400. ",
                f"Response content: {response.content}",
            ),
        )

        # Check cookie is not set
        self.assertFalse("session" in response.cookies, msg="Cookie should not be set")

    def test_login_view_POST_wrong_data(self) -> None:
        data: dict[str, str] = {"username": "wrong", "password": "wrong"}
        response: HttpResponse = self.client.post(
            self.login_url,
            json.dumps(data),
            content_type="application/json",
        )

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=(
                f"Response is {response.status_code}, expected 401. "
                f"Response content: {response.content}"
            ),
        )

        # Check cookie is not set
        self.assertFalse("session" in response.cookies, msg="Cookie should not be set")

    def test_login_view_POST_relogin(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )
        response: HttpResponse = self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            401,
            msg=(
                f"Response is {response.status_code}, expected 401. "
                f"Response content: {response.content}"
            ),
        )

        # Check cookie is not set
        self.assertFalse("session" in response.cookies, msg="Cookie should not be set")


class TestProfileViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data: dict[str, str] = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.profile_url: str = reverse("user_info")
        self.login_url: str = reverse("user_login")

        self.client.post(
            reverse("user_register"),
            json.dumps(self.data),
            content_type="application/json",
        )

    def test_profile_view_correct_GET(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        response: HttpResponse = self.client.get(
            path=self.profile_url, HTTP_AUTHORIZATION=f"Token {token_key}"
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the user is returned
        self.assertEqual(
            response.json()["username"],
            self.data["username"],
            msg=(
                f"Username is {response.json()['username']}, "
                f"expected {self.data['username']}"
            ),
        )
        self.assertEqual(
            response.json()["email"],
            self.data["email"],
            msg=f"Email is {response.json()['email']}, expected {self.data['email']}",
        )

    def test_profile_view_GET_no_cookie(self) -> None:
        response: HttpResponse = self.client.get(self.profile_url)

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=(
                f"Response is {response.status_code}, expected 401. "
                f"Response content: {response.content}"
            ),
        )


class TestUpdateProfileViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data: dict[str, str] = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.update_url: str = reverse("user_update")
        self.login_url: str = reverse("user_login")

        self.client.post(
            reverse("user_register"),
            json.dumps(self.data),
            content_type="application/json",
        )

    def test_update_view_correct_PUT(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        new_data: dict[str, str] = {
            "current_password": self.data["password"],
            "username": "newuser",
            "email": "newtest@test.com",
            "new_password": self.data["password"] + "extra",
        }

        response: HttpResponse = self.client.put(
            path=self.update_url,
            data=json.dumps(new_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the user is updated
        user: User | None = User.objects.first()
        self.assertEqual(
            user.username,
            new_data["username"],
            msg=f"Username is {user.username}, expected {new_data['username']}",
        )
        self.assertEqual(
            user.email,
            new_data["email"],
            msg=f"Email is {user.email}, expected {new_data['email']}",
        )

    def test_update_view_partial_PUT(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        new_data: dict[str, str] = {
            "current_password": self.data["password"],
            "username": "newuser",
            "email": "newtest@test.com",
        }

        response: HttpResponse = self.client.put(
            path=self.update_url,
            data=json.dumps(new_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the user is updated
        user: User | None = User.objects.first()
        self.assertEqual(
            user.username,
            new_data["username"],
            msg=(
                f"Username is {user.username}, expected {new_data['username']}. ",
                "It should be updated.",
            ),
        )
        self.assertEqual(
            user.email,
            new_data["email"],
            msg=(
                f"Email is {user.email}, expected {new_data['email']}. ",
                "It should not be updated.",
            ),
        )
        self.assertTrue(
            user.check_password(self.data["password"]),
            msg="Password should not be updated",
        )

    def test_update_view_PUT_no_cookie(self) -> None:
        new_data: dict[str, str] = {
            "current_password": self.data["password"],
            "username": "newuser",
            "email": "newtest@test.com",
            "new_password": self.data["password"] + "extra",
        }

        response: HttpResponse = self.client.put(
            path=self.update_url,
            data=json.dumps(new_data),
            content_type="application/json",
        )

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=(
                f"Response is {response.status_code}, expected 401. ",
                f"Response content: {response.content}",
            ),
        )

    def test_update_view_PUT_no_data(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        response: HttpResponse = self.client.put(
            path=self.update_url,
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, expected 400. ",
                f"Response content: {response.content}",
            ),
        )

    def test_update_view_PUT_wrong_password(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        new_data: dict[str, str] = {
            "current_password": "wrong_password",
            "username": "newuser",
            "email": "newtest@test.com",
            "new_password": self.data["password"] + "extra",
        }

        response: HttpResponse = self.client.put(
            path=self.update_url,
            data=json.dumps(new_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, expected 400. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the user is not updated
        user: User | None = User.objects.first()
        self.assertEqual(
            user.username,
            self.data["username"],
            msg=(
                f"Username is {user.username}, expected {self.data['username']}. "
                f"It should not be updated."
            ),
        )
        self.assertEqual(
            user.email,
            self.data["email"],
            msg=(
                f"Email is {user.email}, expected {self.data['email']}. "
                f"It should not be updated.",
            ),
        )
        self.assertTrue(
            user.check_password(self.data["password"]),
            msg="Password should not be updated",
        )


class TestLogoutViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data: dict[str, str] = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.logout_url: str = reverse("user_logout")
        self.login_url: str = reverse("user_login")

        self.client.post(
            reverse("user_register"),
            json.dumps(self.data),
            content_type="application/json",
        )
        self.data.pop("email")

    def test_logout_view_correct_DELETE(self) -> None:

        # Log in first
        response: HttpResponse = self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        # Send the DELETE request
        response = self.client.delete(
            path=self.logout_url, HTTP_AUTHORIZATION=f"Token {token_key}"
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the cookie is deleted
        self.assertTrue(
            self.client.cookies["session"].value in [None, ""],
            msg="Cookie should be deleted",
        )

    def test_logout_view_DELETE_no_cookie(self) -> None:
        response: HttpResponse = self.client.delete(self.logout_url)

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=(
                f"Response is {response.status_code}, expected 401. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the cookie is not deleted
        self.assertFalse(
            "session" in response.cookies, msg="Cookie should not be deleted"
        )


class TestDeleteProfileViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data: dict[str, str] = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.delete_url: str = reverse("user_delete")
        self.login_url: str = reverse("user_login")
        self.register_url: str = reverse("user_register")

        self.client.post(
            self.register_url,
            json.dumps(self.data),
            content_type="application/json",
        )

    def test_delete_view_correct_DELETE(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        # Send the DELETE request
        response: HttpResponse = self.client.put(
            path=self.delete_url,
            data={"password": self.data.get("password")},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the cookie is deleted
        self.assertTrue(
            self.client.cookies["session"].value in [None, ""],
            msg="Cookie should be deleted",
        )

        # Check if the user is deleted
        self.assertEqual(
            User.objects.count(),
            0,
            msg=f"There are {User.objects.count()} users and there should be 0.",
        )

    def test_delete_view_DELETE_no_cookie(self) -> None:
        response: HttpResponse = self.client.delete(self.delete_url)

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=(
                f"Response is {response.status_code}, expected 401. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the user is not deleted
        self.assertEqual(
            User.objects.count(),
            1,
            msg=f"There are {User.objects.count()} users and there should be 1.",
        )


class TestCreateDirectorViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.director_data: dict[str, str] = {
            "name": "Test Director",
            "nationality": "testnationality",
        }

        self.create_director_url: str = reverse("add_dir")

    def test_create_director_view_correct_POST(self) -> None:
        response: HttpResponse = self.client.post(
            self.create_director_url,
            json.dumps(self.director_data),
            content_type="application/json",
        )

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=(
                f"Response is {response.status_code}, expected 201. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the director is created
        self.assertEqual(
            Director.objects.count(),
            1,
            msg=f"There are {Director.objects.count()} directors. There should be 1.",
        )

        # Check if the director is created with the correct data
        director: Director | None = Director.objects.first()
        self.assertEqual(
            director.name,
            self.director_data["name"],
            msg=(
                f"Director name is {director.name}, "
                f"expected {self.director_data['name']}"
            ),
        )
        self.assertEqual(
            director.nationality,
            self.director_data["nationality"],
            msg=(
                f"Director nationality is {director.nationality}, ",
                f"expected {self.director_data['nationality']}",
            ),
        )

    def test_create_director_view_POST_no_data(self) -> None:
        response: HttpResponse = self.client.post(self.create_director_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, expected 400. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the director is not created
        self.assertEqual(
            Director.objects.count(),
            0,
            msg=f"There are {Director.objects.count()} directors. There should be 0.",
        )

    def test_create_director_view_POST_existing_director(self) -> None:
        self.client.post(
            self.create_director_url,
            json.dumps(self.director_data),
            content_type="application/json",
        )
        response: HttpResponse = self.client.post(
            self.create_director_url,
            json.dumps(self.director_data),
            content_type="application/json",
        )

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, ",
                f"expected 400. Response content: {response.content}",
            ),
        )

        # Check if the director is not created
        self.assertEqual(
            Director.objects.count(),
            1,
            msg=f"There are {Director.objects.count()} directors. There should be 1.",
        )


class TestCreateActorViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.actor_data: dict[str, str] = {
            "name": "Test Actor",
            "nationality": "testnationality",
        }

        self.create_actor_url: str = reverse("add_actor")

    def test_create_actor_view_correct_POST(self) -> None:
        response: HttpResponse = self.client.post(
            self.create_actor_url,
            json.dumps(self.actor_data),
            content_type="application/json",
        )

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=(
                f"Response is {response.status_code}, "
                f"expected 201. Response content: {response.content}"
            ),
        )

        # Check if the actor is created
        self.assertEqual(
            Actor.objects.count(),
            1,
            msg=f"There are {Actor.objects.count()} actors and there should be 1.",
        )

        # Check if the actor is created with the correct data
        actor: Actor | None = Actor.objects.first()
        self.assertEqual(
            actor.name,
            self.actor_data["name"],
            msg=f"Actor name is {actor.name}, expected {self.actor_data['name']}",
        )
        self.assertEqual(
            actor.nationality,
            self.actor_data["nationality"],
            msg=(
                f"Actor nationality is {actor.nationality}, ",
                f"expected {self.actor_data['nationality']}",
            ),
        )

    def test_create_actor_view_POST_no_data(self) -> None:
        response: HttpResponse = self.client.post(self.create_actor_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, ",
                f"expected 400. Response content: {response.content}",
            ),
        )

        # Check if the actor is not created
        self.assertEqual(
            Actor.objects.count(),
            0,
            msg=f"There are {Actor.objects.count()} actors and there should be 0.",
        )

    def test_create_actor_view_POST_existing_actor(self) -> None:
        self.client.post(
            self.create_actor_url,
            json.dumps(self.actor_data),
            content_type="application/json",
        )
        response: HttpResponse = self.client.post(
            self.create_actor_url,
            json.dumps(self.actor_data),
            content_type="application/json",
        )

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, ",
                f"expected 400. Response content: {response.content}",
            ),
        )

        # Check if the actor is not created
        self.assertEqual(
            Actor.objects.count(),
            1,
            msg=f"There are {Actor.objects.count()} actors and there should be 1.",
        )


class TestCreateFilmViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.director_data: str = "Test Director"
        self.actors_data: list[str] = [
            "Test Actor1",
            "Test Actor2",
            "Test Actor3",
        ]
        self.film_data: dict = {
            "name": "testfilm",
            "release": "2021-01-01",
            "genre": "Action",
            "description": "test film description",
            "duration": 120,
            "director": self.director_data,
            "cast": self.actors_data,
        }

        self.create_film_url: str = reverse("add_film")

    def test_create_film_view_correct_POST(self) -> None:
        response: HttpResponse = self.client.post(
            self.create_film_url,
            json.dumps(self.film_data),
            content_type="application/json",
        )

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=(
                f"Response is {response.status_code}, expected 201. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the film is created
        self.assertEqual(
            Film.objects.count(),
            1,
            msg=f"There are {Film.objects.count()} films and there should be 1.",
        )

        # Check if the film is created with the correct data
        film: Film | None = Film.objects.first()
        self.assertEqual(
            film.name,
            self.film_data["name"],
            msg=f"Film name is {film.name}, expected {self.film_data['name']}",
        )
        self.assertEqual(
            str(film.release),
            self.film_data["release"],
            msg=f"Film release is {film.release}, expected {self.film_data['release']}",
        )
        self.assertEqual(
            film.genre,
            self.film_data["genre"],
            msg=f"Film genre is {film.genre}, expected {self.film_data['genre']}",
        )
        self.assertEqual(
            film.description,
            self.film_data["description"],
            msg=(
                f"Film description is {film.description}, "
                f"expected {self.film_data['description']}"
            ),
        )
        self.assertEqual(
            film.duration,
            self.film_data["duration"],
            msg=(
                f"Film duration is {film.duration}, ",
                f"expected {self.film_data['duration']}",
            ),
        )
        self.assertEqual(
            film.director_id.name,
            self.director_data,
            msg=(
                f"Film director is {film.director_id.name}, "
                f"expected {self.director_data}"
            ),
        )
        self.assertEqual(
            film.cast.count(),
            len(self.actors_data),
            msg=f"Film cast is {film.cast.count()}, expected {len(self.actors_data)}",
        )

    def test_create_film_view_POST_incorrect_actors(self) -> None:
        incorrect_actors_data: list = ["1 2 &%$", 1, ""]
        response: HttpResponse = self.client.post(
            self.create_film_url,
            json.dumps({**self.film_data, "cast": incorrect_actors_data}),
            content_type="application/json",
        )

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, expected 400. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the film is not created
        self.assertEqual(
            Film.objects.count(),
            0,
            msg=f"There are {Film.objects.count()} films and there should be 0.",
        )


class TestCreateReviewViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.user_data: dict[str, str] = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.film_data: dict = {
            "name": "testfilm",
            "release": "2021-01-01",
            "genre": "Action",
            "description": "testdescription",
            "duration": 120,
            "director": "Test Director",
            "cast": ["Test Actor 1", "Test Actor 2", "Test Actor 3"],
        }
        self.client.post(
            reverse("add_film"),
            json.dumps(self.film_data.copy()),
            content_type="application/json",
        )
        self.film_id: int = Film.objects.all().first().id
        self.review_data: dict = {
            "rating": 5,
            "content": "testcomment",
            "film_id": self.film_id,
        }

        self.create_review_url: str = reverse("user_add_review")
        self.login_url: str = reverse("user_login")

        self.client.post(
            reverse("user_register"),
            json.dumps(self.user_data),
            content_type="application/json",
        )
        self.user_data.pop("email")

    def test_create_review_view_correct_POST(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        response: HttpResponse = self.client.post(
            path=self.create_review_url,
            data=json.dumps(self.review_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=(
                f"Response is {response.status_code}, expected 201. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the review is created
        self.assertEqual(
            Review.objects.count(),
            1,
            msg=f"There are {Review.objects.count()} reviews and there should be 1.",
        )

        # Check if the review is created with the correct data
        review: Review | None = Review.objects.first()
        self.assertEqual(
            review.film_id.id,
            self.film_id,
            msg=(
                f"Review film id is {review.film_id.id}, "
                f"expected {self.review_data['film_id']}"
            ),
        )
        self.assertEqual(
            review.rating,
            self.review_data["rating"],
            msg=(
                f"Review rating is {review.rating}, ",
                f"expected {self.review_data['rating']}",
            ),
        )
        self.assertEqual(
            review.content,
            self.review_data["content"],
            msg=(
                f"Review comment is {review.content}, ",
                f"expected {self.review_data['content']}",
            ),
        )

    def test_create_review_view_POST_no_cookie(self) -> None:
        response: HttpResponse = self.client.post(
            self.create_review_url,
            json.dumps(self.review_data),
            content_type="application/json",
        )

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=(
                f"Response is {response.status_code}, expected 401. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the review is not created
        self.assertEqual(
            Review.objects.count(),
            0,
            msg=f"There are {Review.objects.count()} reviews and there should be 0.",
        )

    def test_create_review_view_POST_no_data(self) -> None:
        self.client.post(self.login_url, self.user_data)

        response: HttpResponse = self.client.post(self.create_review_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, ",
                f"expected 400. Response content: {response.content}",
            ),
        )

        # Check if the review is not created
        self.assertEqual(
            Review.objects.count(),
            0,
            msg=f"There are {Review.objects.count()} reviews and there should be 0.",
        )

    def test_create_review_view_POST_wrong_film(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )

        response: HttpResponse = self.client.post(
            reverse("user_add_review"),
            json.dumps({**self.review_data, "film_id": 999999}),
            content_type="application/json",
        )

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=(
                f"Response is {response.status_code}, expected 404. ",
                f"Response content: {response.content}",
            ),
        )

        # Check if the review is not created
        self.assertEqual(
            Review.objects.count(),
            0,
            msg=f"There are {Review.objects.count()} reviews and there should be 0.",
        )


class TestListFilmViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.user_data: dict[str, str] = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.film_data: list[dict] = [
            {
                "name": "Avengers",
                "release": "2012-05-04",
                "genre": "Action",
                "description": "testdescription",
                "duration": 120,
                "director": "Anthony Russo",
                "cast": ["Mark Ruffalo", "Chris Evans", "Robert Downey Jr."],
            },
            {
                "name": "Avengers Endgame",
                "release": "2019-04-26",
                "genre": "Action",
                "description": "testdescription",
                "duration": 120,
                "director": "Anthony Russo",
                "cast": ["Mark Ruffalo", "Chris Evans", "Robert Downey Jr."],
            },
            {
                "name": "When Harry Met Sally",
                "release": "1989-07-21",
                "genre": "Romance",
                "description": "testdescription",
                "duration": 120,
                "director": "Rob Reiner",
                "cast": ["Billy Crystal", "Meg Ryan"],
            },
        ]

        self.login_url: str = reverse("user_login")
        self.list_url: str = reverse("film_filter")

        self.client.post(
            reverse("user_register"),
            json.dumps(self.user_data),
            content_type="application/json",
        )
        self.user_data.pop("email")

    def test_list_film_view_correct_POST(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )

        response: HttpResponse = self.client.post(self.list_url)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the films are returned
        data: dict = response.json()
        self.assertTrue("films" in data, msg="Films field must be present in response")
        self.assertIsInstance(data["films"], list, msg="Films field must be a list")

    def test_list_film_view_GET_with_parameters(self) -> None:
        params: dict[str, str] = {
            "film_name": "Avengers",
            "genre": "Action",
            "min_release": "2010",
            "max_release": "2020",
            "min_rating": "7",
            "max_rating": "10",
        }

        for film in self.film_data:
            self.client.post(
                path=reverse("add_film"),
                data=film.copy(),
                content_type="application/json",
            )

        film_id: int = Film.objects.get(name="Avengers").id
        review_data: dict = {
            "rating": 9,
            "comment": "Very nice film",
            "film_id": film_id,
        }

        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        token_key: str = self.client.cookies["session"].value

        self.client.post(
            path=reverse("user_add_review"),
            data=json.dumps(review_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        response: HttpResponse = self.client.post(
            self.list_url,
            json.dumps(params),
            content_type="application/json",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the films are returned
        data: dict = response.json()
        self.assertTrue("films" in data, msg="Films field must be present in response")
        self.assertIsInstance(data["films"], list, msg="Films field must be a list")
        self.assertTrue(len(data["films"]) > 0, msg="Film list must not be empty")

    def test_list_film_view_GET_no_results(self) -> None:
        params: dict[str, str] = {
            "min_rating": "10",
            "film_name": "xx",
        }

        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        for film in self.film_data:
            self.client.post(
                path=reverse("add_film"),
                data=json.dumps(film),
                content_type="application/json",
            )

        response: HttpResponse = self.client.post(
            self.list_url, data=json.dumps(params), content_type="application/json"
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the films are returned
        data: dict = response.json()
        self.assertTrue("films" in data, msg="Films field must be present in response")
        self.assertIsInstance(data["films"], list, msg="Films field must be a list")
        self.assertTrue(len(data["films"]) == 0, msg="Film list must be empty")

    def test_list_film_view_GET_title(self) -> None:
        params: dict[str, str] = {
            "film_name": "Avengers",
        }

        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )

        for film in self.film_data:
            self.client.post(
                path=reverse("add_film"),
                data=json.dumps(film),
                content_type="application/json",
            )

        response: HttpResponse = self.client.post(
            self.list_url,
            json.dumps(params),
            content_type="application/json",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the films are returned
        data: dict = response.json()
        self.assertTrue("films" in data, msg="Films field must be present in response")
        self.assertIsInstance(data["films"], list, msg="Films field must be a list")
        self.assertTrue(len(data["films"]) > 0, msg="Film list must not be empty")

        self.assertTrue(
            all(film["name"].lower().find("avengers") != -1 for film in data["films"]),
            msg="Results should contain Avengers",
        )

    def test_list_film_view_GET_genre(self) -> None:
        params: dict[str, str] = {
            "genre": "Action",
        }

        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        for film in self.film_data:
            self.client.post(
                path=reverse("add_film"),
                data=json.dumps(film),
                content_type="application/json",
            )

        response: HttpResponse = self.client.post(
            path=self.list_url,
            data=json.dumps(params),
            content_type="application/json",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the films are returned
        data: dict = response.json()
        self.assertTrue("films" in data, msg="Films field must be present in response")
        self.assertIsInstance(data["films"], list, msg="Films field must be a list")
        self.assertTrue(len(data["films"]) > 0, msg="Film list must not be empty")
        self.assertTrue(
            all([film["genre"].lower().find("action") != -1 for film in data["films"]]),
            msg="Results should contain Action",
        )

    def test_list_film_view_GET_min_release(self) -> None:
        params: dict[str, str] = {
            "min_release": "2010",
        }

        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        for film in self.film_data:
            self.client.post(
                path=reverse("add_film"),
                data=json.dumps(film),
                content_type="application/json",
            )

        response: HttpResponse = self.client.post(
            self.list_url,
            json.dumps(params),
            content_type="application/json",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the films are returned
        data: dict = response.json()
        self.assertTrue("films" in data, msg="Films field must be present in response")
        self.assertIsInstance(data["films"], list, msg="Films field must be a list")
        self.assertTrue(len(data["films"]) > 0, msg="Film list must not be empty")
        self.assertTrue(
            all(
                int(datetime.strptime(film["release"], "%Y-%m-%d").year) >= 2010
                for film in data["films"]
            ),
            msg="Results should contain films released after 2010",
        )

    def test_list_film_view_GET_max_release(self) -> None:
        params: dict[str, str] = {
            "max_release": "2015",
        }

        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )
        for film in self.film_data:
            self.client.post(
                path=reverse("add_film"),
                data=json.dumps(film),
                content_type="application/json",
            )

        response: HttpResponse = self.client.post(
            path=self.list_url,
            data=json.dumps(params),
            content_type="application/json",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the films are returned
        data: dict = response.json()
        self.assertTrue("films" in data, msg="Films field must be present in response")
        self.assertIsInstance(data["films"], list, msg="Films field must be a list")
        self.assertTrue(len(data["films"]) > 0, msg="Film list must not be empty")
        self.assertTrue(
            all(
                int(datetime.strptime(film["release"], "%Y-%m-%d").year) <= 2020
                for film in data["films"]
            ),
            msg="Results should contain films released before 2020",
        )

    def test_list_film_view_GET_min_rating(self) -> None:
        params: dict[str, str] = {
            "min_rating": "7",
        }

        review_data: list[dict] = [
            {
                "rating": 5,
                "comment": "testcomment1",
                "film_id": 1,
            },
            {
                "rating": 7,
                "comment": "testcomment2",
                "film_id": 2,
            },
            {
                "rating": 9,
                "comment": "testcomment3",
                "film_id": 3,
            },
        ]

        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        for film in self.film_data:
            self.client.post(
                path=reverse("add_film"),
                data=json.dumps(film),
                content_type="application/json",
            )
        for review in review_data:
            self.client.post(
                path=reverse("user_add_review"),
                data=json.dumps(review),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Token {token_key}",
            )

        response: HttpResponse = self.client.post(
            path=self.list_url,
            data=json.dumps(params),
            content_type="application/json",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the films are returned
        data: dict = response.json()
        self.assertTrue("films" in data, msg="Films field must be present in response")
        self.assertIsInstance(data["films"], list, msg="Films field must be a list")
        self.assertTrue(len(data["films"]) > 0, msg="Film list must not be empty")
        self.assertTrue(
            all(film["avg_rating"] >= 7 for film in data["films"]),
            msg="Results should contain films with score greater than 7",
        )

    def test_list_film_view_GET_max_rating(self) -> None:
        params: dict[str, str] = {
            "max_rating": "8",
        }

        review_data: list[dict] = [
            {
                "rating": 5,
                "comment": "testcomment1",
                "film_id": 1,
            },
            {
                "rating": 7,
                "comment": "testcomment2",
                "film_id": 2,
            },
            {
                "rating": 9,
                "comment": "testcomment3",
                "film_id": 3,
            },
        ]

        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        for film in self.film_data:
            self.client.post(
                path=reverse("add_film"),
                data=json.dumps(film),
                content_type="application/json",
            )

        for review in review_data:
            self.client.post(
                path=reverse("user_add_review"),
                data=json.dumps(review),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Token {token_key}",
            )

        response: HttpResponse = self.client.post(
            path=self.list_url,
            data=json.dumps(params),
            content_type="application/json",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the films are returned
        data: dict = response.json()
        self.assertTrue("films" in data, msg="Films field must be present in response")
        self.assertIsInstance(data["films"], list, msg="Films field must be a list")
        self.assertTrue(len(data["films"]) > 0, msg="Film list must not be empty")
        self.assertTrue(
            all(film["avg_rating"] <= 8 for film in data["films"]),
            msg="Results should contain films with score less than 8",
        )


class TestDetailFilmViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.film_data: dict = {
            "name": "testfilm",
            "release": "2021-01-01",
            "genre": "Action",
            "description": "testdescription",
            "duration": 120,
            "director": "Test Director",
            "cast": ["Test Actor 1", "Test Actor 2", "Test Actor 3"],
        }

    def test_detail_film_view_correct_GET(self) -> None:
        self.client.post(
            path=reverse("add_film"),
            data=json.dumps(self.film_data),
            content_type="application/json",
        )
        self.film_id: int = Film.objects.all().first().id
        response: HttpResponse = self.client.get(
            path=reverse("film_info", kwargs={"id": self.film_id})
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the film is returned
        data: dict = response.json()
        self.assertTrue("name" in data, msg="Title should be present")
        self.assertTrue("release" in data, msg="Release should be present")
        self.assertTrue("genre" in data, msg="Genre should be present")
        self.assertTrue("description" in data, msg="Description should be present")
        self.assertTrue("duration" in data, msg="Duration should be present")

    def test_detail_film_view_GET_wrong_id(self) -> None:
        response: HttpResponse = self.client.get(
            path=reverse("film_info", kwargs={"id": 999})
        )

        # Check if the response is 404
        self.assertEqual(
            response.status_code,
            404,
            msg=(
                f"Response is {response.status_code}, expected 404. "
                f"Response content: {response.content}"
            ),
        )


class TestGetFilmReviewsViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.login_url: str = reverse("user_login")

        self.user_data: dict[str, str] = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.film_data: dict = {
            "name": "testfilm",
            "release": "2021-01-01",
            "genre": "Action",
            "description": "testdescription",
            "duration": 120,
            "director": "Test Director",
            "cast": ["Test Actor 1", "Test Actor 2", "Test Actor 3"],
        }
        self.review_data: dict = {
            "rating": 5,
            "content": "testcomment",
            "film_id": 1,
        }

        self.client.post(
            reverse("add_film"),
            json.dumps(self.film_data),
            content_type="application/json",
        )
        self.film_id: int = Film.objects.first().id

        self.client.post(
            reverse("user_register"),
            json.dumps(self.user_data),
            content_type="application/json",
        )
        self.user_data.pop("email")

    def test_get_film_reviews_view_correct_GET(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        self.client.post(
            path=reverse("user_add_review"),
            data=json.dumps(self.review_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        response: HttpResponse = self.client.get(
            path=reverse("film_reviews", kwargs={"id": self.film_id})
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the reviews are returned
        data: dict = response.json()
        self.assertTrue("reviews" in data, msg="Reviews should be returned")
        self.assertIsInstance(data["reviews"], list, msg="Reviews should be a list")
        self.assertTrue(len(data) > 0, msg="Reviews should should not be empty")

    def test_get_film_reviews_view_GET_not_found(self) -> None:
        response: HttpResponse = self.client.get(
            path=reverse("film_reviews", kwargs={"id": 999})
        )

        # Check if the response is 404
        self.assertEqual(
            response.status_code,
            404,
            msg=(
                f"Response is {response.status_code}, expected 404. "
                f"Response content: {response.content}"
            ),
        )


class TestGetUserReviewsViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.login_url: str = reverse("user_login")

        self.user_data: dict[str, str] = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password1",
        }
        self.film_data: dict = {
            "name": "testfilm",
            "release": "2021-01-01",
            "genre": "Action",
            "description": "testdescription",
            "duration": 120,
            "director": "Test Director",
            "cast": ["Test Actor 1", "Test Actor 2", "Test Actor 3"],
        }
        self.review_data: dict = {
            "rating": 5,
            "content": "testcomment",
            "film_id": 1,
        }

        self.client.post(
            reverse("add_film"),
            json.dumps(self.film_data),
            content_type="application/json",
        )

        self.client.post(
            reverse("user_register"),
            json.dumps(self.user_data),
            content_type="application/json",
        )
        self.user_data.pop("email")

    def test_get_user_reviews_view_correct_GET(self) -> None:
        self.client.post(
            path=self.login_url,
            data=json.dumps(self.user_data),
            content_type="application/json",
        )

        token_key: str = self.client.cookies["session"].value

        self.client.post(
            path=reverse("user_add_review"),
            data=json.dumps(self.review_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        response: HttpResponse = self.client.get(
            path=reverse("user_history"),
            HTTP_AUTHORIZATION=f"Token {token_key}",
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"Response is {response.status_code}, expected 200. "
                f"Response content: {response.content}"
            ),
        )

        # Check if the reviews are returned
        data: dict = response.json()
        self.assertTrue("reviews" in data, msg="Reviews should be returned")
        self.assertIsInstance(data["reviews"], list, msg="Reviews should be a list")
        self.assertTrue(len(data) > 0, msg="Reviews should should not be empty")

    def test_get_user_reviews_view_GET_not_found(self) -> None:
        response: HttpResponse = self.client.get(path=reverse("user_history"))

        # Check if the response is 404
        self.assertEqual(
            response.status_code,
            401,
            msg=(
                f"Response is {response.status_code}, expected 401. "
                f"Response content: {response.content}"
            ),
        )
