import re
import sys
import datetime

from django.http import QueryDict
from django.contrib.auth.base_user import AbstractBaseUser
from django.core import validators
from django.contrib.auth import authenticate
from django.db.models import Value, Avg, Case, When
from rest_framework import serializers, exceptions

# from .models import User, Director, Actor, Film, Score, Review
from apps.users import models
from apps.users.models import User, Director, Actor, Film, Review

PASSWORD_VALIDATION_PATTERN = r"^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z]).*$"

# Notes.
# 1. Current password verification to change user data is done in views.py. This is
# because, doing it in UserSerializer would require to use an optional serializer field
# (current password would be required to update the user but not to create it), and that
# implementation of optional serializer arguments is not straightforward.

# See more in:
# https://stackoverflow.com/questions/38845051/how-to-update-user-password-in-django-rest-framework


class UserSerializer(serializers.ModelSerializer):

    email: serializers.Field = serializers.EmailField(style={"input_type": "email"})
    password: serializers.Field = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields: tuple[str, str, str, bool, str] = (
            "id",
            "username",
            "email",
            "password",
            # "professional",
            # "profile_picture",
        )

        extra_kwargs: dict[str, dict[str, bool]] = {
            "password": {"write_only": True},
            "style": {"input_type": "password"},
        }  # Hide password after serialization

    def validate_username(value: str) -> str:
        if len(value) < 4 or len(value) > 15:
            raise serializers.ValidationError(
                {"username": ["Username must have between 4 and 15 characters."]}
            )
        return value

    def validate_password(self, value: str) -> str:

        # Define password validation error message
        validation_error_message: str = (
            "Password must contain at least one lowercase letter, "
            "one uppercase letter, and one number."
        )

        # Check if introduced password satisfies the patternn
        if not re.match(PASSWORD_VALIDATION_PATTERN, value):
            raise serializers.ValidationError({"password": [validation_error_message]})

        return value

    def validate_email(self, value: str) -> str:

        # Recommended: Utilize Django's built-in email validator:
        try:
            validators.validate_email(value)
        except exceptions.ValidationError:
            raise serializers.ValidationError({"email": ["Invalid email format."]})

        # Note. This validator is equivalent to the default Django validator, executed
        # when no custom validator is defined. However, I prefer to make it explicit.

        return value

    def create(self, validated_data) -> User:

        # Note.
        # When using the create user method Django internally calls the set_password
        # method to save the password hashed. So there is no need to call it explicitly.
        user: User = User.objects.create_user(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            password=validated_data.get("password"),
            professional=False,
            # profile_picture=validated_data.get("profile_picture", None),
        )
        return user


class UserLoginSerializer(serializers.Serializer):

    username: serializers.Field = serializers.CharField()
    password: serializers.Field = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def validate(self, data) -> AbstractBaseUser:
        # Ejercicio 11
        username: str = data.get("username")
        password: str = data.get("password")

        if username and password:
            user: AbstractBaseUser = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )
            if not user:
                raise serializers.ValidationError(
                    {"user": ["Unable to log in with provided credentials."]}
                )
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    current_password: serializers.Field = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    username: serializers.Field = serializers.CharField(allow_blank=True)
    email: serializers.Field = serializers.EmailField(allow_blank=True)
    new_password: serializers.Field = serializers.CharField(
        style={"input_type": "password"}, source="password", allow_blank=True
    )

    class Meta:
        model = User
        fields: list[str] = [
            "current_password",
            "username",
            "email",
            "new_password",
        ]

    def validate_current_password(self, value: str) -> str:
        # Check that the current_password field is correct.
        if not self.instance.check_password(value):
            raise serializers.ValidationError({"current_password": ["Wrong password."]})
        return value

    def validate_username(self, value: str) -> str:
        if value == "":
            value = self.instance.username
        if len(value) < 4 or len(value) > 15:
            raise serializers.ValidationError(
                {"username": ["Username must have between 4 and 15 characters."]}
            )
        return value

    def validate_email(self, value: str) -> str:
        if value == "":
            value = self.instance.email
        # Recommended: Utilize Django's built-in email validator:
        try:
            validators.validate_email(value)
        except exceptions.ValidationError:
            raise serializers.ValidationError(
                {"email": ["Enter a valid email address."]}
            )

        return value

    def validate_new_password(self, value: str) -> str:

        if not value == "":
            # Define password validation error message
            validation_error_message: str = (
                "Password must contain at least one lowercase letter, "
                "one uppercase letter, and one number."
            )

            # Check if introduced password satisfies the patternn
            if not re.match(PASSWORD_VALIDATION_PATTERN, value):
                raise serializers.ValidationError(
                    {"new_password": [validation_error_message]}
                )

        return value

    def update(self, instance: User, validated_data: dict) -> User:
        # remove the current_password field from the validated_data dictionary
        validated_data.pop("current_password", None)
        new_password: str = validated_data.pop("password", None)
        if not new_password:
            instance.set_password(new_password)
        return super().update(instance, validated_data)


