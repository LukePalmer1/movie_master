from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
from django.core.paginator import Paginator

from movie_app.forms import UserForm, UserProfileForm
from movie_app.models import UserProfile, Rating, Movie

def user_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('movie_app:dashboard'))
            else:
                error = "Your account is disabled."
        else:
            error = "Invalid login credentials."
    return render(request, 'movie_app/login.html', {'error': error})

def sign_up(request):
    registered = False
    error = None  # for password mismatch

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            error = "Your passwords don't match"
        elif user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            registered = True
        else:
            error = "Please fix the errors"

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'movie_app/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered,
        'error': error
    })

@login_required
def user_logout(request):
    #Log the user out and send them back to the homepage.
    logout(request)
    return redirect(reverse('movie_app:login'))

@login_required
def dashboard(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    ratings = Rating.objects.filter(user_profile=profile).select_related('movie')[:7]
    watchlist = profile.watch_list.all()
    movies = Movie.objects.all()[:8]

    context = {
        'profile': profile,
        'ratings': ratings,
        'watchlist': watchlist,
        'movies' : movies,
    }
    return render(request, 'movie_app/dashboard.html', context)

def all_movies(request, page=1):
    movies = Movie.objects.all()

    query = request.GET.get('q', '').strip()
    if query:
        movies = movies.filter(title__icontains=query)

    year = request.GET.get('year', '').strip()
    if year and year != "all":
        if year == "older":
            movies = movies.filter(release_date__startswith="1")
        else:
            movies = movies.filter(release_date__startswith=year)

    movies = movies.order_by('title')
    paginator = Paginator(movies, 100)
    last_page_no = paginator.num_pages

    if page > last_page_no:
        return redirect(reverse('movie_app:all_movies') + str(last_page_no)  + "?" + request.GET.urlencode())
    
    cur_page = paginator.get_page(page)

    context = {
        'movies': cur_page,
        'query': query,
        'year': year,
        'num_pages': last_page_no,
        'page': page,
    }
    return render(request, 'movie_app/all_movies.html', context)

@login_required
def view_profile(request, user_slug):
    profile_user = get_object_or_404(User, username=user_slug)
    profile = get_object_or_404(UserProfile, user=profile_user)
    ratings = Rating.objects.filter(user_profile=profile).select_related('movie')

    already_following = False
    if request.user.is_authenticated and request.user != profile_user:
        try:
            viewer_profile = UserProfile.objects.get(user=request.user)
            already_following = viewer_profile.follow_list.filter(pk=profile.pk).exists()
        except UserProfile.DoesNotExist:
            pass

    is_own_profile = request.user == profile_user

    if request.POST:
        removed_movie = get_object_or_404(Movie, movieID__iexact=request.POST.get("removed_movie"))

        if removed_movie:
            profile.watch_list.remove(removed_movie.movieID)

    context = {
        'profile': profile,
        'profile_user': profile_user,
        'ratings': ratings,
        'already_following': already_following,
        'is_own_profile': is_own_profile,
    }
    return render(request, 'movie_app/profile.html', context)

def movie_detail(request, movieID):
    movie = get_object_or_404(Movie, movieID__iexact=movieID)
    ratings = Rating.objects.filter(movie=movie).select_related('user_profile__user')

    user_rating = None
    in_watchlist = False
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            if request.POST:
                rating = request.POST.get("rating")
                review = request.POST.get("review")
                new_rating, created = Rating.objects.get_or_create(user_profile = profile, movie = movie)
                new_rating.rating = rating
                new_rating.review = review
                new_rating.save()

                movie_ratings = Rating.objects.filter(movie=movie)
                total = 0
                if created:
                    movie.no_of_ratings += 1
                for cur_rating in movie_ratings:
                    total += cur_rating.rating
                movie.average_rating = total
                movie.save()

            user_rating = Rating.objects.filter(user_profile=profile, movie=movie).first()
            in_watchlist = profile.watch_list.filter(pk=movie.pk).exists()
        except UserProfile.DoesNotExist:
            pass

    context = {
        'movie': movie,
        'ratings': ratings,
        'user_rating': user_rating,
        'in_watchlist': in_watchlist,
    }
    return render(request, 'movie_app/movie_detail.html', context)

@login_required
def toggle_watchlist(request, movieID):
    if request.method == 'POST':
        movie   = get_object_or_404(Movie, movieID__iexact=movieID)
        profile = get_object_or_404(UserProfile, user=request.user)

        if profile.watch_list.filter(pk=movie.pk).exists():
            profile.watch_list.remove(movie)
        else:
            profile.watch_list.add(movie)

    return redirect(reverse('movie_app:movie_detail',
                            kwargs={'movieID': movieID}))

@login_required
def follow_user(request, user_slug):
    if request.method == 'POST':
        target_user    = get_object_or_404(User, username=user_slug)
        target_profile = get_object_or_404(UserProfile, user=target_user)
        my_profile     = get_object_or_404(UserProfile, user=request.user)

        if target_user != request.user:
            if my_profile.follow_list.filter(pk=target_profile.pk).exists():
                my_profile.follow_list.remove(target_profile)
            else:
                my_profile.follow_list.add(target_profile)

    return redirect(reverse('movie_app:view_profile', kwargs={'user_slug': user_slug}))