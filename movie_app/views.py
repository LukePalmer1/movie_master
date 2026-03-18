from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse

from movie_app.models import UserProfile, Rating, Movie

def user_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('movie_app:dashboard'))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('movie_app:dashboard'))
            else:
                return HttpResponse("Your account is disabled.")
        else:
            context = {'error': 'Invalid username or password. Please try again.'}
            return render(request, 'movie_app/login.html', context)

    return render(request, 'movie_app/login.html')

def sign_up(request):
    if request.user.is_authenticated:
        return redirect(reverse('movie_app:dashboard'))

    registered = False
    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        biography = request.POST.get('biography', '').strip()

        if not username or not password:
            error = 'Username and password are required.'
        elif password != password2:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error = 'That username is already taken.'
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()

            profile = UserProfile.objects.create(user=user, biography=biography)
            profile.save()

            registered = True

    context = {'registered': registered, 'error': error}
    return render(request, 'movie_app/signup.html', context)

@login_required
def user_logout(request):
    #Log the user out and send them back to the homepage.
    logout(request)
    return redirect(reverse('movie_app:login'))

@login_required
def dashboard(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    ratings = Rating.objects.filter(user_profile=profile).select_related('movie')
    watchlist = profile.watch_list.all()

    context = {
        'profile': profile,
        'ratings': ratings,
        'watchlist': watchlist,
    }
    return render(request, 'movie_app/dashboard.html', context)

def all_movies(request):
    movies = Movie.objects.all()

    query = request.GET.get('q', '').strip()
    if query:
        movies = movies.filter(title__icontains=query)

    year = request.GET.get('year', '').strip()
    if year:
        movies = movies.filter(release_date__startswith=year)

    movies = movies.order_by('title')

    context = {
        'movies': movies,
        'query': query,
        'year': year,
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

    context = {
        'profile': profile,
        'profile_user': profile_user,
        'ratings': ratings,
        'already_following': already_following,
        'is_own_profile': is_own_profile,
    }
    return render(request, 'movie_app/profile.html', context)