class UserDeleteSerializer(serializers.ModelSerializer):
    password: serializers.Field = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields: list[str] = ["password"]

    def validate_password(self, value: str) -> str:
        if value == "":
            raise serializers.ValidationError({"password": ["Password required."]})
        if not self.instance.check_password(value):
            raise serializers.ValidationError({"password": ["Wrong password."]})
        return value


class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields: list[str] = ["name", "nationality"]

    def validate_fields(self, data: dict) -> dict:
        """
        Validates fields of the Director model ignoring database internal integrity
        """
        name: str | None = data.get("name", None)
        data["name"] = self.validate_name(name)
        nationality: str | None = data.get("nationality", None)
        if nationality:  # nationality is optional
            data["nationality"] = self.validate_release(nationality)

    def validate_name(self, value) -> str:
        if value is None:
            raise serializers.ValidationError({"name": ["Director name required."]})
        if type(value) is not str:
            raise serializers.ValidationError(
                {"name": ["Director name must be a string."]}
            )
        if len(value) > models.NAME_MAX_LENGTH:
            max_lenght: int = models.NAME_MAX_LENGTH
            message: str = f"Director name cannot exceed {max_lenght} characters."
            raise serializers.ValidationError({"name": [message]})

        pattern = r"^\w+\s+\w+"  # pattern to check if string contains at least 2 words
        if not bool(re.match(pattern, value)):
            raise serializers.ValidationError(
                {"name": ["Director name must be at least 2 words long."]}
            )
        return value

    def validate_nationality(self, value) -> str:
        if value is not None and type(value) is not str:
            raise serializers.ValidationError(
                {"nationality": ["Nationality must be a string."]}
            )
        return value

    def create(self, validated_data) -> Director:
        try:
            director: Director = Director.objects.create(
                name=validated_data.get("name"),
                nationality=validated_data.get("nationality", None),
            )
        except serializers.IntegrityError:
            raise serializers.ValidationError("Director already exists")
        return director

    def update(self, instance, validated_data) -> Director:
        # if password is specified, set_password method saves the password hashed
        instance.name = validated_data.get("name", instance.name)
        instance.nationality = validated_data.get("nationality", instance.nationality)
        instance.save()
        return instance


class DeleteDirectorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Review
        fields: list[str] = ["id"]


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields: list[str] = ["name", "nationality"]

    def validate_fields(self, data: dict) -> dict:
        """
        Validates fields of the Actor model ignoring database internal integrity
        """
        name: str | None = data.get("name", None)
        data["name"] = self.validate_name(name)
        nationality: str | None = data.get("nationality", None)
        if nationality:  # nationality is optional
            data["nationality"] = self.validate_release(nationality)

    def validate_name(self, value: str) -> str:
        if value is None:
            raise serializers.ValidationError({"name": ["Actor name required."]})
        pattern = r"^\w+\s+\w+"  # pattern to check if string contains at least 2 words
        if not bool(re.match(pattern, value)):
            raise serializers.ValidationError(
                {"name": ["Director name must be at least 2 words long."]}
            )
        if len(value) > models.NAME_MAX_LENGTH:
            max_lenght: int = models.NAME_MAX_LENGTH
            message: str = f"Actor name cannot exceed {max_lenght} characters."
            raise serializers.ValidationError({"name": [message]})
        return value

    def validate_nationality(self, value) -> str:
        if value is not None and type(value) is not str:
            raise serializers.ValidationError(
                {"nationality": ["Nationality must be a string."]}
            )
        return value

    def create(self, validated_data: dict) -> Actor:
        actor: Actor = Actor.objects.create(
            name=validated_data.get("name"),
            nationality=validated_data.get("nationality", None),
        )
        return actor

    def update(self, instance, validated_data) -> Actor:
        # if password is specified, set_password method saves the password hashed
        instance.name = validated_data.get("name", instance.name)
        instance.nationality = validated_data.get("nationality", instance.nationality)
        instance.save()
        return instance


class DeleteActorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Review
        fields: list[str] = ["id"]


class FilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        # fields: str = "__all__"
        fields: list[str] = [
            "id",
            "name",
            "release",
            "genre",
            "description",
            "duration",
            "image_url",
            "director_id",
            "cast",
        ]

    def to_internal_value(self, data: dict) -> dict:
        """
        Override to prevent automatic conversion of data. Apply field validation
        directly to the raw input.
        """

        # Validate Film Attributes
        name: str | None = data.get("name", None)
        data["name"] = self.validate_name(name)
        release: str | None = data.get("release", None)
        data["release"] = self.validate_release(release)
        genre: str | None = data.get("genre", None)
        data["genre"] = self.validate_genre(genre)
        description: str | None = data.get("description", None)
        data["description"] = self.validate_description(description)
        duration: int | None = data.get("duration", None)
        data["duration"] = self.validate_duration(duration)
        image_url: str | None = data.get("image_url", None)
        if image_url is not None and not image_url == "":
            data["image_url"] = self.validate_image_url(image_url)
        director_id: int | None = data.get("director_id", None)
        data["director_id"] = self.validate_director_id(director_id)
        cast: list[int] | None = data.get("cast", None)
        data["cast"] = self.validate_cast(cast)

        return data

    def validate_name(self, value) -> str:
        if value is None or value == "":
            raise serializers.ValidationError({"name": ["Film name required."]})
        if type(value) is not str:
            raise serializers.ValidationError({"name": ["Film name must be a string."]})
        if len(value) > models.NAME_MAX_LENGTH:
            max_lenght: int = models.NAME_MAX_LENGTH
            message: str = f"Film name cannot exceed {max_lenght} characters."
            raise serializers.ValidationError({"name": [message]})
        return value

    def validate_release(self, value) -> str:
        if value is None or value == "":
            raise serializers.ValidationError({"release": ["Release date required."]})
        if type(value) is not str and type(value) is not datetime.datetime:
            message: str = "Invalid date format. Release must be string or datetime"
            raise serializers.ValidationError({"release": [message]})
        if type(value) is str:
            try:
                patterns: dict[str, str] = {
                    "%Y": r"^\d{4}$",
                    "%Y-%m": r"^\d{4}-\d{2}$",
                    "%Y-%m-%d": r"^\d{4}-\d{2}-\d{2}$",
                    "%m-%Y": r"^\d{2}-\d{4}$",
                    "%d-%m-%Y": r"^\d{2}-\d{2}-\d{4}$",
                }
                format_match: bool = False
                for date_format, pattern in patterns.items():
                    if re.match(pattern, value):
                        format_match = True
                        print(f"Matched {date_format} format", file=sys.stderr)
                        return datetime.datetime.strptime(value, date_format)

                if not format_match:
                    raise serializers.ValidationError(
                        "Invalid date format.",
                        "Accepted formats: %Y, %Y-%m, %Y-%m-%d, %m-%Y, %d-%m-%Y",
                    )

            except ValueError:
                raise serializers.ValidationError({"release": ["Invalid date."]})
        return value

    def validate_genre(self, value: str) -> str:
        if value is None or value == "":
            raise serializers.ValidationError({"genre": ["Genre required."]})
        if value not in Film.GENRE_CHOICES:
            raise serializers.ValidationError({"genre": ["Invalid genre."]})
        return value

    def validate_description(self, value) -> str:
        if value is None or value == "":
            raise serializers.ValidationError(
                {"description": ["Description required."]}
            )
        if len(value) > models.CONTENT_MAX_LENGTH:
            max_lenght: int = models.CONTENT_MAX_LENGTH
            message: str = f"Description cannot exceed {max_lenght} characters."
            raise serializers.ValidationError({"description": [message]})

        return value

    def validate_duration(self, value: int) -> int:
        try:
            value: int = int(value)
        except ValueError:
            raise serializers.ValidationError(
                {"duration": ["Duration must be numeric."]}
            )

        return value

    def validate_image_url(self, value: str) -> str:
        if type(value) is not str:
            raise serializers.ValidationError(
                {"image_url": ["Image URL must be a string."]}
            )
        url_pattern = r"^https://"
        if not re.match(url_pattern, value):
            raise serializers.ValidationError(
                {"image_url": ["Invalid image URL format."]}
            )
        return value

    def validate_director_id(self, value: int) -> Director:
        if value is None or type(value) is not int:
            raise serializers.ValidationError({"director_id": ["Director required."]})
        try:
            instance: Director = Director.objects.get(pk=value)
        except Director.DoesNotExist:
            raise serializers.ValidationError({"director_id": ["Invalid director ID."]})
        return instance

    def validate_cast(self, value: list[int]) -> list[Actor]:
        print("validate_cast", file=sys.stderr)
        if value is None or not type(value) is list:
            raise serializers.ValidationError(
                {"cast": ["Cast must be a list of names (list[str])."]}
            )
        try:
            instance: Actor
            instances: list[Actor] = []
            for id in value:
                if id is None or type(id) is not int:
                    raise serializers.ValidationError({"cast": ["Invalid cast ID."]})
                else:
                    # instance = Actor.objects.filter(pk__in=id)
                    instance = Actor.objects.get(pk=id)
                    instances.append(instance)
        except Actor.DoesNotExist:
            raise serializers.ValidationError({"cast": ["Invalid cast ID."]})

        return instances

    def to_representation(self, instance: Review) -> dict:
        """Transforms the instance into its JSON representation."""
        representation: dict = super().to_representation(instance)

        director_id: int = representation.pop("director_id", None)
        representation["director"] = Director.objects.get(id=director_id).name
        cast_ids: int = representation.get("cast", None)
        representation["cast"] = [
            Actor.objects.get(id=cast_id).name for cast_id in cast_ids
        ]

        # Add the average rating
        avg_rating: float = instance.reviews.aggregate(
            avg_rating=Avg(
                Case(
                    When(rating__isnull=True, then=Value(0)),
                    default="rating",
                )
            )
        )["avg_rating"]
        representation["avg_rating"] = avg_rating if avg_rating is not None else 0

        return representation

    def create(self, validated_data: dict) -> Film:
        cast: list[Actor] = validated_data.pop("cast")
        film: Film = Film.objects.create(**validated_data)
        film.cast.set(cast)
        return film

    def update(self, instance: Film, validated_data: dict) -> Film:
        instance.name = validated_data.get("name", instance.name)
        instance.release = validated_data.get("release", instance.release)
        instance.genre = validated_data.get("genre", instance.genre)
        instance.description = validated_data.get("description", instance.description)
        instance.duration = validated_data.get("duration", instance.duration)
        instance.image_url = validated_data.get("image_url", instance.image_url)
        instance.director = validated_data.get("director_id", instance.director)

        if "cast" in validated_data:
            print(f"validated_data['cast']: {validated_data['cast']}", file=sys.stderr)
            instance.cast.set(validated_data["cast"])

        instance.save()
        return instance


