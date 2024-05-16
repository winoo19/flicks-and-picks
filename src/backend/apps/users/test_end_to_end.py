from selenium import webdriver
from selenium.webdriver.common.by import By

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from time import sleep, perf_counter


PROJECT_URL = "http://localhost:5173/"


class TestRegisterPage(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.driver = webdriver.Chrome()

    def setUp(self):
        super().setUp()

        if self.driver.current_url != PROJECT_URL + "register/":
            self.driver.get(PROJECT_URL + "register/")

    def test_register(self):
        user = str(int(perf_counter() * 100))

        # Fill the form
        self.driver.find_element(by=By.ID, value="username").send_keys(user)
        self.driver.find_element(by=By.ID, value="email").send_keys(
            f"{user}@{user}.com"
        )
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="password2").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()

        sleep(2)

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL + "login/?registered",
            "Register redirect failed in register page",
        )

    def test_back_button(self):
        self.driver.find_element(by=By.ID, value="cancel-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL,
            "Back button failed in register page",
        )

    def test_login_button(self):
        self.driver.find_element(by=By.ID, value="login-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL + "login",
            "Login button redirect failed in register page",
        )

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()


class TestLoginPage(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.driver = webdriver.Chrome()

    def setUp(self):
        super().setUp()

        self.user = str(int(perf_counter() * 100))

        # Register a user to test the login
        self.driver.get(PROJECT_URL + "register/")
        self.driver.find_element(by=By.ID, value="username").send_keys(self.user)
        self.driver.find_element(by=By.ID, value="email").send_keys(
            f"{self.user}@{self.user}.com"
        )
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="password2").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()
        sleep(2)

        self.driver.get(PROJECT_URL + "login/")

    def test_login(self):
        # Fill the form
        self.driver.find_element(by=By.ID, value="username").send_keys(self.user)
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()

        # Wait for the page to load
        sleep(3)

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, PROJECT_URL, "Login redirect failed in login page"
        )

    def test_back_button(self):
        self.driver.find_element(by=By.ID, value="cancel-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, PROJECT_URL, "Back button failed in login page"
        )

    def test_register_button(self):
        self.driver.find_element(by=By.ID, value="register-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL + "register",
            "Register button failed in login page",
        )

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()


class TestProfilePage(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.driver = webdriver.Chrome()

    def setUp(self):
        super().setUp()

        # Create a user to test the profile
        self.user = str(int(perf_counter() * 100))
        self.driver.get(PROJECT_URL + "register/")
        self.driver.find_element(by=By.ID, value="username").send_keys(self.user)
        self.driver.find_element(by=By.ID, value="email").send_keys(
            f"{self.user}@{self.user}.com"
        )
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="password2").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()
        sleep(3)

        # Log in the user
        self.driver.get(PROJECT_URL + "login/")
        self.driver.find_element(by=By.ID, value="username").send_keys(self.user)
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()
        sleep(3)

        self.driver.get(PROJECT_URL + "profile-app/profile/")

    def test_logout(self):
        sleep(10)
        self.driver.find_element(by=By.ID, value="logout-button").click()
        sleep(3)

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL,
            "Logout redirect failed in profile page",
        )

        # Check if the user is correctly logged out
        self.driver.get(PROJECT_URL + "profile-app/profile/")
        sleep(1)
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL,
            "Logout failed in profile page",
        )

    def test_delete(self):
        sleep(10)
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="unsubscribe-button").click()
        self.driver.switch_to.alert.accept()
        sleep(3)

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL,
            "Delete redirect failed in profile page",
        )

        # Check if the user is correctly deleted
        self.driver.get(PROJECT_URL + "login/")
        self.driver.find_element(by=By.ID, value="username").send_keys(self.user)
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()
        sleep(3)
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL + "login/",
            "Delete failed in profile page",
        )

    def tearDown(self):
        super().tearDown()

        # Log out the user
        self.driver.get(PROJECT_URL + "profile-app/profile/")
        sleep(3)
        if self.driver.current_url == PROJECT_URL + "profile-app/profile/":
            self.driver.find_element(by=By.ID, value="logout-button").click()
            sleep(3)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()


