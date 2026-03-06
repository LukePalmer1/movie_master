from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    movieID = models.IntegerField(unique=True, primary_key=True)
    title = models.CharField(max_length=200)
    release_date = models.CharField(max_length=10)
    overview = models.CharField(max_length=1000)
    poster_path = models.URLField(max_length=100)
    average_rating = models.FloatField(max_length=4, default=0)

    def __str__(self):
        return self.title
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    biography = models.CharField(max_length=500)
    watch_list = models.ManyToManyField(Movie, blank=True)
    follow_list = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.user.username
    
        
class Rating(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET(-1)) # Set id = -1, will be handled later as q deleted user
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE) 
    rating = models.IntegerField()
    review = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.user_profile}'s review of {self.movie}"
