from django.urls import path
from movie_app import views

app_name = 'movie_app'

urlpatterns = [
     path('', views.user_login, 
        name='homepage'),

     path('login/', views.user_login, 
        name='login'),

     path('sign-up/', views.sign_up,
         name='sign_up'),

     path('logout/', views.user_logout,
         name='logout'),
         
     path('dashboard/', views.dashboard,
         name='dashboard'),

     path('all-movies/', views.all_movies,
         name='all_movies'),

     path('all-movies/<int:page>/', views.all_movies,
         name='all_movies'),

    path('profile/save-bio/', views.save_bio,
        name='save_bio'),

    path('profile/reviews/<int:rating_id>/edit/', views.edit_review, 
        name='edit_review'),

    path('profile/<slug:user_slug>/', views.view_profile, 
        name='view_profile'),
    
    path('<int:movieID>/watchlist/', views.toggle_watchlist,
        name='toggle_watchlist'),

    path('movie-detail/<int:movieID>/', views.movie_detail, 
        name='movie_detail'),

    path('<slug:user_slug>/toggle-follow/', views.toggle_follow, 
        name='toggle_follow'),
]