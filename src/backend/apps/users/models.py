from django.db import models
from django.contrib.auth.models import AbstractUser

NAME_MAX_LENGTH = 64
CONTENT_MAX_LENGTH = 500


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    email = models.EmailField(max_length=NAME_MAX_LENGTH, unique=True)
    password = models.CharField(max_length=NAME_MAX_LENGTH)
    professional = models.BooleanField(default=False)

    # In this case,
    # as we require both the email and the username to be unique,
    # we will not overwrite the save method to set the email as username
    def save(self, *args, **kwargs) -> None:
        # This is equivalent to de default save method
        super().save(*args, **kwargs)


class Director(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    nationality = models.CharField(max_length=NAME_MAX_LENGTH, null=True)


class Actor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    nationality = models.CharField(max_length=NAME_MAX_LENGTH, null=True)


class Film(models.Model):

    GENRE_CHOICES: list[str] = [
        "Action",
        "Comedy",
        "Crime",
        "Documentary",
        "Drama",
        "Horror",
        "Romance",
        "Sci-Fi",
        "Thriller",
        "Western",
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    release = models.DateField()
    genre = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField()
    duration = models.FloatField()
    image_url = models.CharField(max_length=200, null=True)
    director_id = models.ForeignKey(
        Director, on_delete=models.SET_NULL, null=True, related_name="films"
    )
    cast = models.ManyToManyField(Actor, related_name="films")


class Review(models.Model):

    MIN_SCORE = 1
    MAX_SCORE = 10

    id = models.AutoField(primary_key=True)
    rating = models.IntegerField(default=0)
    content = models.TextField(max_length=CONTENT_MAX_LENGTH, null=True)

    # Note.
    # The problem of using delete on CASCADE is that it requires to ensure that a
    # review is always going to have a film instance to match, and the only way to
    # ensure this is defining a default value. (The reason why the default value is
    # the only posible solution is because the ensurance must be done with
    # independence of the number of existing instances in the foreing table, which
    # therefore, can be 0)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # film = models.ForeignKey(Film, on_delete=models.CASCADE)

    # Note.
    # We prefer to make the field nullable, and ensure existance of foreing instace
    # in the model serializer

    user_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="reviews"
    )
    film_id = models.ForeignKey(
        Film, on_delete=models.SET_NULL, null=True, related_name="reviews"
    )

    class Meta:
        constraints: list[models.BaseConstraint] = [
            models.UniqueConstraint(
                fields=["user_id", "film_id"], name="unique_combination"
            )
        ]
