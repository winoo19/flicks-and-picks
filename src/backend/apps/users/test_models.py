import json
from django.test import TestCase
from apps.users.models import User, Director, Actor, Film
from apps.users.serializers import (
    UserSerializer,
    DirectorSerializer,
    ActorSerializer,
    FilmSerializer,
    ReviewSerializer,
)


class TestModels(TestCase):
    def test_user(self) -> None:
        user_tests: list[tuple[bool, dict, str]] = [
            (
                True,
                {
                    "username": "test_username1",
                    "email": "test1@test1.com",
                    "password": "Password1",
                },
                "Valid user data.",
            ),
            (
                False,
                {
                    "username": "test_username1",
                    "email": "test1@test1.com",
                    "password": "Password",
                },
                "Invalid password. Password must contain at least 1 number.",
            ),
            (
                False,
                {
                    "username": "test_username1",
                    "email": "test1@test1.com",
                    "password": "password1",
                },
                "Invalid password. Password must contain at least 1 upper case char.",
            ),
            (
                False,
                {
                    "username": "test_username1",
                    "email": "test1@test1.com",
                    "password": "PASSWORD1",
                },
                "Invalid password. Password must contain at least 1 upper case char.",
            ),
            (
                False,
                {
                    "username": "test_username1",
                    "email": "email",
                    "password": "Password1",
                },
                (
                    "Invalid email. Email must match regular expression: "
                    "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                ),
            ),
            (
                False,
                {
                    "username": "test_username111111111111",
                    "email": "test1@test1.com",
                    "password": "Password1",
                },
                "Invalid username. Username must be less than 15 characters.",
            ),
            (
                False,
                {
                    "username": "te",
                    "email": "test1@test1.com",
                    "password": "Password1",
                },
                "Invalid username. Username must be at least 4 characters.",
            ),
        ]

        for i, example in enumerate(user_tests):
            valid: bool
            data: dict
            message: str
            valid, data, message = example
            serializer: UserSerializer = UserSerializer(data=data)
            instance_valid: bool = serializer.is_valid()
            self.assertTrue(
                instance_valid is valid,
                f"Failed user test {i+1}. {message}.\nData:\n{json.dumps(data)}",
            )

        # Test password is hidden
        user: UserSerializer = UserSerializer(
            data={
                "username": "test_username",
                "email": "test1@test1.com",
                "password": "Password1",
            }
        )
        user.is_valid()
        self.assertNotIn("password", user.data)

    def test_director(self) -> None:
        director_tests: list[tuple[bool, dict, str]] = [
            (
                True,
                {
                    "name": "Director Name",
                    "nationality": "Spanish",
                },
                "Valid director data.",
            ),
            (
                True,
                {
                    "name": "Director Name",
                },
                "Valid director data without nationality.",
            ),
            (
                False,
                {
                    "name": "Director",
                    "nationality": "Spanish",
                },
                "Invalid director name. Name must be at least 2 words.",
            ),
            (
                False,
                {
                    "name": "a " + "a" * 64,
                    "nationality": "Spanish",
                },
                "Invalid director name. Name must be less than 64 characters.",
            ),
        ]

        for i, example in enumerate(director_tests):
            valid: bool
            data: dict
            message: str
            valid, data, message = example
            serializer: DirectorSerializer = DirectorSerializer(data=data)
            instance_valid: bool = serializer.is_valid()
            self.assertTrue(
                instance_valid is valid,
                f"Failed director test {i+1}. {message}.\nData:\n{json.dumps(data)}",
            )

    def test_actor(self) -> None:
        actor_tests: list[tuple[bool, dict, str]] = [
            (
                True,
                {
                    "name": "Actor Name",
                    "nationality": "Spanish",
                },
                "Valid actor data.",
            ),
            (
                True,
                {
                    "name": "Actor Name",
                },
                "Valid actor data without nationality.",
            ),
            (
                False,
                {
                    "name": "Actor",
                    "nationality": "Spanish",
                },
                "Invalid actor name. Name must be at least 2 words.",
            ),
        ]

        for i, example in enumerate(actor_tests):
            valid: bool
            data: dict
            message: str
            valid, data, message = example
            serializer: ActorSerializer = ActorSerializer(data=data)
            instance_valid: bool = serializer.is_valid()
            self.assertTrue(
                instance_valid is valid,
                f"Failed actor test {i+1}. {message}\nData:\n{json.dumps(data)}",
            )

    def test_film(self) -> None:
        valid_director: Director = Director.objects.create(
            name="Test Director", nationality="none"
        )
        valid_director.save()
        valid_actor_1: Actor = Actor.objects.create(name="Test Actor 1")
        valid_actor_1.save()
        valid_actor_2: Actor = Actor.objects.create(name="Test Actor 2")
        valid_actor_2.save()
        film_tests: list[tuple[bool, dict, str]] = [
            (
                True,
                {
                    "name": "Film Name",
                    "release": "2021-01-01",
                    "genre": "Action",
                    "description": "Valid film description",
                    "duration": 120,
                    "director_id": valid_director.id,
                    "cast": [valid_actor_1.id, valid_actor_2.id],
                },
                "Valid film data.",
            ),
            (
                False,
                {
                    "name": "Film Name" * 30,
                    "release": "2021-01-01",
                    "genre": "Action",
                    "description": "Valid film description",
                    "duration": 120,
                    "director_id": valid_director.id,
                    "cast": [valid_actor_1.id, valid_actor_2.id],
                },
                "Invalid film name. Name must be less than 64 characters.",
            ),
            (
                False,
                {
                    "name": "Film Name" * 30,
                    "release": "2021-01-01a",
                    "genre": "Action",
                    "description": "Valid film description",
                    "duration": 120,
                    "director_id": valid_director.id,
                    "cast": [valid_actor_1.id, valid_actor_2.id],
                },
                (
                    "Invalid release date. Date must be one of the following formats: "
                    "%Y, %Y-%m, %Y-%m-%d, %m-%Y, %d-%m-%Y"
                ),
            ),
            (
                False,
                {
                    "name": "Film Name",
                    "release": "2021-01-01",
                    "genre": "Incorrect Genre",
                    "description": "Valid film description",
                    "duration": 120,
                    "director_id": valid_director.id,
                    "cast": [valid_actor_1.id, valid_actor_2.id],
                },
                (
                    "Invalid genre. Genre must be one of the following: "
                    "Action, Comedy, Crime, Documentary, Drama, Horror, "
                    "Romance, Sci-Fi, Thriller, Western"
                ),
            ),
            (
                False,
                {
                    "name": "Film Name",
                    "release": "2021-01-01",
                    "genre": "Action",
                    "description": "Valid film description" * 100,
                    "duration": 120,
                    "director_id": valid_director.id,
                    "cast": [valid_actor_1.id, valid_actor_2.id],
                },
                "Invalid description. Description must be less than 500 characters.",
            ),
            (
                True,
                {
                    "name": "Film Name",
                    "release": "2021-01-01",
                    "genre": "Action",
                    "description": "Valid film description",
                    "duration": 120,
                    "director_id": valid_director.id,
                    "cast": [valid_actor_1.id, valid_actor_2.id],
                    "image_url": "https://www.image.com",
                },
                "Valid film data with image url.",
            ),
            (
                False,
                {
                    "name": "Film Name",
                    "release": "2021-01-01",
                    "genre": "Action",
                    "description": "Valid film description",
                    "duration": 120,
                    "director_id": valid_director.id,
                    "cast": [valid_actor_1.id, valid_actor_2.id],
                    "image_url": "www.image.com",
                },
                "Invalid image url. Image url must start with https://.",
            ),
            (
                False,
                {
                    "name": "Film Name",
                    "release": "2021-01-01",
                    "genre": "Action",
                    "description": "Valid film description",
                    "duration": 120,
                    "director_id": 999,
                    "cast": [valid_actor_1.id, valid_actor_2.id],
                },
                "Invalid director id. Director does not exist.",
            ),
            (
                False,
                {
                    "name": "Film Name",
                    "release": "2021-01-01",
                    "genre": "Action",
                    "description": "Valid film description",
                    "duration": 120,
                    "director_id": valid_director.id,
                    "cast": [999, valid_actor_2.id],
                },
                "Invalid actor id. Actor does not exist.",
            ),
        ]

        for i, example in enumerate(film_tests):
            valid: bool
            data: dict
            message: str
            valid, data, message = example
            serializer: FilmSerializer = FilmSerializer(data=data)
            instance_valid: bool = serializer.is_valid()
            self.assertTrue(
                instance_valid is valid,
                f"Failed film test {i+1}. {message}\nData:\n{json.dumps(data)}",
            )

    def test_review(self) -> None:
        valid_user: User = User.objects.create(
            username="test_username", email="test1@test1.com", password="Password1"
        )
        valid_user.save()
        valid_director: Director = Director.objects.create(name="Test Director")
        valid_director.save()
        valid_actor_1: Actor = Actor.objects.create(name="Test Actor 1")
        valid_actor_1.save()
        valid_actor_2: Actor = Actor.objects.create(name="Test Actor 2")
        valid_actor_2.save()
        valid_film: Film = Film.objects.create(
            name="Film Name",
            release="2015-01-01",
            genre="Action",
            description="Valid film description",
            duration=120,
            director_id=valid_director,
        )
        valid_film.cast.set([valid_actor_1, valid_actor_2])
        valid_film.save()
        review_tests: list[tuple[bool, dict, str]] = [
            (
                True,
                {"user_id": valid_user.id, "film_id": valid_film.id, "rating": 5},
                "Valid review data.",
            ),
            (
                True,
                {
                    "user_id": valid_user.id,
                    "film_id": valid_film.id,
                    "rating": 5,
                    "content": "Review content",
                },
                "Valid review data.",
            ),
            (
                False,
                {"user_id": valid_user.id, "film_id": valid_film.id, "rating": 11},
                "Invalid rating. Rating must be between 1 and 10.",
            ),
            (
                False,
                {"user_id": valid_user.id, "film_id": valid_film.id, "rating": 0},
                "Invalid rating. Rating must be between 1 and 10.",
            ),
            (
                False,
                {
                    "user_id": valid_user.id,
                    "film_id": valid_film.id,
                    "rating": 5,
                    "content": "a" * 1000,
                },
                "Invalid content. Content must be less than 500 characters.",
            ),
            (
                False,
                {"user_id": 999, "film_id": valid_film.id, "rating": 5},
                "Invalid user id. User does not exist.",
            ),
            (
                False,
                {"user_id": valid_user.id, "film_id": 999, "rating": 5},
                "Invalid film id. Film does not exist.",
            ),
        ]

        for i, example in enumerate(review_tests):
            valid: bool
            data: dict
            message: str
            valid, data, message = example
            serializer: ReviewSerializer = ReviewSerializer(data=data)
            instance_valid: bool = serializer.is_valid()
            if "user_id" in data and isinstance(data["user_id"], User):
                data["user_id"] = data["user_id"].id
            if "film_id" in data and isinstance(data["film_id"], Film):
                data["film_id"] = data["film_id"].id
            self.assertTrue(
                instance_valid is valid,
                f"Failed review test {i+1}. {message}\nData:\n{json.dumps(data)}",
            )
