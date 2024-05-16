import datetime
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import transaction, IntegrityError
from django.db.models import QuerySet, Value, Avg, Case, When
from django.db.models.manager import BaseManager
from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied

# from rest_framework.authentication import SessionAuthentication
# from rest_framework.exceptions import PermissionDenied

from apps.users.models import User, Film, Director, Actor, Review
from apps.users.serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserUpdateSerializer,
    UserDeleteSerializer,
    DirectorSerializer,
    DeleteDirectorSerializer,
    ActorSerializer,
    DeleteActorSerializer,
    FilmSerializer,
    FilmFilterSerializer,
    DeleteFilmSerializer,
    ReviewSerializer,
    DeleteReviewSerializer,
)

# To display headers and authenticators of a view request:
# print("\nRequest headers:")
# for header, value in request.META.items():
#     if header.startswith("HTTP_"):
#         print(f"{header}: {value}")

# print("\nAuthenticators:")
# for auth in request.authenticators:
#     print(auth)
# print()


class UserRegisterView(generics.CreateAPIView):
    serializer_class: type = UserSerializer
    # Specify that unauthenticated (service) users have access to this view

    def post(self, request: Request) -> Response:
        # parse data
        data: dict = {
            k: v[0] if type(v) is list and len(v) == 1 else v
            for k, v in dict(request.data).items()
        }
        # serialize
        serializer: serializers.Serializer = self.get_serializer(data=data)
        response: Response
        if serializer.is_valid():
            serializer.save()  # Directly use create() from the serializer
            response_content: dict[str, str] = {
                "detail": "Singin successful",
            }
            response = Response(response_content, status=status.HTTP_201_CREATED)
        else:
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return response


