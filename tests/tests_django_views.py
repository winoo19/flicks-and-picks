from django.test import TestCase, Client
from django.urls import reverse
from ..django_backend.apps.users.models import (
    User,
    Film,
    Director,
    Actor,
    Score,
    Review,
)


class TestRegisterViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.register_url = reverse("user_register")

    def test_register_view_correct_POST(self):
        response = self.client.post(self.register_url, self.data)

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=f"Response is {response.status_code}, expected 201",
        )

        # Check if the user is created
        self.assertEqual(User.objects.count(), 1, msg="User was not created")

        # Check if the user is created with the correct data
        user = User.objects.first()
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

    def test_register_view_POST_no_data(self):
        response = self.client.post(self.register_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check if the user is not created
        self.assertEqual(User.objects.count(), 0, msg="User was created")

    def test_register_view_POST_existing_user(self):
        self.client.post(self.register_url, self.data)
        response = self.client.post(self.register_url, self.data)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check if the user is not created
        self.assertEqual(User.objects.count(), 1, msg="User was created")


class TestLoginViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.login_url = reverse("user_login")

        self.client.post(reverse("user_register"), self.data)

    def test_login_view_correct_POST(self):
        response = self.client.post(self.login_url, self.data)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check cookie is set
        self.assertTrue("session" in response.cookies, msg="Cookie should be set")

    def test_login_view_POST_no_data(self):
        response = self.client.post(self.login_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check cookie is not set
        self.assertFalse("session" in response.cookies, msg="Cookie should not be set")

    def test_login_view_POST_wrong_data(self):
        response = self.client.post(
            self.login_url, {"username": "wrong", "password": "wrong"}
        )

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=f"Response is {response.status_code}, expected 401",
        )

        # Check cookie is not set
        self.assertFalse("session" in response.cookies, msg="Cookie should not be set")

    def test_login_view_POST_relogin(self):
        self.client.post(self.login_url, self.data)
        response = self.client.post(self.login_url, self.data)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            401,
            msg=f"Response is {response.status_code}, expected 401",
        )

        # Check cookie is not set
        self.assertFalse("session" in response.cookies, msg="Cookie should not be set")


class TestProfileViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.profile_url = reverse("user_info")
        self.login_url = reverse("user_login")

        self.client.post(reverse("user_register"), self.data)

    def test_profile_view_correct_GET(self):
        self.client.post(self.login_url, self.data)

        response = self.client.get(self.profile_url)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the user is returned
        self.assertEqual(
            response.json()["username"],
            self.data["username"],
            msg=f"Username is {response.json()['username']}, expected {self.data['username']}",
        )
        self.assertEqual(
            response.json()["email"],
            self.data["email"],
            msg=f"Email is {response.json()['email']}, expected {self.data['email']}",
        )

    def test_profile_view_GET_no_cookie(self):
        response = self.client.get(self.profile_url)

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=f"Response is {response.status_code}, expected 401",
        )


class TestUpdateProfileViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.update_url = reverse("user_update")
        self.login_url = reverse("user_login")

        self.client.post(reverse("user_register"), self.data)

    def test_update_view_correct_PUT(self):
        self.client.post(self.login_url, self.data)

        new_data = {
            "username": "newuser",
            "email": "new@i.l",
            "password": self.data["password"],
        }

        response = self.client.put(self.update_url, new_data)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the user is updated
        user = User.objects.first()
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
        self.assertTrue(
            user.check_password(self.data["password"]),
            msg="Password should not be updated",
        )

    def test_update_view_partial_PUT(self):
        self.client.post(self.login_url, self.data)

        new_data = {
            "username": "newuser",
            "password": self.data["password"],
        }

        response = self.client.put(self.update_url, new_data)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the user is updated
        user = User.objects.first()
        self.assertEqual(
            user.username,
            new_data["username"],
            msg=f"Username is {user.username}, expected {new_data['username']}. It should be updated.",
        )
        self.assertEqual(
            user.email,
            self.data["email"],
            msg=f"Email is {user.email}, expected {self.data['email']}. It should not be updated.",
        )
        self.assertTrue(
            user.check_password(self.data["password"]),
            msg="Password should not be updated",
        )

    def test_update_view_PUT_no_cookie(self):
        new_data = {
            "username": "newuser",
            "email": "new@i.l",
            "password": self.data["password"],
        }

        response = self.client.put(self.update_url, new_data)

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=f"Response is {response.status_code}, expected 401",
        )

    def test_update_view_PUT_no_data(self):
        self.client.post(self.login_url, self.data)

        response = self.client.put(self.update_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

    def test_update_view_PUT_wrong_password(self):
        self.client.post(self.login_url, self.data)

        new_data = {
            "username": "newuser",
            "email": "new@i.l",
            "password": "wrongpassword",
        }

        response = self.client.put(self.update_url, new_data)

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=f"Response is {response.status_code}, expected 401",
        )

        # Check if the user is not updated
        user = User.objects.first()
        self.assertEqual(
            user.username,
            self.data["username"],
            msg=f"Username is {user.username}, expected {self.data['username']}. It should not be updated.",
        )
        self.assertEqual(
            user.email,
            self.data["email"],
            msg=f"Email is {user.email}, expected {self.data['email']}. It should not be updated.",
        )
        self.assertTrue(
            user.check_password(self.data["password"]),
            msg="Password should not be updated",
        )


class TestLogoutViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.logout_url = reverse("user_logout")
        self.login_url = reverse("user_login")

        self.client.post(reverse("user_register"), self.data)

    def test_logout_view_correct_POST(self):
        self.client.post(self.login_url, self.data)

        response = self.client.post(self.logout_url)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the cookie is deleted
        self.assertFalse("session" in response.cookies, msg="Cookie should be deleted")

    def test_logout_view_POST_no_cookie(self):
        response = self.client.post(self.logout_url)

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=f"Response is {response.status_code}, expected 401",
        )

        # Check if the cookie is not deleted
        self.assertFalse(
            "session" in response.cookies, msg="Cookie should not be deleted"
        )


class TestDeleteProfileViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.delete_url = reverse("user_delete")
        self.login_url = reverse("user_login")
        self.register_url = reverse("user_register")

        self.client.post(self.register_url, self.data)

    def test_delete_view_correct_DELETE(self):
        self.client.post(self.login_url, self.data)

        response = self.client.delete(self.delete_url)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the cookie is deleted
        self.assertFalse("session" in response.cookies, msg="Cookie should be deleted")

        # Check if the user is deleted
        self.assertEqual(User.objects.count(), 0, msg="User was not deleted")

    def test_delete_view_DELETE_no_cookie(self):
        response = self.client.delete(self.delete_url)

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check if the user is not deleted
        self.assertEqual(User.objects.count(), 1, msg="User was deleted")


class TestCreateDirectorViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.director_data = {
            "name": "testdirector",
            "nationality": "testnationality",
        }

        self.create_director_url = reverse("add_dir")

    def test_create_director_view_correct_POST(self):
        response = self.client.post(self.create_director_url, self.director_data)

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=f"Response is {response.status_code}, expected 201",
        )

        # Check if the director is created
        self.assertEqual(Director.objects.count(), 1, msg="Director was not created")

        # Check if the director is created with the correct data
        director = Director.objects.first()
        self.assertEqual(
            director.name,
            self.director_data["name"],
            msg=f"Director name is {director.name}, expected {self.director_data['name']}",
        )
        self.assertEqual(
            director.nationality,
            self.director_data["nationality"],
            msg=f"Director nationality is {director.nationality}, expected {self.director_data['nationality']}",
        )

    def test_create_director_view_POST_no_data(self):
        response = self.client.post(self.create_director_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check if the director is not created
        self.assertEqual(Director.objects.count(), 0, msg="Director was created")

    def test_create_director_view_POST_existing_director(self):
        self.client.post(self.create_director_url, self.director_data)
        response = self.client.post(self.create_director_url, self.director_data)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check if the director is not created
        self.assertEqual(Director.objects.count(), 1, msg="Director was created")


class TestCreateActorViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.actor_data = {
            "name": "testactor",
            "nationality": "testnationality",
        }

        self.create_actor_url = reverse("add_actor")

    def test_create_actor_view_correct_POST(self):
        response = self.client.post(self.create_actor_url, self.actor_data)

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=f"Response is {response.status_code}, expected 201",
        )

        # Check if the actor is created
        self.assertEqual(Actor.objects.count(), 1, msg="Actor was not created")

        # Check if the actor is created with the correct data
        actor = Actor.objects.first()
        self.assertEqual(
            actor.name,
            self.actor_data["name"],
            msg=f"Actor name is {actor.name}, expected {self.actor_data['name']}",
        )
        self.assertEqual(
            actor.nationality,
            self.actor_data["nationality"],
            msg=f"Actor nationality is {actor.nationality}, expected {self.actor_data['nationality']}",
        )

    def test_create_actor_view_POST_no_data(self):
        response = self.client.post(self.create_actor_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check if the actor is not created
        self.assertEqual(Actor.objects.count(), 0, msg="Actor was created")

    def test_create_actor_view_POST_existing_actor(self):
        self.client.post(self.create_actor_url, self.actor_data)
        response = self.client.post(self.create_actor_url, self.actor_data)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check if the actor is not created
        self.assertEqual(Actor.objects.count(), 1, msg="Actor was created")


class TestCreateFilmViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.director_data = "testdirector"
        self.actors_data = [
            "testactor1",
            "testactor2",
            "testactor3",
        ]
        self.film_data = {
            "title": "testfilm",
            "release": "2021-01-01",
            "genre": "Action",
            "description": "testdescription",
            "duration": 120,
            "director": self.director_data,
            "cast": self.actors_data,
        }

        self.create_film_url = reverse("add_film")

    def test_create_film_view_correct_POST(self):
        response = self.client.post(self.create_film_url, self.film_data)

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=f"Response is {response.status_code}, expected 201",
        )

        # Check if the film is created
        self.assertEqual(Film.objects.count(), 1, msg="Film was not created")

        # Check if the film is created with the correct data
        film = Film.objects.first()
        self.assertEqual(
            film.title,
            self.film_data["title"],
            msg=f"Film title is {film.title}, expected {self.film_data['title']}",
        )
        self.assertEqual(
            film.release,
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
            msg=f"Film description is {film.description}, expected {self.film_data['description']}",
        )
        self.assertEqual(
            film.duration,
            self.film_data["duration"],
            msg=f"Film duration is {film.duration}, expected {self.film_data['duration']}",
        )
        self.assertEqual(
            film.director.name,
            self.director_data,
            msg=f"Film director is {film.director.name}, expected {self.director_data}",
        )
        self.assertEqual(
            film.cast.count(),
            len(self.actors_data),
            msg=f"Film cast is {film.cast.count()}, expected {len(self.actors_data)}",
        )

    def test_create_film_view_POST_incorrect_actors(self):
        incorrect_actors_data = ["1 2 &%$", 1, ""]
        response = self.client.post(self.create_film_url, self.film_data)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check if the film is not created
        self.assertEqual(Film.objects.count(), 0, msg="Film was created")


class TestCreateReviewViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.film_data = {
            "title": "testfilm",
            "release": "2021-01-01",
            "genre": "Action",
            "description": "testdescription",
            "duration": 120,
            "director": "testdirector",
            "cast": ["testactor1", "testactor2", "testactor3"],
        }
        self.review_data = {
            "score": 5,
            "comment": "testcomment",
        }

        self.create_review_url = reverse("user_add_review", kwargs={"pk": 1})
        self.login_url = reverse("user_login")

        self.client.post(reverse("user_register"), self.user_data)
        self.client.post(reverse("add_film"), self.film_data)

    def test_create_review_view_correct_POST(self):
        self.client.post(self.login_url, self.user_data)

        response = self.client.post(self.create_review_url, self.review_data)

        # Check if the response is 201
        self.assertEqual(
            response.status_code,
            201,
            msg=f"Response is {response.status_code}, expected 201",
        )

        # Check if the review is created
        self.assertEqual(Review.objects.count(), 1, msg="Review was not created")

        # Check if the review is created with the correct data
        review = Review.objects.first()
        self.assertEqual(
            review.film.id,
            1,
            msg=f"Review film is {review.film.id}, expected {self.review_data['film_id']}",
        )
        self.assertEqual(
            review.value,
            self.review_data["score"],
            msg=f"Review score is {review.value}, expected {self.review_data['score']}",
        )
        self.assertEqual(
            review.content,
            self.review_data["comment"],
            msg=f"Review comment is {review.content}, expected {self.review_data['comment']}",
        )

    def test_create_review_view_POST_no_cookie(self):
        response = self.client.post(self.create_review_url, self.review_data)

        # Check if the response is 401
        self.assertEqual(
            response.status_code,
            401,
            msg=f"Response is {response.status_code}, expected 401",
        )

        # Check if the review is not created
        self.assertEqual(Review.objects.count(), 0, msg="Review was created")

    def test_create_review_view_POST_no_data(self):
        self.client.post(self.login_url, self.user_data)

        response = self.client.post(self.create_review_url)

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )

        # Check if the review is not created
        self.assertEqual(Review.objects.count(), 0, msg="Review was created")

    def test_create_review_view_POST_wrong_film(self):
        self.client.post(self.login_url, self.user_data)

        response = self.client.post(
            reverse("user_add_review", kwargs={"pk": 99999}), self.review_data
        )

        # Check if the response is 404
        self.assertEqual(
            response.status_code,
            404,
            msg=f"Response is {response.status_code}, expected 404",
        )

        # Check if the review is not created
        self.assertEqual(Review.objects.count(), 0, msg="Review was created")


class TestListFilmViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.film_data = [
            {
                "title": "Avengers",
                "release": "2012-05-04",
                "genre": "Action",
                "description": "testdescription",
                "duration": 120,
                "director": "Anthony Russo",
                "cast": ["Mark Ruffalo", "Chris Evans", "Robert Downey Jr."],
            },
            {
                "title": "Avengers Endgame",
                "release": "2019-04-26",
                "genre": "Action",
                "description": "testdescription",
                "duration": 120,
                "director": "Anthony Russo",
                "cast": ["Mark Ruffalo", "Chris Evans", "Robert Downey Jr."],
            },
            {
                "title": "When Harry Met Sally",
                "release": "1989-07-21",
                "genre": "Romance",
                "description": "testdescription",
                "duration": 120,
                "director": "Rob Reiner",
                "cast": ["Billy Crystal", "Meg Ryan"],
            },
        ]

        self.login_url = reverse("user_login")
        self.list_url = reverse("film_filter")

        self.client.post(reverse("user_register"), self.user_data)

    def test_list_film_view_correct_GET(self):
        self.client.post(self.login_url, self.user_data)

        response = self.client.get(self.list_url)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the films are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )

    def test_list_film_view_GET_with_parameters(self):
        params = {
            "title": "Avengers",
            "genre": "Action",
            "min_release": "2010",
            "max_release": "2020",
            "min_score": "7",
            "max_score": "10",
        }

        self.client.post(self.login_url, self.user_data)
        for film in self.film_data:
            self.client.post(reverse("add_film"), film)

        response = self.client.get(self.list_url, params)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the films are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )

    def test_list_film_view_GET_no_results(self):
        params = {
            "min_score": "10",
            "title": "asdasd",
        }

        self.client.post(self.login_url, self.user_data)
        for film in self.film_data:
            self.client.post(reverse("add_film"), film)

        response = self.client.get(self.list_url, params)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the films are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )
        self.assertEqual(
            len(response.json()["results"]), 0, msg="Results should be empty"
        )

    def test_list_film_view_GET_title(self):
        params = {
            "title": "Avengers",
        }

        self.client.post(self.login_url, self.user_data)
        for film in self.film_data:
            self.client.post(reverse("add_film"), film)

        response = self.client.get(self.list_url, params)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the films are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )
        self.assertTrue(
            all(
                (
                    film["title"].lower().find("avengers") != -1
                    for film in response.json()["results"]
                )
            ),
            msg="Results should contain Avengers",
        )

    def test_list_film_view_GET_genre(self):
        params = {
            "genre": "Action",
        }

        self.client.post(self.login_url, self.user_data)
        for film in self.film_data:
            self.client.post(reverse("add_film"), film)

        response = self.client.get(self.list_url, params)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the films are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )
        self.assertTrue(
            all(
                (
                    film["genre"].lower().find("action") != -1
                    for film in response.json()["results"]
                )
            ),
            msg="Results should contain Action",
        )

    def test_list_film_view_GET_min_release(self):
        params = {
            "min_release": "2010",
        }

        self.client.post(self.login_url, self.user_data)
        for film in self.film_data:
            self.client.post(reverse("add_film"), film)

        response = self.client.get(self.list_url, params)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the films are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )
        self.assertTrue(
            all(
                (film["release"] >= 2010 for film in response.json()["results"]),
                msg="Results should contain films released after 2010",
            )
        )

    def test_list_film_view_GET_max_release(self):
        params = {
            "max_release": "2015",
        }

        self.client.post(self.login_url, self.user_data)
        for film in self.film_data:
            self.client.post(reverse("add_film"), film)

        response = self.client.get(self.list_url, params)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the films are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )
        self.assertTrue(
            all(
                (film["release"] <= 2020 for film in response.json()["results"]),
                msg="Results should contain films released before 2020",
            )
        )

    def test_list_film_view_GET_min_score(self):
        params = {
            "min_score": "7",
        }

        review_data = [
            {
                "score": 5,
                "comment": "testcomment1",
            },
            {
                "score": 7,
                "comment": "testcomment2",
            },
            {
                "score": 9,
                "comment": "testcomment3",
            },
        ]

        self.client.post(self.login_url, self.user_data)
        for film in self.film_data:
            self.client.post(reverse("add_film"), film)
        for review in review_data:
            self.client.post(reverse("user_add_review", kwargs={"pk": 1}), review)

        response = self.client.get(self.list_url, params)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the films are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )
        self.assertTrue(
            all(
                (film["score"] >= 7 for film in response.json()["results"]),
                msg="Results should contain films with score greater than 7",
            )
        )

    def test_list_film_view_GET_max_score(self):
        params = {
            "max_score": "8",
        }

        review_data = [
            {
                "score": 5,
                "comment": "testcomment1",
            },
            {
                "score": 7,
                "comment": "testcomment2",
            },
            {
                "score": 9,
                "comment": "testcomment3",
            },
        ]

        self.client.post(self.login_url, self.user_data)
        for film in self.film_data:
            self.client.post(reverse("add_film"), film)
        for review in review_data:
            self.client.post(reverse("user_add_review", kwargs={"pk": 1}), review)

        response = self.client.get(self.list_url, params)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the films are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )
        self.assertTrue(
            all(
                (film["score"] <= 8 for film in response.json()["results"]),
                msg="Results should contain films with score less than 8",
            )
        )


class TestDetailFilmViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.detail_url = reverse("film_info", kwargs={"pk": 1})

        self.user_data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.film_data = {
            "title": "testfilm",
            "release": "2021-01-01",
            "genre": "Action",
            "description": "testdescription",
            "duration": 120,
            "director": "testdirector",
            "cast": ["testactor1", "testactor2", "testactor3"],
        }

        self.login_url = reverse("user_login")

        self.client.post(reverse("user_register"), self.user_data)

    def test_detail_film_view_correct_GET(self):
        self.client.post(self.login_url, self.user_data)
        self.client.post(reverse("add_film"), self.film_data)

        response = self.client.get(self.detail_url)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the film is returned
        self.assertTrue("name" in response.json(), msg="Title should be present")
        self.assertTrue("release" in response.json(), msg="Release should be present")
        self.assertTrue("genre" in response.json(), msg="Genre should be present")
        self.assertTrue(
            "description" in response.json(), msg="Description should be present"
        )
        self.assertTrue("duration" in response.json(), msg="Duration should be present")

    def test_detail_film_view_GET_no_result(self):
        self.client.post(self.login_url, self.user_data)

        response = self.client.get(reverse("film_info", args=[99999]))

        # Check if the response is 404
        self.assertEqual(
            response.status_code,
            404,
            msg=f"Response is {response.status_code}, expected 404",
        )


class TestGetFilmReviewsViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.get_reviews_url = reverse(
            "film_reviews", kwargs={"film_id": 1, "user_id": 1}
        )
        self.login_url = reverse("user_login")

        self.user_data = {
            "username": "testuser",
            "email": "em@i.l",
            "password": "testpassword",
        }
        self.film_data = {
            "title": "testfilm",
            "release": "2021-01-01",
            "genre": "Action",
            "description": "testdescription",
            "duration": 120,
            "director": "testdirector",
            "cast": ["testactor1", "testactor2", "testactor3"],
        }
        self.review_data = {
            "score": 5,
            "comment": "testcomment",
        }

        self.client.post(reverse("user_register"), self.user_data)

    def test_get_reviews_view_correct_GET(self):
        self.client.post(self.login_url, self.user_data)
        self.client.post(reverse("add_film"), self.film_data)
        self.client.post(reverse("user_add_review", kwargs={"pk": 1}), self.review_data)

        response = self.client.get(self.get_reviews_url)

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the reviews are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )

    def test_get_reviews_view_GET_no_results(self):
        response = self.client.get(
            self.get_reviews_url, {"user_id": 1, "film_id": 99999}
        )

        # Check if the response is 200
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Response is {response.status_code}, expected 200",
        )

        # Check if the reviews are returned
        self.assertTrue("results" in response.json(), msg="Results should be present")
        self.assertIsInstance(
            response.json()["results"], list, msg="Results should be a list"
        )
        self.assertEqual(
            len(response.json()["results"]), 0, msg="Results should be empty"
        )

    def test_get_reviews_view_GET_wrong_parameters(self):
        response = self.client.get(
            self.get_reviews_url, {"user_id": "wrong", "film_id": "wrong"}
        )

        # Check if the response is 400
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Response is {response.status_code}, expected 400",
        )