class FilmFilterSerializer(serializers.Serializer):
    film_name = serializers.CharField()
    director_name = serializers.CharField()
    actor_name = serializers.CharField()
    genre = serializers.CharField()
    description = serializers.CharField()
    min_release = serializers.DateField()
    max_release = serializers.DateField()
    min_rating = serializers.IntegerField()
    max_rating = serializers.IntegerField()

    class Meta:
        fields: list[str] = [
            "film_name",
            "director_name",
            "actor_name",
            "genre",
            "description",
            "min_release",
            "max_release",
            "min_rating",
            "max_rating",
        ]

    def to_internal_value(self, qdata: QueryDict) -> dict:
        """
        Override to prevent automatic conversion of data. Apply field validation
        directly to the raw input.
        """

        data: dict = qdata.dict()

        # Validate Film Attributes
        film_name: str | None = data.get("film_name", None)
        if film_name is not None and not film_name == "":
            data["film_name"] = self.validate_film_name(film_name)
        director_name: str | None = data.get("director_name", None)
        if director_name is not None and not director_name == "":
            data["director_name"] = self.validate_director_name(director_name)
        actor_name: str | None = data.get("actor_name", None)
        if actor_name is not None and not actor_name == "":
            data["actor_name"] = self.validate_actor_name(actor_name)
        genre: str | None = data.get("genre", None)
        if genre is not None and not genre == "":
            data["genre"] = self.validate_genre(genre)
        description: str | None = data.get("genre", None)
        if description is not None and not description == "":
            data["description"] = self.validate_description(description)

        min_release: datetime.datetime | None = data.get("min_release", None)
        if min_release is not None and not min_release == "":
            data["min_release"] = self.validate_min_release(min_release)
        max_release: datetime.datetime | None = data.get("max_release", None)
        if max_release is not None and not max_release == "":
            data["max_release"] = self.validate_max_release(max_release)

        min_rating: int | None = data.get("min_rating", None)
        if min_rating is not None and not min_rating == "":
            data["min_rating"] = self.validate_min_rating(min_rating)
        max_rating: int | None = data.get("max_rating", None)
        if max_rating is not None and not max_rating == "":
            data["max_rating"] = self.validate_max_rating(max_rating)

        return data

    def validate_film_name(self, value: str) -> str:
        if type(value) is not str:
            raise serializers.ValidationError(
                {"film_name": ["Film name must be a string."]}
            )
        if len(value) > models.NAME_MAX_LENGTH:
            max_lenght: int = models.NAME_MAX_LENGTH
            message: str = f"Film name cannot exceed {max_lenght} characters."
            raise serializers.ValidationError({"film_name": [message]})
        return value

    def validate_director_name(self, value: str) -> str:
        if type(value) is not str:
            raise serializers.ValidationError(
                {"director_name": ["Director name must be a string."]}
            )
        if len(value) > models.NAME_MAX_LENGTH:
            max_lenght: int = models.NAME_MAX_LENGTH
            message: str = f"Director name cannot exceed {max_lenght} characters."
            raise serializers.ValidationError({"director_name": [message]})
        return value

    def validate_actor_name(self, value: str) -> str:
        if type(value) is not str:
            raise serializers.ValidationError(
                {"actor_name": ["Actor name must be a string."]}
            )
        if len(value) > models.NAME_MAX_LENGTH:
            max_lenght: int = models.NAME_MAX_LENGTH
            message: str = f"Actor name cannot exceed {max_lenght} characters."
            raise serializers.ValidationError({"actor_name": [message]})
        return value

    def validate_genre(self, value: str) -> str:
        if type(value) is not str:
            raise serializers.ValidationError({"genre": ["Genre must be a string."]})
        if value not in Film.GENRE_CHOICES:
            raise serializers.ValidationError({"genre": ["Invalid genre."]})
        return value

    def validate_description(self, value: str) -> str:
        if type(value) is not str:
            raise serializers.ValidationError(
                {"description": ["Description must be a string."]}
            )
        if len(value) > models.CONTENT_MAX_LENGTH:
            max_lenght: int = models.CONTENT_MAX_LENGTH
            message: str = f"Description cannot exceed {max_lenght} characters."
            raise serializers.ValidationError({"description": [message]})
        return value

    def validate_min_release(self, value: str) -> str:
        if type(value) is not str and type(value) is not datetime.datetime:
            message: str = "Invalid date format. Release must be string or datetime"
            raise serializers.ValidationError({"min_release": [message]})
        if type(value) is str:
            try:
                patterns: dict[str, str] = {
                    "%Y": r"^\d{4}$",
                    "%Y-%m": r"^\d{4}-\d{2}$",
                    "%Y-%m-%d": r"^\d{4}-\d{2}-\d{2}$",
                    "%m-%Y": r"^\d{2}-\d{4}$",
                    "%d-%m-%Y": r"^\d{2}-\d{2}-\d{4}$",
                }
                format_match: bool = False
                for date_format, pattern in patterns.items():
                    if re.match(pattern, value):
                        format_match = True
                        print(f"Matched {date_format} format", file=sys.stderr)
                        return datetime.datetime.strptime(value, date_format)

                if not format_match:
                    raise serializers.ValidationError(
                        "Invalid date format.",
                        "Accepted formats: %Y, %Y-%m, %Y-%m-%d, %m-%Y, %d-%m-%Y",
                    )

            except ValueError:
                raise serializers.ValidationError({"min_release": ["Invalid date."]})
        print(type(value), file=sys.stderr)
        return value

    def validate_max_release(self, value: str) -> str:
        if type(value) is not str and type(value) is not datetime.datetime:
            message: str = "Invalid date format. Release must be string or datetime"
            raise serializers.ValidationError({"max_release": [message]})
        if type(value) is str:
            try:
                patterns: dict[str, str] = {
                    "%Y": r"^\d{4}$",
                    "%Y-%m": r"^\d{4}-\d{2}$",
                    "%Y-%m-%d": r"^\d{4}-\d{2}-\d{2}$",
                    "%m-%Y": r"^\d{2}-\d{4}$",
                    "%d-%m-%Y": r"^\d{2}-\d{2}-\d{4}$",
                }
                format_match: bool = False
                for date_format, pattern in patterns.items():
                    if re.match(pattern, value):
                        format_match = True
                        print(f"Matched {date_format} format", file=sys.stderr)
                        return datetime.datetime.strptime(value, date_format)

                if not format_match:
                    raise serializers.ValidationError(
                        "Invalid date format.",
                        "Accepted formats: %Y, %Y-%m, %Y-%m-%d, %m-%Y, %d-%m-%Y",
                    )

            except ValueError:
                raise serializers.ValidationError({"max_release": ["Invalid date."]})
        return value

    def validate_min_rating(self, value: int) -> int:
        try:
            value: int = int(value)
        except ValueError:
            raise serializers.ValidationError(
                {"min_rating": ["Score must be numeric."]}
            )
        if value not in range(Review.MIN_SCORE, Review.MAX_SCORE + 1):
            raise serializers.ValidationError(
                {"min_rating": ["Score must be between 1 and 10."]}
            )
        return value

    def validate_max_rating(self, value: int) -> int:
        try:
            value: int = int(value)
        except ValueError:
            raise serializers.ValidationError(
                {"max_rating": ["Score must be numeric."]}
            )
        if value not in range(Review.MIN_SCORE, Review.MAX_SCORE + 1):
            raise serializers.ValidationError(
                {"max_rating": ["Score must be between 1 and 10."]}
            )
        return value


class DeleteFilmSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Review
        fields: list[str] = ["name"]


class ReviewSerializer(serializers.ModelSerializer):
    id: serializers.Field = serializers.IntegerField(read_only=True)
    rating: serializers.Field = serializers.IntegerField()
    content: serializers.Field = serializers.CharField()
    user_id: serializers.Field = serializers.IntegerField(read_only=True)
    film_id: serializers.Field = serializers.IntegerField()

    class Meta:
        model = Review
        fields: list[str] = ["id", "rating", "content", "user_id", "film_id"]

    def to_internal_value(self, data: dict) -> dict:
        """
        Override to prevent automatic conversion of data. Apply field validation
        directly to the raw input.
        """

        # Validate Film Attributes
        rating: int | None = data.get("rating", None)
        data["rating"] = self.validate_rating(rating)
        content: str | None = data.get("content", None)
        if content is not None:  # content is optional
            data["content"] = self.validate_content(content)

        # No need to validate user_id (as it is generated in the view)
        # But we take advantage of validation to transform user_id into User object
        user_id: int | None = data.get("user_id", None)
        data["user_id"] = self.validate_user_id(user_id)

        film_id: int | None = data.get("film_id", None)
        data["film_id"] = self.validate_film_id(film_id)

        print(data, file=sys.stderr)

        return data

    def validate_rating(self, value: int) -> int:
        if value is None:
            raise serializers.ValidationError({"rating": ["Rating required."]})
        try:
            value: int = int(value)
        except ValueError:
            raise serializers.ValidationError({"rating": ["Score must be numeric."]})
        if value not in range(Review.MIN_SCORE, Review.MAX_SCORE + 1):
            raise serializers.ValidationError(
                {"rating": ["Score must be between 1 and 10."]}
            )
        return value

    def validate_content(self, value: str) -> str:
        if type(value) is not str:
            raise serializers.ValidationError(
                {"content": ["Content must be a string."]}
            )
        if len(value) > models.CONTENT_MAX_LENGTH:
            max_lenght: int = models.CONTENT_MAX_LENGTH
            message: str = f"Content cannot exceed {max_lenght} characters."
            raise serializers.ValidationError({"description": [message]})

        return value

    def validate_user_id(self, value: int) -> int:
        if value is None:
            raise serializers.ValidationError({"user_id": ["User ID required."]})
        try:
            value: int = int(value)
        except ValueError:
            raise serializers.ValidationError(
                {"user_id": ["User ID must be an integer."]}
            )
        try:
            instance: Film = User.objects.get(pk=value)
        except Film.DoesNotExist:
            raise serializers.ValidationError({"user_id": ["Invalid user ID."]})
        return instance

    def validate_film_id(self, value: int) -> int:
        if value is None:
            raise serializers.ValidationError({"film_id": ["Film ID required."]})
        try:
            value: int = int(value)
        except ValueError:
            raise serializers.ValidationError(
                {"film_id": ["Film ID must be an integer."]}
            )
        try:
            instance: Film = Film.objects.get(pk=value)
        except Film.DoesNotExist:
            raise serializers.ValidationError({"film_id": ["Invalid film ID."]})
        return instance

    def to_representation(self, instance: Review) -> dict:
        """Transforms the instance into its JSON representation."""
        # representation: dict = super().to_representation(instance)

        representation: dict = {}
        representation["id"] = instance.id
        representation["user_id"] = instance.user_id.id
        representation["film_id"] = instance.film_id.id
        representation["film"] = instance.film_id.name
        representation["content"] = instance.content
        representation["rating"] = instance.rating

        return representation

    def create(self, validated_data: dict) -> Review:
        film: Film = validated_data.pop("film_id")
        user: User = validated_data.pop("user_id")
        review: Review = Review.objects.create(**validated_data)
        review.user_id = user
        review.film_id = film
        review.save()
        return review


class DeleteReviewSerializer(serializers.ModelSerializer):
    review_id: serializers.Serializer = serializers.IntegerField()

    class Meta:
        model = Review
        fields: list[str] = ["review_id"]
