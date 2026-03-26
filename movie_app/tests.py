
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from movie_app.models import Movie, UserProfile, Rating, Follow
from movie_app.forms import UserForm, UserProfileForm
from django.db import IntegrityError

# Create your tests here.









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

    def test_movie_creation(self):
        self.assertEqual(self.movie.movieID, 1)
        self.assertEqual(self.movie.title, "Movie")
        self.assertEqual(self.movie.release_date, "2000-01-01")
        self.assertEqual(self.movie.average_rating, 9.0)

    def test_movie_unique_id(self):
        with self.assertRaises(Exception):
            Movie.objects.create(
                movieID=1,
                title="Different Movie",
                release_date="2001-01-01",
                overview="Another movie",
                poster_path="http://example.com/movie2.jpg",
                average_rating=8.0
            )

    def test_movie_default_rating(self):
        movie = Movie.objects.create(
            movieID=2,
            title="Test Movie",
            release_date="2020-01-01",
            overview="Test",
            poster_path="http://example.com/test.jpg"
        )
        self.assertEqual(movie.average_rating, 0)

    def test_movie_queryset_order(self):
        Movie.objects.create(
            movieID=3,
            title="Zebra Movie",
            release_date="2019-01-01",
            overview="Z movie",
            poster_path="http://example.com/z.jpg"
        )
        movies = Movie.objects.all()
        self.assertEqual(movies.count(), 2)


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = UserProfile.objects.create(user=self.user, biography="movies")

    def test_profile_str(self):
        self.assertEqual(str(self.profile), "testuser")

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.biography, "movies")

    def test_profile_one_to_one_relationship(self):
        user2 = User.objects.create_user(username="user2", password="password")
        profile2 = UserProfile.objects.create(user=user2, biography="user2")
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(profile2.user, user2)
        self.assertEqual(UserProfile.objects.get(user=self.user), self.profile)
        self.assertEqual(UserProfile.objects.get(user=user2), profile2)

    def test_profile_watch_list_add_movie(self):
        movie = Movie.objects.create(
            movieID=10,
            title="Test Movie",
            release_date="2020-01-01",
            overview="Test",
            poster_path="http://example.com/test.jpg"
        )
        self.profile.watch_list.add(movie)
        self.assertIn(movie, self.profile.watch_list.all())

    def test_profile_watch_list_multiple_movies(self):
        movie1 = Movie.objects.create(
            movieID=11,
            title="Movie 1",
            release_date="2020-01-01",
            overview="Test",
            poster_path="http://example.com/1.jpg"
        )
        movie2 = Movie.objects.create(
            movieID=12,
            title="Movie 2",
            release_date="2020-01-01",
            overview="Test",
            poster_path="http://example.com/2.jpg"
        )
        self.profile.watch_list.add(movie1, movie2)
        self.assertEqual(self.profile.watch_list.count(), 2)

    def test_profile_can_be_followed(self):
        user2 = User.objects.create_user(username="user2", password="password")
        profile2 = UserProfile.objects.create(user=user2, biography="user2 bio")
        follow = Follow.objects.create(follower_user=self.profile, follows_user=profile2)
        self.assertEqual(follow.follower_user, self.profile)
        self.assertEqual(follow.follows_user, profile2)

    def test_multiple_follow_relationships(self):
        user2 = User.objects.create_user(username="user2", password="password")
        user3 = User.objects.create_user(username="user3", password="password")
        profile2 = UserProfile.objects.create(user=user2, biography="user2")
        profile3 = UserProfile.objects.create(user=user3, biography="user3")
        Follow.objects.create(follower_user=self.profile, follows_user=profile2)
        Follow.objects.create(follower_user=self.profile, follows_user=profile3)
        follows = Follow.objects.filter(follower_user=self.profile)
        self.assertEqual(follows.count(), 2)


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

    def test_rating_creation(self):
        self.assertEqual(self.rating.user_profile, self.profile)
        self.assertEqual(self.rating.movie, self.movie)
        self.assertEqual(self.rating.rating, 10)
        self.assertEqual(self.rating.review, "Amazing!")

    def test_rating_foreign_key_relationship(self):
        ratings = Rating.objects.filter(user_profile=self.profile)
        self.assertIn(self.rating, ratings)
        ratings_for_movie = Rating.objects.filter(movie=self.movie)
        self.assertIn(self.rating, ratings_for_movie)

    def test_multiple_ratings_for_same_movie(self):
        user2 = User.objects.create_user(username="user2", password="password")
        profile2 = UserProfile.objects.create(user=user2, biography="user2")
        rating2 = Rating.objects.create(
            user_profile=profile2,
            movie=self.movie,
            rating=8,
            review="Good movie"
        )
        ratings = Rating.objects.filter(movie=self.movie)
        self.assertEqual(ratings.count(), 2)
        self.assertIn(self.rating, ratings)
        self.assertIn(rating2, ratings)

    def test_user_can_have_multiple_ratings(self):
        movie2 = Movie.objects.create(
            movieID=2,
            title="Movie 2",
            release_date="2001-01-01",
            overview="Another movie",
            poster_path="http://example.com/movie2.jpg",
            average_rating=7.5
        )
        rating2 = Rating.objects.create(
            user_profile=self.profile,
            movie=movie2,
            rating=7,
            review="Not bad"
        )
        user_ratings = Rating.objects.filter(user_profile=self.profile)
        self.assertEqual(user_ratings.count(), 2)

    def test_rating_different_values(self):
        movie2 = Movie.objects.create(
            movieID=3,
            title="Movie 3",
            release_date="2002-01-01",
            overview="Test",
            poster_path="http://example.com/movie3.jpg"
        )
        user2 = User.objects.create_user(username="user2", password="password")
        profile2 = UserProfile.objects.create(user=user2, biography="user2")
        
        for rating_value in [1, 5, 10]:
            Rating.objects.create(
                user_profile=profile2,
                movie=movie2,
                rating=rating_value,
                review=f"{rating_value} star review"
            )
        all_ratings = Rating.objects.filter(movie=movie2)
        self.assertEqual(all_ratings.count(), 3)