class UserLoginView(generics.GenericAPIView):
    serializer_class: type = UserLoginSerializer
    # Specify that unauthenticated (web) users have access to this view

    def get_object(self) -> AbstractBaseUser:
        """Overwrite method to get the authenticated user object"""
        try:
            session_key: str = self.request.COOKIES.get("session")
            user: AbstractBaseUser = Token.objects.get(key=session_key).user
        except ObjectDoesNotExist:
            user = None
        return user

    def post(self, request: Request) -> Response:
        response: Response
        user: AbstractBaseUser

        try:
            # parse data
            data: dict = {
                k: v[0] if type(v) is list and len(v) == 1 else v
                for k, v in dict(request.data).items()
            }
            # Verify the absence of session token
            serializer: serializers.Serializer = self.get_serializer(data=data)
            user = self.get_object()
            if user:
                raise ValidationError("Already logged in.")

            # Run serializer validations
            user = serializer.is_valid()
            if not user:
                raise ValidationError("Unable to log in with provided credentials.")

            # Create response content (in this case, just a confirmation message)
            response_content: dict[str, str] = {
                "detail": "Login successful",
            }
            # Create response object
            response = Response(data=response_content, status=status.HTTP_200_OK)
            # Aggregate cookie to the response
            token: Token
            token, _ = Token.objects.get_or_create(user=serializer.validated_data)
            response.set_cookie(
                key="session",
                value=token.key,
                secure=True,
                httponly=True,
                samesite="lax",
            )

        except ValidationError as error:
            response = Response(
                {"detail": error.message},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return response


class UserProfileInfoView(generics.RetrieveAPIView):
    serializer_class: type = UserSerializer
    # Specify that only authenticated (web) users have access to this view

    def get_object(self) -> AbstractBaseUser:
        """Overwrite method to get the authenticated user object"""

        # Note.
        # I think that once I have specified permission classes I could simply do this:
        # return self.request.user

        try:
            session_key: str = self.request.COOKIES.get("session")
            user: AbstractBaseUser = Token.objects.get(key=session_key).user
        except ObjectDoesNotExist:
            raise PermissionDenied("session cookie missing or not valid")
        return user

    def get(self, request: Request) -> Response:

        response: Response
        try:
            user: AbstractBaseUser = self.get_object()
            serializer: serializers.Serializer = self.get_serializer(user)
            response = Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except PermissionDenied as error:
            response = Response(
                {"detail": str(error)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return response


class UserProfileUpdateView(generics.UpdateAPIView):
    # Specify that only authenticated (web) users have access to this view

    def get_serializer_class(self) -> serializers.Serializer:
        return UserUpdateSerializer

    def get_object(self) -> AbstractBaseUser:
        """Overwrite method to get the authenticated user object"""
        try:
            session_key: str = self.request.COOKIES.get("session")
            user: AbstractBaseUser = Token.objects.get(key=session_key).user
        except ObjectDoesNotExist:
            raise PermissionDenied("session cookie missing or not valid")
        return user

    def update(self, request: Request) -> Response:
        response: Response

        try:
            # parse data
            data: dict = {
                k: v[0] if type(v) is list and len(v) == 1 else v
                for k, v in dict(request.data).items()
            }
            # Get user (or raise error if no cookie)
            user: AbstractBaseUser = self.get_object()

            # Serialize and validate user data
            serializer: serializers.ModelSerializer = self.get_serializer(
                user,
                data=data,
            )
            serializer.is_valid(raise_exception=True)  # Check user's current password
            serializer.save()

            response = Response(
                status=status.HTTP_200_OK,
                data={"detail": "Update successful"},
            )

        except ValidationError as error:
            response = Response(
                {"detail": error.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except PermissionDenied as error:
            response = Response(
                {"detail": str(error)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return response


class UserLogoutView(generics.GenericAPIView):

    # Note.
    # In Django REST Framework, the serializer_class attribute is used by the framework
    # to handle request data and to generate forms in the browsable API. Even if you’re
    # not explicitly using a serializer in your view, the framework still expects this
    # attribute to be set. However, if you don’t need to serialize any data in your
    # view, you can override the get_serializer_class() method to return a basic
    # Serializer class. This will satisfy the framework’s requirement without affecting
    # your view’s functionality.

    def get_serializer_class(self) -> serializers.Serializer:
        return serializers.Serializer  # Return basic Serializer class

    def delete(self, request: Request) -> Response:
        response: Response

        try:
            session_key: str = self.request.COOKIES.get("session")
            token: Token = Token.objects.get(key=session_key)
            response = Response(
                status=status.HTTP_200_OK,
                data={"detail": "Logout successful"},
            )
            response.delete_cookie(key="session")
            token.delete()

        except ObjectDoesNotExist:
            response = Response(
                {"detail": "Session cookie not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return response


# class UserVerificationView(generics.GenericAPIView)


class UserDeleteView(generics.DestroyAPIView):

    def get_serializer_class(self) -> serializers.Serializer:
        return UserDeleteSerializer

    def get_object(self) -> AbstractBaseUser:
        """Overwrite method to get the authenticated user object"""
        try:
            session_key: str = self.request.COOKIES.get("session")
            user: AbstractBaseUser = Token.objects.get(key=session_key).user
        except ObjectDoesNotExist:
            raise PermissionDenied("session cookie missing or not valid")
        return user

    def put(self, request: Request) -> Response:
        response: Response

        try:
            # get user
            user: User = self.get_object()

            # parse request data
            data: dict = {
                k: v[0] if type(v) is list and len(v) == 1 else v
                for k, v in dict(request.data).items()
            }
            # Get user using session cookie
            session_key: str = self.request.COOKIES.get("session")
            token: Token = Token.objects.get(key=session_key)
            user: AbstractBaseUser = token.user

            # Validate password
            serializer: serializers.ModelSerializer = self.get_serializer(
                user, data=data, partial=True
            )
            serializer.is_valid(raise_exception=True)  # Check user's current password

            response = Response(
                status=status.HTTP_200_OK,
                data={"detail": "Account deletion successful"},
            )
            response.delete_cookie(key="session")
            token.delete()
            user.delete()

        except PermissionDenied as error:
            response = Response(
                {"detail": str(error)},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except ValidationError as error:
            response = Response(
                {"detail": error.message},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return response

    def delete(self, request: Request) -> Response:
        # Using a DELETE method to delete a user would be the optimal practice, but as
        # django rest framework does not support using delete with json body (required
        # for password validation) we are using PUT instead.

        response: Response = Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"detail": "DELETE method not supported. Use PUT instead."},
        )

        return response


class FilterFilmsView(APIView):
    serializer_class: type = FilmFilterSerializer
    queryset: BaseManager[Film] = Film.objects.all()

    def get_object(self) -> AbstractBaseUser:
        """Overwrite method to get the authenticated user object"""
        try:
            session_key: str = self.request.COOKIES.get("session")
            user: AbstractBaseUser = Token.objects.get(key=session_key).user
        except ObjectDoesNotExist:
            raise PermissionDenied("session cookie missing or not valid")
        return user

    def get(self, request: Request) -> Response:
        # For some reason, django rest framework doesnt render the form when using
        # a HTTP GET resquest method. We are using POST instead.

        response: Response = Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"detail": "GET method not supported. Use POST instead."},
        )

        return response

    def post(self, request: Request) -> Response:

        response: Response
        try:
            # parse request data
            filter_data: dict = {
                k: v[0] if type(v) is list and len(v) == 1 else v
                for k, v in dict(request.data).items()
            }

            serializer: serializers.Serializer = FilmFilterSerializer(data=filter_data)
            serializer.is_valid(raise_exception=True)
            validated_data: dict = serializer.validated_data

            film_name: str = filter_data.get("film_name", None)
            director_name: str = filter_data.get("actor_name", None)
            actor_name: str = filter_data.get("director_name", None)
            film_genre: str = filter_data.get("genre", None)
            film_description: str = filter_data.get("description", None)
            min_release: str = filter_data.get("min_release", None)
            max_release: str = filter_data.get("max_release", None)
            min_rating: float = filter_data.get("min_rating", None)
            max_rating: float = filter_data.get("max_rating", None)

            # String Filters
            use_union: bool = True
            use_string_filter: bool = False
            if use_union:
                string_queryset: QuerySet = Film.objects.none()  # empty Film queryset
            else:
                string_queryset: QuerySet = Film.objects.all()

            if film_name is not None and not film_name == "":
                use_string_filter = True
                film_name_queryset: QuerySet = self.queryset.filter(
                    name__icontains=film_name
                )
                if use_union:
                    string_queryset = string_queryset.union(film_name_queryset)
                else:
                    string_queryset = string_queryset.intersection(film_name_queryset)

            if director_name is not None and not director_name == "":
                use_string_filter = True
                dir_name_queryset: QuerySet = self.queryset.filter(
                    director_id__name__icontains=director_name
                )
                if use_union:
                    string_queryset = string_queryset.union(dir_name_queryset)
                else:
                    string_queryset = string_queryset.intersection(dir_name_queryset)

            if actor_name is not None and not actor_name == "":
                use_string_filter = True
                actor_name_queryset: QuerySet = self.queryset.filter(
                    cast__name__icontains=actor_name
                )
                if use_union:
                    string_queryset = string_queryset.union(actor_name_queryset)
                else:
                    string_queryset = string_queryset.intersection(actor_name_queryset)

            if film_genre is not None and not film_genre == "":
                use_string_filter = True
                genre_queryset: QuerySet = self.queryset.filter(
                    genre__icontains=film_genre
                )
                if use_union:
                    string_queryset = string_queryset.union(genre_queryset)
                else:
                    string_queryset = string_queryset.intersection(genre_queryset)

            if film_description is not None and not film_description == "":
                use_string_filter = True
                description_queryset: QuerySet = self.queryset.filter(
                    description__icontains=film_description
                )
                if use_union:
                    string_queryset = string_queryset.union(description_queryset)
                else:
                    string_queryset = string_queryset.intersection(description_queryset)

            if not use_string_filter:
                string_queryset = self.queryset.all()

            # Filter films by release year
            relase_queryset: QuerySet = self.queryset.all()
            if min_release is not None and not min_release == "":
                min_date: datetime.datetime = validated_data.get("min_release")
                relase_queryset = relase_queryset.filter(release__gte=min_date.date())

            if max_release is not None and not max_release == "":
                max_date: datetime.datetime = validated_data.get("max_release")
                relase_queryset = relase_queryset.filter(release__lte=max_date.date())

            # Filter films by average rating
            rating_queryset: QuerySet = self.queryset.all()
            if min_rating is not None and not min_rating == "":
                min_value: int = validated_data.get("min_rating")
                # Annotate each film with its average rating
                rating_queryset = rating_queryset.annotate(
                    avg_rating=Avg(
                        Case(
                            When(reviews__rating__isnull=True, then=Value(0)),
                            default="reviews__rating",
                        )
                    )
                )
                rating_queryset = rating_queryset.filter(avg_rating__gte=min_value)

            if max_rating is not None and not max_rating == "":
                max_value: int = validated_data.get("max_rating")
                # If not already annotated, annotate each film with its average rating
                if min_rating is None or min_release == "":
                    rating_queryset = rating_queryset.annotate(
                        avg_rating=Avg(
                            Case(
                                When(reviews__rating__isnull=True, then=Value(0)),
                                default="reviews__rating",
                            )
                        )
                    )
                rating_queryset = rating_queryset.filter(avg_rating__lte=max_value)

            processed_rating_queryset: BaseManager[Film] = self.queryset.filter(
                id__in=rating_queryset
            )

            final_queryset: QuerySet = self.queryset.all()
            final_queryset = final_queryset.intersection(string_queryset)
            final_queryset = final_queryset.intersection(relase_queryset)
            final_queryset = final_queryset.intersection(processed_rating_queryset)
            serializer = FilmSerializer(final_queryset, many=True)

            response = Response(
                status=status.HTTP_200_OK,
                data={"films": serializer.data},
            )

        except ValidationError as error:
            response = Response(
                {"detail": error.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return response


class FilmDetailView(generics.RetrieveAPIView):
    queryset: BaseManager[Film] = Film.objects.all()

    def get_object(self, value: int) -> Film:
        try:
            film: Film = Film.objects.get(pk=value)
        except Film.DoesNotExist:
            film = None
            raise ValidationError("Film not found.")
        return film

    def get(self, request: Request, id: int) -> Response:
        response: Response

        try:
            film: Film = self.get_object(id)
            serializer: serializers.Serializer = FilmSerializer(film)
            response = Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as error:
            response = Response(
                {"detail": error.message},
                status=status.HTTP_404_NOT_FOUND,
            )

        return response


class FilmReviewsView(generics.ListAPIView):
    queryset: BaseManager[Review] = Review.objects.all()

    def get_object(self, value: int) -> Film:
        try:
            film: Film = Film.objects.get(pk=value)
        except Film.DoesNotExist:
            film = None
            raise ObjectDoesNotExist("Film not found.")
        return film

    def get(self, request: Request, id: int) -> Response:
        response: Response
        try:
            film: Film = self.get_object(id)
            reviews: BaseManager[Review] = self.queryset.filter(film_id=film)

            # Create response
            review_serializer: ReviewSerializer = ReviewSerializer(reviews, many=True)
            response = Response(
                {"reviews": review_serializer.data},
                status=status.HTTP_200_OK,
            )

        except ValidationError as error:
            response = Response(
                {"detail": error.message}, status=status.HTTP_400_BAD_REQUEST
            )
        except ObjectDoesNotExist as error:
            response = Response(
                {"detail": str(error)}, status=status.HTTP_404_NOT_FOUND
            )

        return response


class PostReviewView(generics.CreateAPIView):
    serializer_class: type = ReviewSerializer

    def get_object(self) -> AbstractBaseUser:
        """Overwrite method to get the authenticated user object"""
        try:
            session_key: str = self.request.COOKIES.get("session")
            user: AbstractBaseUser = Token.objects.get(key=session_key).user
        except ObjectDoesNotExist:
            raise PermissionDenied("session cookie missing or not valid")
        return user

    def post(self, request: Request) -> Response:

        response: Response

        # form: ModelForm = PostReviewForm(request.data, instance=user)

        try:
            # parse request data
            data: dict = {
                k: v[0] if type(v) is list and len(v) == 1 else v
                for k, v in dict(request.data).items()
            }
            # Get authenticated user & request data
            user: User = self.get_object()
            review_data: dict = dict()
            review_data["rating"] = data.get("rating", None)
            review_data["content"] = data.get("content", None)
            review_data["film_id"] = data.get("film_id", None)
            review_data["user_id"] = user.id

            # Validate and save review
            review_serializer: serializers.Serializer = ReviewSerializer(
                data=review_data  # review_data
            )
            review_serializer.is_valid(raise_exception=True)
            review_serializer.save()

            # Create response
            response = Response(
                {"detail": "Film review successfully posted."},
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as error:
            response = Response(
                {"detail": error.message}, status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError:
            response = Response(
                {"detail": "User can only post one review about each film."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PermissionDenied as error:
            response = Response(
                {"detail": str(error)}, status=status.HTTP_401_UNAUTHORIZED
            )

        return response


class RetrieveReviewsView(generics.RetrieveAPIView):
    queryset: BaseManager[Review] = Review.objects.all()

    def get_object(self) -> AbstractBaseUser:
        """Overwrite method to get the authenticated user object"""
        try:
            session_key: str = self.request.COOKIES.get("session")
            user: AbstractBaseUser = Token.objects.get(key=session_key).user
        except ObjectDoesNotExist:
            raise PermissionDenied("session cookie missing or not valid")
        return user

    def get(self, request: Request) -> Response:
        response: Response
        try:
            user: User = self.get_object()
            reviews: BaseManager[Review] = self.queryset.filter(user_id=user)

            # Create response
            review_serializer: ReviewSerializer = ReviewSerializer(reviews, many=True)
            response = Response(
                {"reviews": review_serializer.data},
                status=status.HTTP_200_OK,
            )

        except ValidationError as error:
            response = Response(
                {"detail": error.message}, status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as error:
            response = Response(
                {"detail": str(error)}, status=status.HTTP_401_UNAUTHORIZED
            )

        return response


class DeleteReviewView(generics.DestroyAPIView):
    serializer_class: type = DeleteReviewSerializer

    def get_object(self) -> AbstractBaseUser:
        """Overwrite method to get the authenticated user object"""
        try:
            session_key: str = self.request.COOKIES.get("session")
            user: AbstractBaseUser = Token.objects.get(key=session_key).user
        except ObjectDoesNotExist:
            raise PermissionDenied("session cookie missing or not valid")
        return user

    def post(self, request: Request) -> Response:

        response: Response
        try:
            # parse request data
            data: dict = {
                k: v[0] if type(v) is list and len(v) == 1 else v
                for k, v in dict(request.data).items()
            }
            # Verify that the provided ID is numeric
            review_id: int = data.get("review_id", None)
            if review_id is None or review_id == "":
                raise ValidationError("Review ID required.")
            try:
                review_id = int(review_id)
            except ValueError:
                raise ValidationError("Review ID must be an integer")

            # Verify that the provided review ID corresponds to an existing review
            # of the current logged user
            try:
                review: Review = Review.objects.get(id=review_id)
            except Review.DoesNotExist:
                raise ValidationError(
                    "Provided review ID does not match any existing review."
                )
            user: User = self.get_object()
            allowed: bool = review.user_id.id == user.id
            if not allowed:
                raise ValidationError(
                    "Unauthorized to delete an unauthenticated user's post."
                )

            review.delete()

            # Create response
            response = Response(
                {"detail": "Film review successfully deleted."},
                status=status.HTTP_202_ACCEPTED,
            )

        except ValidationError as error:
            response = Response(
                {"detail": error.message}, status=status.HTTP_400_BAD_REQUEST
            )
        except ObjectDoesNotExist as error:
            response = Response(
                {"detail": error.message}, status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as error:
            response = Response(
                {"detail": str(error)}, status=status.HTTP_401_UNAUTHORIZED
            )

        return response


class AggregateDirectorView(generics.CreateAPIView):
    serializer_class: type = DirectorSerializer

    def post(self, request: Request) -> Response:
        response: Response
        with transaction.atomic():  # Ensure all or nothing persistence
            try:
                # parse request data
                director_data: dict = {
                    k: v[0] if type(v) is list and len(v) == 1 else v
                    for k, v in dict(request.data).items()
                }
                # serialize director
                director_serializer = DirectorSerializer(data=director_data)
                director_serializer.is_valid(raise_exception=True)
                director: Director
                director, _ = Director.objects.get_or_create(**director_data)
                director.save()

                response: Response = Response(
                    {"detail": "Director added succesfully"},
                    status=status.HTTP_201_CREATED,
                )

            except ValidationError as error:
                response = Response(
                    {"detail": error.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return response


class DeleteDirectorView(generics.DestroyAPIView):

    def get_serializer_class(self) -> serializers.Serializer:
        return DeleteDirectorSerializer

    def get_object(self) -> Director:
        """Overwrite method to get the authenticated user object"""
        director_id: str = self.request.data.get("id")
        director: Director = Director.objects.get(id=director_id)
        return director

    def post(self, request: Request) -> Response:
        response: Response
        with transaction.atomic():  # Ensure all or nothing persistence
            try:
                # parse request data
                director_data: dict = {
                    k: v[0] if type(v) is list and len(v) == 1 else v
                    for k, v in dict(request.data).items()
                }
                # Get the director id from the request data
                director_id: int = director_data.get("id")
                if not director_id:
                    raise ValidationError("Director ID must be provided")
                try:
                    director_id = int(director_id)
                except ValueError:
                    raise ValidationError("Director ID must be an integer")

                # Get the director instance
                director: Director = Director.objects.get(id=director_id)

                # Delete the director
                director.delete()

                response = Response(
                    {"detail": "Director deleted successfully"},
                    status=status.HTTP_204_NO_CONTENT,
                )

            except Director.DoesNotExist:
                response = Response(
                    {"detail": "Director not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except ValidationError as error:
                response = Response(
                    {"detail": error.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return response

    def delete(self, request: Request) -> Response:

        response: Response = Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"detail": "DELETE method not supported. Use PUT instead."},
        )

        return response


class AggregateActorView(generics.CreateAPIView):
    serializer_class: type = ActorSerializer

    def post(self, request: Request) -> Response:
        response: Response
        with transaction.atomic():  # Ensure all or nothing persistence
            try:
                # parse request data
                actor_data: dict = {
                    k: v[0] if type(v) is list and len(v) == 1 else v
                    for k, v in dict(request.data).items()
                }
                # serialize actor
                actor_serializer = ActorSerializer(data=actor_data)
                actor_serializer.is_valid(raise_exception=True)
                actor: Actor
                actor, _ = Actor.objects.get_or_create(**actor_data)
                actor.save()

                response: Response = Response(
                    {"detail": "Actor added succesfully"},
                    status=status.HTTP_201_CREATED,
                )

            except ValidationError as error:
                response = Response(
                    {"detail": error.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return response


class DeleteActorView(generics.DestroyAPIView):

    def get_serializer_class(self) -> serializers.Serializer:
        return DeleteActorSerializer

    def get_object(self) -> Actor:
        """Overwrite method to get the authenticated user object"""
        actor_id: str = self.request.data.get("id")
        actor: Actor = Actor.objects.get(name=actor_id)
        return actor

    def post(self, request: Request) -> Response:
        response: Response
        with transaction.atomic():  # Ensure all or nothing persistence
            try:
                # parse request data
                actor_data: dict = {
                    k: v[0] if type(v) is list and len(v) == 1 else v
                    for k, v in dict(request.data).items()
                }
                # Get the director name from the request data
                actor_id: str = actor_data.get("id")
                if not actor_id:
                    raise ValidationError("Actor ID must be provided")
                try:
                    actor_id = int(actor_id)
                except ValueError:
                    raise ValidationError("Actor ID must be an integer")

                # Get the actor instance
                actor: Actor = Actor.objects.get(id=actor_id)

                # Delete the actor
                actor.delete()

                response = Response(
                    {"detail": "Actor deleted successfully"},
                    status=status.HTTP_204_NO_CONTENT,
                )

            except Actor.DoesNotExist:
                response = Response(
                    {"detail": "Actor not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except ValidationError as error:
                response = Response(
                    {"detail": error.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return response

    def delete(self, request: Request) -> Response:

        response: Response = Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"detail": "DELETE method not supported. Use PUT instead."},
        )

        return response


class AggregateFilmView(generics.CreateAPIView):
    serializer_class: type = FilmSerializer

    def post(self, request: Request) -> Response:

        with transaction.atomic():  # Ensure all or nothing persistence

            try:
                # parse request data
                film_data: dict = {
                    k: (
                        v[0]
                        if type(v) is list and len(v) == 1 and not k == "cast"
                        else v
                    )
                    for k, v in dict(request.data).items()
                }

                # Handle Director
                if "director" not in film_data.keys():
                    raise ValidationError("director field must be provided")
                director_name: str = film_data.pop("director", {})
                director_data: dict[str, str] = {"name": director_name}
                director_serializer = DirectorSerializer(data=director_data)
                # director_serializer.is_valid(raise_exception=True)
                director_serializer.validate_fields(data=director_data)
                director: Director
                created: bool
                director, created = Director.objects.get_or_create(**director_data)
                if created:
                    director.save()

                # Handle Cast (Actors)
                if "cast" not in film_data.keys():
                    raise ValidationError("cast field must be provided")
                cast_names: list[str] = film_data.pop("cast", [])
                if type(cast_names) is not list:
                    raise ValidationError("cast must be a list of names (list[string])")
                actors: list[Actor] = []  # List to store Actor instances
                for name in cast_names:
                    if not type(name) is str:
                        raise ValidationError(
                            "cast must be a list of names (list[string])"
                        )
                    actor_data: dict[str, str] = {"name": name}
                    actor_serializer = ActorSerializer(data=actor_data)
                    actor_serializer.validate_fields(data=actor_data)
                    actor: Actor
                    created: bool
                    actor, created = Actor.objects.get_or_create(**actor_data)
                    actor.save()
                    actors.append(actor)  # Add the Actor instance to the list

                # Handle Film
                # film_data.pop("image_url")
                film_data["director_id"] = director.id  # director ID
                film_data["cast"] = [actor.id for actor in actors]  # list of actor IDs
                film_serializer = FilmSerializer(data=film_data)
                film_serializer.is_valid(raise_exception=True)
                film: Film
                created: bool = False
                film_name: str = film_data.get("name")
                try:
                    film = Film.objects.get(name=film_name)
                    for attr, value in film_serializer.validated_data.items():
                        if attr == "cast":
                            film.cast.set(value)
                        else:
                            setattr(film, attr, value)
                    film.save()
                except Film.DoesNotExist:
                    created = True
                    film = film_serializer.save()

                message: str = f"Film {'added' if created else 'updated'} successfully"
                response: Response = Response(
                    {"detail": message},
                    status=status.HTTP_201_CREATED,
                )

            except ValidationError as error:
                response = Response(
                    {"detail": error.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Return serialized data (customize as needed)
            return response


class DeleteFilmView(generics.DestroyAPIView):

    def get_serializer_class(self) -> serializers.Serializer:
        return DeleteFilmSerializer

    def get_object(self) -> AbstractBaseUser:
        """Overwrite method to get the authenticated user object"""
        film_name: str = self.request.data.get("name")
        film: Film = Film.objects.get(name=film_name)
        return film

    def post(self, request: Request) -> Response:
        response: Response
        with transaction.atomic():  # Ensure all or nothing persistence
            try:
                # parse request data
                film_data: dict = {
                    k: v[0] if type(v) is list and len(v) == 1 else v
                    for k, v in dict(request.data).items()
                }
                # Get the director name from the request data
                film_name: str = film_data.get("name")
                if not film_name:
                    raise ValidationError("Film name must be provided")
                if type(film_name) is not str:
                    raise ValidationError("Film name must be a string")

                # Get the director instance
                film: Film = Film.objects.get(name=film_name)

                # Delete the director
                film.delete()

                response = Response(
                    {"detail": "Film deleted successfully"},
                    status=status.HTTP_204_NO_CONTENT,
                )

            except Film.DoesNotExist:
                response = Response(
                    {"detail": "Film not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except ValidationError as error:
                response = Response(
                    {"detail": error.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return response

    def delete(self, request: Request) -> Response:

        response: Response = Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"detail": "DELETE method not supported. Use PUT instead."},
        )

        return response


# TODOS
# Add image saving logic (views + serializers + models) (OPTIONAL)
