import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','movie_master.settings')

import django
django.setup()

from movie_app.models import Movie

def populate():
    with open("TMDB_movie_dataset.csv", encoding = "utf-8") as f:
        i = 0
        for lineStr in f:
            if i == 10000:
                break
            line = lineStr.split("\",\"")
            add_movie(id = int(line[0][1:]), title = line[1], release_date = line[5], overview = line[15], poster_path = line[17])
            i += 1

        

def add_movie(id : int, title: str, release_date: str, overview: str, poster_path: str):
    movie = Movie.objects.get_or_create(movieID = id)[0]
    movie.title = title
    movie.release_date = release_date
    movie.overview = overview.replace("\"\"", "\"")
    if poster_path != "":
        movie.poster_path = "https://image.tmdb.org/t/p/original" + poster_path
    else:
        movie.poster_path = "https://placehold.co/300x450/e9ecef/495057?text=Movie+Poster"
    movie.save()

if __name__ == '__main__':
    print('Starting population script...')
    populate()
    print('Finished population script')
