from selenium import webdriver
from ..models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse


class TestRegisterPage(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("chromedriver.exe")
        self.driver.get(self.live_server_url + reverse("user_register"))

    def test_register(self):
        # Fill the form
        self.driver.find_element_by_id("id_username").send_keys("test_username")
        self.driver.find_element_by_id("id_email").send_keys("em@i.l")
        self.driver.find_element_by_id("id_password").send_keys("test_password")
        self.driver.find_element_by_id("id_professional").click()
        self.driver.find_element_by_id("submit").click()

        # Check if the user is correctly created
        user = User.objects.get(username="test_username")
        self.assertEqual(user.email, "em@i.l")
        self.assertEqual(user.password, "test_password")
        self.assertTrue(user.professional)

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
        self.driver.find_element_by_id("id_username").send_keys("test_username")
        self.driver.find_element_by_id("id_password").send_keys("test_password")
        self.driver.find_element_by_id("submit").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("film_filter")
        )

        # Check if the user is correctly logged in
        # by checking if the user is in the session
        self.assertEqual(
            self.driver.get_cookie("sessionid")["value"], self.user.session_key
        )

    def tearDown(self):
        self.driver.quit()


class TestProfilePage(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("chromedriver.exe")
        self.driver.get(self.live_server_url + reverse("user_info"))

        # Create a user to test the profile
        self.user = User.objects.create(
            username="test_username", email="em@i.l", password="test_password"
        )

        # Log in the user by sending a request
        self.client.post(
            reverse("user_login"),
            {"username": "test_username", "password": "test_password"},
        )

    def test_logout(self):
        self.driver.find_element_by_id("logout").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_login")
        )

        # Check if the user is correctly logged out
        # by checking if the user is in the session
        self.assertIsNone(self.driver.get_cookie("sessionid"))

    def test_delete(self):
        self.driver.find_element_by_id("delete").click()

        # Check if the user is redirected to the correct page
        self.assertEqual(
            self.driver.current_url, self.live_server_url + reverse("user_login")
        )

        # Check if the user is correctly deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="test_username")

    def test_update(self):
        # Fill the form
        self.driver.find_element_by_id("id_email").send_keys("new_em@i.l")
        self.driver.find_element_by_id("id_password").send_keys("new_test_password")
        self.driver.find_element_by_id("submit").click()

        # Check if the user is correctly updated
        user = User.objects.get(username="test_username")
        self.assertEqual(user.email, "new_em@i.l")
        self.assertEqual(user.password, "new_test_password")

    def tearDown(self):
        self.driver.quit()
