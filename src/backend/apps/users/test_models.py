from django.test import TestCase
from apps.users.models import User, Director, Actor, Film, Review
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class TestModels(TestCase):
    def test_user(self) -> None:
        user: User = User.objects.create(
            username="test_username1",
            email="test1@test1.com",
            password="Password1",
            professional=True,
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "test_username1")
        self.assertEqual(user.email, "test1@test1.com")
        self.assertEqual(user.password, "Password1")
        self.assertTrue(user.professional)

        user = User.objects.create(
            username="test_username2",
            email="test2@test2.com",
            password="Password1",
        )
        self.assertTrue(not user.professional)

    def test_director(self) -> None:
        director: Director = Director.objects.create(name="test_director")
        self.assertIsInstance(director, Director)
        self.assertEqual(director.name, "test_director")
        self.assertIsNone(director.nationality)

        director = Director.objects.create(
            name="test_director2", nationality="test_nationality"
        )
        self.assertEqual(director.nationality, "test_nationality")

    def test_actor(self) -> None:
        actor: Actor = Actor.objects.create(name="test_actor")
        self.assertIsInstance(actor, Actor)
        self.assertEqual(actor.name, "test_actor")
        self.assertIsNone(actor.nationality)

        actor = Actor.objects.create(name="test_actor2", nationality="test_nationality")
        self.assertEqual(actor.nationality, "test_nationality")

    def test_film(self) -> None:
        director: Director = Director.objects.create(name="test_director")
        director.save()

        actor: Actor = Actor.objects.create(name="test_actor")
        actor.save()

        film = Film.objects.create(
            name="test_film",
            release="2021-01-01",
            genre="Action",
            description="test_description",
            duration=1.5,
            director_id=director,
        )
        film.cast.add(actor)
        film.save()

        self.assertIsInstance(film, Film)
        self.assertEqual(film.name, "test_film")
        self.assertEqual(film.release, "2021-01-01")
        self.assertEqual(film.genre, "Action")
        self.assertEqual(film.description, "test_description")
        self.assertEqual(film.duration, 1.5)
        self.assertEqual(film.director_id, director)
        self.assertEqual(film.cast.first(), actor)

        with self.assertRaises(ValidationError):
            film: Film = Film.objects.create(
                name="test_film2",
                release="2021-01-01",
                genre="incorrect genre",
                description="test_description",
                duration=1.5,
                director_id=director,
            )
            film.save()

    def test_review(self) -> None:
        user: User = User.objects.create(
            username="test_username",
            email="test@test.com",
            password="Password1",
        )
        user.save()

        film: Film = Film.objects.create(
            name="test_film",
            release="2021-01-01",
            genre="Action",
            description="test_description",
            duration=1.5,
        )
        film.save()

        review: Review = Review.objects.create(
            user_id=user, film_id=film, rating=5, content="test"
        )
        review.save()

        self.assertIsInstance(review, Review)
        self.assertEqual(review.user_id, user)
        self.assertEqual(review.film_id, film)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, "test")

        with self.assertRaises(IntegrityError):
            Review.objects.create(user_id=user, film_id=film, rating=7, content="test1")
