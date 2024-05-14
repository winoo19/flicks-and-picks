from selenium import webdriver
from selenium.webdriver.common.by import By
from ..django_backend.apps.users.models import User, Review
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse


class TestRegisterPage(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("chromedriver.exe")
        self.driver.get(self.live_server_url + reverse("user_register"))

    def test_register(self):
        # Fill the form
        self.driver.find_element_by_id("username").send_keys("test_username")
        self.driver.find_element_by_id("email").send_keys("em@i.l")
        self.driver.find_element_by_id("password").send_keys("test_password")
        self.driver.find_element_by_id("password2").send_keys("test_password")
        self.driver.find_element_by_id("submit-button").click()

        # Check if the user is correctly created
        user = User.objects.get(username="test_username")
        self.assertEqual(user.email, "em@i.l")
        self.assertEqual(user.password, "test_password")
        self.assertTrue(user.professional)

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_login")
        )

    def test_back_button(self):
        self.driver.find_element_by_id("cancel-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(self.driver.current_url, self.live_server_url)

    def test_login_button(self):
        self.driver.find_element_by_id("login-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_login")
        )

    def tearDown(self):
        self.driver.quit()


class TestLoginPage(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("chromedriver.exe")
        self.driver.get(self.live_server_url + reverse("user_login"))

        # Create a user to test the login
        self.user = User.objects.create(
            username="test_username", email="em@i.l", password="test_password"
        )

    def test_login(self):
        # Fill the form
        self.driver.find_element_by_id("email").send_keys("em@i.l")
        self.driver.find_element_by_id("password").send_keys("test_password")
        self.driver.find_element_by_id("submit-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(self.driver.current_url, self.live_server_url)

        # Check if the user is correctly logged in
        # by checking if the user is in the session
        self.assertEqual(
            self.driver.get_cookie("sessionid")["value"], self.user.session_key
        )

    def test_back_button(self):
        self.driver.find_element_by_id("cancel-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(self.driver.current_url, self.live_server_url)

    def test_register_button(self):
        self.driver.find_element_by_id("register-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_register")
        )

    def tearDown(self):
        self.driver.quit()


class TestProfilePage(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("chromedriver.exe")

        # Create a user to test the profile
        self.user = User.objects.create(
            username="test_username", email="em@i.l", password="test_password"
        )

        # Log in the user by sending a request
        self.client.post(
            reverse("user_login"),
            {"username": "test_username", "password": "test_password"},
        )

        self.driver.get(self.live_server_url + reverse("user_info"))

    def test_logout(self):
        self.driver.find_element_by_id("logout-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(self.driver.current_url, self.live_server_url)

        # Check if the user is correctly logged out
        # by checking if the user is in the session
        self.assertIsNone(self.driver.get_cookie("sessionid"))

    def test_delete(self):
        self.driver.find_element_by_id("delete-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(self.driver.current_url, self.live_server_url)

        # Check if the user is correctly deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="test_username")

    def test_update(self):
        self.driver.find_element_by_id("update-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_update")
        )

    def test_back_button(self):
        self.driver.find_element_by_id("back-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(self.driver.current_url, self.live_server_url)

    def tearDown(self):
        self.driver.quit()


class TestUpdatePage(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("chromedriver.exe")

        # Create a user to test the update
        self.user = User.objects.create(
            username="test_username", email="em@i.l", password="test_password"
        )

        # Log in the user by sending a request
        self.client.post(
            reverse("user_login"),
            {"username": "test_username", "password": "test_password"},
        )

        self.driver.get(self.live_server_url + reverse("user_update"))

    def test_update(self):
        # Fill the form
        self.driver.find_element_by_id("id_email").send_keys("new_em@i.l")
        self.driver.find_element_by_id("id_password").send_keys("new_test_password")
        self.driver.find_element_by_id("id_password2").send_keys("new_test_password")
        self.driver.find_element_by_id("submit-button").click()

        # Check if the user is correctly updated
        user = User.objects.get(username="test_username")
        self.assertEqual(user.email, "new_em@i.l")
        self.assertEqual(user.password, "new_test_password")

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_info")
        )

    def test_back_button(self):
        self.driver.find_element_by_id("cancel-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_info")
        )


class TestInitialPage(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("chromedriver.exe")
        self.driver.get(self.live_server_url)

    def test_film_selection(self):
        films = self.driver.find_elements(by=By.CLASS_NAME, value="film-details")

        for film in films:
            film_id = film.get_attribute("id")
            film_title = film.find_element(by=By.ID, value="title")
            film_thumbnail = film.find_element(by=By.ID, value="thumbnail")

            # Check if the user is redirected to the correct page
            film_title.click()
            self.assertEqual(
                self.driver.current_url,
                self.live_server_url + reverse("film", args=[film_id]),
            )
            self.driver.back()

            # Check if the user is redirected to the correct page
            film_thumbnail.click()
            self.assertEqual(
                self.driver.current_url,
                self.live_server_url + reverse("film", args=[film_id]),
            )
            self.driver.back()

    def test_film_filter(self):
        search_bar = self.driver.find_element(by=By.ID, value="search")
        search_bar.send_keys("The Shawshank Redemption")

        films = self.driver.find_elements(by=By.CLASS_NAME, value="film-details")

        # Check if the film is correctly displayed
        self.assertEqual(len(films), 1)
        self.assertEqual(
            films[0].find_element(by=By.ID, value="title").text,
            "The Shawshank Redemption",
        )
        search_bar.clear()

        search_bar.send_keys("aaaaaabbbbbccccccNotARealFilm")
        films = self.driver.find_elements(by=By.CLASS_NAME, value="film-details")

        # Check that no film is displayed
        self.assertEqual(len(films), 0)

    def test_login_and_register_redirect(self):
        self.driver.find_element(by=By.ID, value="login-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_login")
        )

        self.driver.get(self.live_server_url)
        self.driver.find_element(by=By.ID, value="register-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_register")
        )

    def tearDown(self):
        self.driver.quit()


class TestFilmPage(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("chromedriver.exe")
        self.driver.get(self.live_server_url + reverse("film", args=[1]))
        self.user = User.objects.create(
            username="test_username", email="em@i.l", password="test_password"
        )
        self.client.post(
            reverse("user_login"),
            {"username": "test_username", "password": "test_password"},
        )

    def test_film_review(self):
        review = self.driver.find_element(by=By.ID, value="review")
        score = self.driver.find_element(by=By.ID, value="score")
        update_button = self.driver.find_element(by=By.ID, value="update-button")

        # Fill the form
        review.send_keys("test_review")
        score.send_keys("5")
        update_button.click()

        # Check if the review is correctly created in the database
        self.assertEqual(
            Review.objects.get(user=self.user, film_id=1).review, "test_review"
        )
        self.assertEqual(Review.objects.get(user=self.user, film_id=1).score, 5)

    def test_back_button(self):
        back_button = self.driver.find_element(by=By.ID, value="back-button")
        back_button.click()

        # Check if the user is redirected to the correct page
        self.assertEqual(self.driver.current_url, self.live_server_url)
