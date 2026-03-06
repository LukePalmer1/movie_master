from django.contrib import admin
from movie_app.models import Movie, UserProfile, Rating

class UserProfileAdmin(admin.ModelAdmin):
    pass

class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "poster_path", "average_rating")
    exclude = ("movieID",)

class RatingAdmin(admin.ModelAdmin):
    list_display = ("user_profile", "movie", "rating", "review")

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Rating, RatingAdmin)