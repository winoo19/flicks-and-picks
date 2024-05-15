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
        # user: User = User.objects.create(
        #     username="test_username1",
        #     email="test1@test1.com",
        #     password="Password1",
        #     professional=True,
        # )
        # self.assertIsInstance(user, User)
        # self.assertEqual(user.username, "test_username1")
        # self.assertEqual(user.email, "test1@test1.com")
        # self.assertEqual(user.password, "Password1")
        # self.assertTrue(user.professional)

        # user = User.objects.create(
        #     username="test_username2",
        #     email="test2@test2.com",
        #     password="Password1",
        # )
        # self.assertTrue(not user.professional)

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

    def test_director(self) -> None:
        # director: Director = Director.objects.create(name="test_director")
        # self.assertIsInstance(director, Director)
        # self.assertEqual(director.name, "test_director")
        # self.assertIsNone(director.nationality)

        # director = Director.objects.create(
        #     name="test_director2", nationality="test_nationality"
        # )
        # self.assertEqual(director.nationality, "test_nationality")

        director_tests: list[tuple[bool, dict, str]] = [
            (
                True,
                {
                    "name": "Director Name",
                    "nationality": "Spanish",
                },
                "Valid director data.",
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
        # actor: Actor = Actor.objects.create(name="test_actor")
        # self.assertIsInstance(actor, Actor)
        # self.assertEqual(actor.name, "test_actor")
        # self.assertIsNone(actor.nationality)

        # actor = Actor.objects.create(name="test_actor2", nationality="nationality")
        # self.assertEqual(actor.nationality, "test_nationality")

        actor_tests: list[tuple[bool, dict, str]] = [
            (
                True,
                {
                    "name": "Actor Name",
                    "nationality": "Spanish",
                },
                "Valid actor data.",
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
        # director: Director = Director.objects.create(name="test_director")
        # director.save()

        # actor: Actor = Actor.objects.create(name="test_actor")
        # actor.save()

        # film = Film.objects.create(
        #     name="test_film",
        #     release="2021-01-01",
        #     genre="Action",
        #     description="test_description",
        #     duration=1.5,
        #     director_id=director,
        # )
        # film.cast.add(actor)
        # film.save()

        # self.assertIsInstance(film, Film)
        # self.assertEqual(film.name, "test_film")
        # self.assertEqual(film.release, "2021-01-01")
        # self.assertEqual(film.genre, "Action")
        # self.assertEqual(film.description, "test_description")
        # self.assertEqual(film.duration, 1.5)
        # self.assertEqual(film.director_id, director)
        # self.assertEqual(film.cast.first(), actor)

        # with self.assertRaises(ValidationError):
        #     film: Film = Film.objects.create(
        #         name="test_film2",
        #         release="2021-01-01",
        #         genre="incorrect genre",
        #         description="test_description",
        #         duration=1.5,
        #         director_id=director,
        #     )
        #     film.save()

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
        # user: User = User.objects.create(
        #     username="test_username",
        #     email="test@test.com",
        #     password="Password1",
        # )
        # user.save()

        # film: Film = Film.objects.create(
        #     name="test_film",
        #     release="2021-01-01",
        #     genre="Action",
        #     description="test_description",
        #     duration=1.5,
        # )
        # film.save()

        # review: Review = Review.objects.create(
        #     user_id=user, film_id=film, rating=5, content="test"
        # )
        # review.save()

        # self.assertIsInstance(review, Review)
        # self.assertEqual(review.user_id, user)
        # self.assertEqual(review.film_id, film)
        # self.assertEqual(review.rating, 5)
        # self.assertEqual(review.content, "test")

        # with self.assertRaises(IntegrityError):
        #     Review.objects.create(
        #         user_id=user,
        #         film_id=film,
        #         rating=7,
        #         content="test1"
        #     )

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
        ]

        for i, example in enumerate(review_tests):
            valid: bool
            data: dict
            message: str
            valid, data, message = example
            serializer: ReviewSerializer = ReviewSerializer(data=data)
            instance_valid: bool = serializer.is_valid()
            data["user_id"] = data["user_id"].id
            data["film_id"] = data["film_id"].id
            self.assertTrue(
                instance_valid is valid,
                f"Failed review test {i+1}. {message}\nData:\n{json.dumps(data)}",
            )