class TestUpdatePage(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.driver = webdriver.Chrome()

    def setUp(self):
        super().setUp()

        # Create a user to test the profile
        self.user = str(int(perf_counter() * 100))

        self.driver.get(PROJECT_URL + "register/")
        self.driver.find_element(by=By.ID, value="username").send_keys(self.user)
        self.driver.find_element(by=By.ID, value="email").send_keys(
            f"{self.user}@{self.user}.com"
        )
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="password2").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()
        sleep(3)

        # Log in the user
        self.driver.get(PROJECT_URL + "login/")
        self.driver.find_element(by=By.ID, value="username").send_keys(self.user)
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()
        sleep(3)

        self.driver.get(PROJECT_URL + "profile-app/profile-update/")

    def test_update(self):
        sleep(5)
        # Fill the form
        self.driver.find_element(by=By.ID, value="email").clear()
        self.driver.find_element(by=By.ID, value="email").send_keys(
            "newemail@email.com"
        )

        self.driver.find_element(by=By.ID, value="current-password").send_keys(
            "Password1"
        )
        self.driver.find_element(by=By.ID, value="new-password").send_keys("Password2")
        self.driver.find_element(by=By.ID, value="update-button").click()

        sleep(3)

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL,
            "Update redirect failed in update page",
        )

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()


class TestInitialPage(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.driver = webdriver.Chrome()

    def setUp(self):
        super().setUp()

        self.driver.get(PROJECT_URL)

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
                PROJECT_URL + f"film/{film_id}/",
                f"Title redirect failed in initial page for film {film_id}",
            )
            self.driver.back()

            # Check if the user is redirected to the correct page
            film_thumbnail.click()
            self.assertEqual(
                self.driver.current_url,
                PROJECT_URL + f"film/{film_id}/",
                f"Thumbnail redirect failed in initial page for film {film_id}",
            )
            self.driver.back()

    def test_film_filter(self):
        search_bar = self.driver.find_element(by=By.ID, value="search")
        search_bar.send_keys("The Shawshank Redemption")

        sleep(3)
        films = self.driver.find_elements(by=By.CLASS_NAME, value="film-details")

        # Check if the film is correctly displayed
        self.assertEqual(
            len(films),
            1,
            f"Search bar filter failed, should have displayed 1 film",
        )
        self.assertEqual(
            films[0].find_element(by=By.ID, value="title").text,
            "The Shawshank Redemption",
            "Search bar filter failed, should have displayed The Shawshank Redemption",
        )
        search_bar.clear()

        search_bar.send_keys("aaaaaabbbbbccccccNotARealFilm")
        sleep(1)

        films = self.driver.find_elements(by=By.CLASS_NAME, value="film-details")

        # Check that no film is displayed
        self.assertEqual(
            len(films), 0, "Search bar filter failed, should have displayed no film"
        )

    def test_login_and_register_redirect(self):
        self.driver.find_element(by=By.ID, value="login-button").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL + "login",
            "Login button redirect failed in initial page",
        )

        self.driver.get(PROJECT_URL)

        # Wait for the page to load
        button = self.driver.find_element(by=By.ID, value="register-button")
        button.click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL + "register",
            "Register button redirect failed in initial page",
        )

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()


class TestFilmPage(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.driver = webdriver.Chrome()

    def setUp(self):
        super().setUp()

    def test_film_review(self):
        # Register a user to test the review
        user = str(int(perf_counter() * 100))

        self.driver.get(PROJECT_URL + "register/")
        self.driver.find_element(by=By.ID, value="username").send_keys(user)
        self.driver.find_element(by=By.ID, value="email").send_keys(
            f"{user}@{user}.com"
        )
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="password2").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()
        sleep(3)
        self.driver.get(PROJECT_URL + "login/")
        self.driver.find_element(by=By.ID, value="username").send_keys(user)
        self.driver.find_element(by=By.ID, value="password").send_keys("Password1")
        self.driver.find_element(by=By.ID, value="submit-button").click()
        sleep(3)

        self.driver.get(PROJECT_URL + "film/1/")
        sleep(5)

        review = self.driver.find_element(by=By.ID, value="review")
        score = self.driver.find_element(by=By.ID, value="score")
        update_button = self.driver.find_element(by=By.ID, value="update-button")

        # Fill the form
        review.send_keys("test_review")
        score.send_keys("5")
        update_button.click()

        # Check redirection
        self.assertEqual(
            self.driver.current_url,
            PROJECT_URL,
            "Review redirect failed in film page",
        )

    def test_back_button(self):
        self.driver.get(PROJECT_URL + "film/1/")
        sleep(5)

        back_button = self.driver.find_element(by=By.ID, value="back-button")
        back_button.click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, PROJECT_URL, "Back button failed in film page"
        )

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
