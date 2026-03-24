from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse

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
                return redirect('movie_app:dashboard')
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