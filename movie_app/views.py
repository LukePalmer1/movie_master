from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse

from movie_app.models import UserProfile

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
            user = User.objects.create_user(username=username, password=password)
            user.save()

            profile = UserProfile.objects.create(user=user, biography=biography)
            profile.save()

            registered = True

    context = {'registered': registered, 'error': error}
    return render(request, 'movie_app/signup.html', context)
