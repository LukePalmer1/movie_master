from django.test import TestCase

# Create your tests here.

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from movie_app.models import Movie, UserProfile, Rating
from movie_app.forms import UserForm, UserProfileForm








class MovieModelTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            movieID=1,
            title="Movie",
            release_date="2000-01-01",
            overview="A movie or something",
            poster_path="http://example.com/Movie.jpg",
            average_rating=9.0
        )

    def test_movie_str(self):
        self.assertEqual(str(self.movie), "Movie")


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = UserProfile.objects.create(user=self.user, biography="movies")

    def test_profile_str(self):
        self.assertEqual(str(self.profile), "testuser")


class RatingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = UserProfile.objects.create(user=self.user, biography="movies")
        self.movie = Movie.objects.create(
            movieID=1,
            title="Movie",
            release_date="2000-01-01",
            overview="A movie or something",
            poster_path="http://example.com/Movie.jpg",
            average_rating=9.0
        )
        self.rating = Rating.objects.create(user_profile=self.profile, movie=self.movie, rating=10, review="Amazing!")

    def test_rating_str(self):
        expected = f"{self.profile}'s review of {self.movie}"
        self.assertEqual(str(self.rating), expected)









class UserFormTest(TestCase):
    def test_valid_user_form(self):
        data = {'username': 'newuser', 'email': 'ua@example.com', 'password': 'password'}
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_user_form(self):
        data = {'username': '', 'email': 'ua@example.com', 'password': 'password'}
        form = UserForm(data=data)
        self.assertFalse(form.is_valid())


class UserProfileFormTest(TestCase):
    def test_valid_profile_form(self):
        form = UserProfileForm(data={'biography': 'movies'})
        self.assertTrue(form.is_valid())










class MovieAppViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = UserProfile.objects.create(user=self.user, biography="movies")
        self.movie = Movie.objects.create(
            movieID=1,
            title="Movie",
            release_date="2000-01-01",
            overview="A movie or something",
            poster_path="http://example.com/Movie.jpg",
            average_rating=9.0
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('movie_app:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie_app/login.html')

    def test_signup_view_get(self):
        response = self.client.get(reverse('movie_app:sign_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie_app/signup.html')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('movie_app:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie_app/dashboard.html')


def test_all_movies_view(self):
    response = self.client.get(reverse('movie_app:all_movies'))
    self.assertEqual(response.status_code, 200)
    self.assertIn(self.movie, response.context['movies'])



def test_view_profile(self):
    self.client.login(username='testuser', password='password')
    response = self.client.get(reverse('movie_app:view_profile', args=[self.user.username]))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'movie_app/profile.html')
    self.assertEqual(response.context['profile'].biography, "movies")