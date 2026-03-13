from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from movie_app.forms import UserForm, UserProfileForm
from movie_app.models import Rating, UserProfile

# Create your views here.

def register(request):
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

@login_required
def user_logout(request):
    logout(request)
    return redirect('movie_app:login')

@login_required
def restricted(request):
    return render(request, 'movie_app/restricted.html')

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