class UserFormTest(TestCase):
    def test_valid_user_form(self):
        data = {'username': 'newuser', 'email': 'ua@example.com', 'password': 'password'}
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_user_form(self):
        data = {'username': '', 'email': 'ua@example.com', 'password': 'password'}
        form = UserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_missing_password(self):
        data = {'username': 'newuser', 'email': 'ua@example.com', 'password': ''}
        form = UserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_missing_email(self):
        data = {'username': 'newuser', 'email': '', 'password': 'password'}
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_missing_all_fields(self):
        data = {'username': '', 'email': '', 'password': ''}
        form = UserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_valid_with_valid_email(self):
        data = {'username': 'testuser', 'email': 'user@example.co.uk', 'password': 'testpass123'}
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_has_password_input_widget(self):
        form = UserForm()
        self.assertEqual(form.fields['password'].widget.__class__.__name__, 'PasswordInput')

    def test_form_save_creates_user(self):
        data = {'username': 'newuser', 'email': 'new@example.com', 'password': 'password123'}
        form = UserForm(data=data)
        if form.is_valid():
            user = form.save()
            self.assertEqual(user.username, 'newuser')
            self.assertEqual(user.email, 'new@example.com')


class UserProfileFormTest(TestCase):
    def test_valid_profile_form(self):
        form = UserProfileForm(data={'biography': 'movies'})
        self.assertTrue(form.is_valid())

    def test_empty_biography_valid(self):
        form = UserProfileForm(data={'biography': ''})
        self.assertTrue(form.is_valid())

    def test_long_biography(self):
        bio = 'x' * 500
        form = UserProfileForm(data={'biography': bio})
        self.assertTrue(form.is_valid())

    def test_biography_exceeds_max_length(self):
        bio = 'x' * 501
        form = UserProfileForm(data={'biography': bio})
        self.assertFalse(form.is_valid())

    def test_profile_form_has_biography_field(self):
        form = UserProfileForm()
        self.assertIn('biography', form.fields)

    def test_profile_form_save(self):
        user = User.objects.create_user(username='testuser', password='password')
        form = UserProfileForm(data={'biography': 'Test bio'})
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            self.assertEqual(profile.biography, 'Test bio')










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
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:all_movies'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.movie, response.context['movies'])

    def test_view_profile(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:view_profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie_app/profile.html')
        self.assertEqual(response.context['profile'].biography, "movies")

    def test_login_post_success(self):
        response = self.client.post(reverse('movie_app:login'), {
            'username': 'testuser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movie_app:dashboard'))

    def test_login_post_invalid_credentials(self):
        response = self.client.post(reverse('movie_app:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertTemplateUsed(response, 'movie_app/login.html')

    def test_login_post_nonexistent_user(self):
        response = self.client.post(reverse('movie_app:login'), {
            'username': 'nonexistent',
            'password': 'password'
        }, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_signup_post_success(self):
        response = self.client.post(reverse('movie_app:sign_up'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'biography': 'New user bio'
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_signup_password_mismatch(self):
        response = self.client.post(reverse('movie_app:sign_up'), {
            'username': 'newuser2',
            'email': 'new2@example.com',
            'password': 'pass123',
            'password2': 'differentpass',
            'biography': 'Bio'
        }, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_logout_redirects_to_login(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('movie_app:login'))

    def test_logout_requires_login(self):
        response = self.client.get(reverse('movie_app:logout'))
        self.assertEqual(response.status_code, 302)

    def test_all_movies_view_contains_context(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:all_movies'))
        self.assertIn('movies', response.context)
        self.assertIn('query', response.context)
        self.assertIn('year', response.context)

    def test_all_movies_search_by_title(self):
        self.client.login(username='testuser', password='password')
        Movie.objects.create(
            movieID=2,
            title="Inception",
            release_date="2010-01-01",
            overview="Dream movie",
            poster_path="http://example.com/inception.jpg"
        )
        response = self.client.get(reverse('movie_app:all_movies'), {'q': 'Inception'})
        self.assertEqual(response.status_code, 200)
        movies = response.context['movies']
        self.assertEqual(len(list(movies)), 1)
        self.assertEqual(list(movies)[0].title, 'Inception')

    def test_all_movies_filter_by_year(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:all_movies'), {'year': '2000'})
        self.assertEqual(response.status_code, 200)
        movies = response.context['movies']
        self.assertIn(self.movie, movies)

    def test_all_movies_empty_query(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:all_movies'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.movie, response.context['movies'])

    def test_dashboard_shows_user_ratings(self):
        rating = Rating.objects.create(
            user_profile=self.profile,
            movie=self.movie,
            rating=9,
            review="Great movie!"
        )
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(rating, response.context['ratings'])

    def test_dashboard_shows_watchlist(self):
        self.profile.watch_list.add(self.movie)
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], self.profile)

    def test_view_profile_shows_user_ratings(self):
        rating = Rating.objects.create(
            user_profile=self.profile,
            movie=self.movie,
            rating=8,
            review="Good"
        )
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:view_profile', args=[self.user.username]))
        self.assertIn(rating, response.context['ratings'])

    def test_view_profile_own_profile_indicator(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:view_profile', args=[self.user.username]))
        self.assertTrue(response.context['is_own_profile'])

    def test_view_other_profile_not_own(self):
        user2 = User.objects.create_user(username='otheruser', password='password')
        profile2 = UserProfile.objects.create(user=user2, biography="other")
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:view_profile', args=['otheruser']))
        self.assertFalse(response.context['is_own_profile'])

    def test_view_profile_following_status(self):
        user2 = User.objects.create_user(username='otheruser', password='password')
        profile2 = UserProfile.objects.create(user=user2, biography="other")
        Follow.objects.create(follower_user=self.profile, follows_user=profile2)
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('movie_app:view_profile', args=['otheruser']))
        follows = Follow.objects.filter(follower_user=self.profile, follows_user=profile2)
        self.assertTrue(follows.exists())