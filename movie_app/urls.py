from django.urls import path
from movie_app import views

app_name = 'movie_app'

urlpatterns = [
    path('login/', views.user_login, 
        name='login'),

    path('sign-up/', views.sign_up,
         name='sign_up'),

    path('logout/', views.user_logout,
         name='logout'),
         
    path('dashboard/', views.dashboard,
         name='dashboard'),
]