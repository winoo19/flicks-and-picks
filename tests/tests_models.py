from django.test import TestCase
from ..models import User, Director, Actor, Film, Review
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class TestModels(TestCase):
    def test_user(self):
        user = User.objects.create(
            username="test_username",
            email="em@i.l",
            password="test_password",
            professional=True,
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "test_username")
        self.assertEqual(user.email, "em@i.l")
        self.assertEqual(user.password, "test_password")
        self.assertTrue(user.professional)

        user = User.objects.create(
            username="test_username",
            email="em@i.l",
            password="test_password",
        )
        self.assertTrue(not user.professional)

    def test_director(self):
        director = Director.objects.create(name="test_director")
        self.assertIsInstance(director, Director)
        self.assertEqual(director.name, "test_director")
        self.assertIsNone(director.nationality)

        director = Director.objects.create(
            name="test_director", nationality="test_nationality"
        )
        self.assertEqual(director.nationality, "test_nationality")

    def test_actor(self):
        actor = Actor.objects.create(name="test_actor")
        self.assertIsInstance(actor, Actor)
        self.assertEqual(actor.name, "test_actor")
        self.assertIsNone(actor.nationality)

        actor = Actor.objects.create(name="test_actor", nationality="test_nationality")
        self.assertEqual(actor.nationality, "test_nationality")

    def test_film(self):
        director = Director.objects.create(name="test_director")
        director.save()

        actor = Actor.objects.create(name="test_actor")
        actor.save()

        film = Film.objects.create(
            name="test_film",
            release="2021-01-01",
            genre="Action",
            description="test_description",
            duration=1.5,
            director=director,
        )
        film.cast.add(actor)
        film.save()

        self.assertIsInstance(film, Film)
        self.assertEqual(film.name, "test_film")
        self.assertEqual(film.release, "2021-01-01")
        self.assertEqual(film.genre, "Action")
        self.assertEqual(film.description, "test_description")
        self.assertEqual(film.duration, 1.5)
        self.assertEqual(film.director, director)
        self.assertEqual(film.cast.first(), actor)

        with self.assertRaises(ValidationError):
            film.genre = "test_genre"

    def test_review(self):
        user = User.objects.create(
            username="test_username",
            email="em@i.l",
            password="test_password",
        )
        user.save()

        film = Film.objects.create(
            name="test_film",
            release="2021-01-01",
            genre="Action",
            description="test_description",
            duration=1.5,
        )
        film.save()

        review = Review.objects.create(user=user, film=film, value=5, content="test")
        review.save()

        self.assertIsInstance(review, Review)
        self.assertEqual(review.user, user)
        self.assertEqual(review.film, film)
        self.assertEqual(review.value, 5)
        self.assertEqual(review.content, "test")

        with self.assertRaises(IntegrityError):
            Review.objects.create(user=user, film=film, value=7, content="test1")
