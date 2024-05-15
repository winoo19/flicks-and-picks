from django.test import SimpleTestCase
from django.urls import reverse, resolve


"""
user_urls: list[path] = [
    path("user/register/", UserRegisterView.as_view(), name="user_register"),
    path("user/login/", UserLoginView.as_view(), name="user_login"),
    path("user/profile-info/", UserProfileInfoView.as_view(), name="user_info"),
    path("user/profile-update/", UserProfileUpdateView.as_view(), name="user_update"),
    path("user/logout/", UserLogoutView.as_view(), name="user_logout"),
    path("user/delete/", UserDeleteView.as_view(), name="user_delete"),
    path("user/add-review/", PostReviewView.as_view(), name="user_add_review"),
    path("user/delete-review/", DeleteReviewView.as_view(), name="user_del_review"),
    path("user/history/", RetrieveReviewsView.as_view(), name="user_history"),
]

site_urls: list[path] = [
    path("films/", FilterFilmsView.as_view(), name="film_filter"),
    path("film/<int:id>/", FilmDetailView.as_view(), name="film_info"),
    path("film/<int:id>/reviews/", FilmReviewsView.as_view(), name="film_reviews"),
]

admin_urls: list[path] = [
    path("admin/", admin.site.urls),
    path("site-admin/add-director/", AggregateDirectorView.as_view(), name="add_dir"),
    path("site-admin/add-actor/", AggregateActorView.as_view(), name="add_actor"),
    path("site-admin/add-film/", AggregateFilmView.as_view(), name="add_film"),
    path("site-admin/delete-director/", DeleteDirectorView.as_view(), name="del_dir"),
    path("site-admin/delete-actor/", DeleteActorView.as_view(), name="del_actor"),
    path("site-admin/delete-film/", DeleteFilmView.as_view(), name="del_film"),
]
"""


class TestUrls(SimpleTestCase):
    def test_user_register_url(self) -> None:
        url: str = reverse("user_register")
        self.assertEqual(resolve(url).func.view_class.__name__, "UserRegisterView")

    def test_user_login_url(self) -> None:
        url: str = reverse("user_login")
        self.assertEqual(resolve(url).func.view_class.__name__, "UserLoginView")

    def test_user_info_url(self) -> None:
        url: str = reverse("user_info")
        self.assertEqual(resolve(url).func.view_class.__name__, "UserProfileInfoView")

    def test_user_update_url(self) -> None:
        url: str = reverse("user_update")
        self.assertEqual(resolve(url).func.view_class.__name__, "UserProfileUpdateView")

    def test_user_logout_url(self) -> None:
        url: str = reverse("user_logout")
        self.assertEqual(resolve(url).func.view_class.__name__, "UserLogoutView")

    def test_user_delete_url(self) -> None:
        url: str = reverse("user_delete")
        self.assertEqual(resolve(url).func.view_class.__name__, "UserDeleteView")

    def test_user_add_review_url(self) -> None:
        url: str = reverse("user_add_review")
        self.assertEqual(resolve(url).func.view_class.__name__, "PostReviewView")

    def test_user_del_review_url(self) -> None:
        url: str = reverse("user_del_review")
        self.assertEqual(resolve(url).func.view_class.__name__, "DeleteReviewView")

    def test_user_history_url(self) -> None:
        url: str = reverse("user_history")
        self.assertEqual(resolve(url).func.view_class.__name__, "RetrieveReviewsView")

    def test_film_filter_url(self) -> None:
        url: str = reverse("film_filter")
        self.assertEqual(resolve(url).func.view_class.__name__, "FilterFilmsView")

    def test_film_info_url(self) -> None:
        url: str = reverse("film_info", args=[1])
        self.assertEqual(resolve(url).func.view_class.__name__, "FilmDetailView")

    def test_film_reviews_url(self) -> None:
        url: str = reverse("film_reviews", args=[1])
        self.assertEqual(resolve(url).func.view_class.__name__, "FilmReviewsView")

    def test_add_dir_url(self) -> None:
        url: str = reverse("add_dir")
        self.assertEqual(resolve(url).func.view_class.__name__, "AggregateDirectorView")

    def test_add_actor_url(self) -> None:
        url: str = reverse("add_actor")
        self.assertEqual(resolve(url).func.view_class.__name__, "AggregateActorView")

    def test_add_film_url(self) -> None:
        url: str = reverse("add_film")
        self.assertEqual(resolve(url).func.view_class.__name__, "AggregateFilmView")

    def test_del_dir_url(self) -> None:
        url: str = reverse("del_dir")
        self.assertEqual(resolve(url).func.view_class.__name__, "DeleteDirectorView")

    def test_del_actor_url(self) -> None:
        url: str = reverse("del_actor")
        self.assertEqual(resolve(url).func.view_class.__name__, "DeleteActorView")

    def test_del_film_url(self) -> None:
        url: str = reverse("del_film")
        self.assertEqual(resolve(url).func.view_class.__name__, "DeleteFilmView")

    def test_admin_url(self) -> None:
        url: str = reverse("admin:index")
        self.assertEqual(resolve(url).func.__name__, "index")
