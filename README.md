# MovieMaster

A Django web application for discovering and reviewing movies. Users can browse a catalogue of films sourced from TMDB, rate and review them, manage a personal watchlist, and follow other users.

## Features

- Browse and search a catalogue of 10,000+ movies
- Rate and review movies
- Personal watchlist management
- User profiles with biography
- Follow other users and see their reviews
- Filter movies by release year

## Tech Stack

- **Programming Language:** Python 3.14.11
- **Backend:** Django 2.2.28
- **Database:** SQLite3
- **Image handling:** Pillow
- **Movie data:** TMDB dataset

## Run locally

Clone the project

```bash
git clone https://github.com/LukePalmer1/movie_master
```

Go to the project directory

```bash
cd movie_master
```

Install dependencies

```bash
pip install -r requirements.txt
```

Apply database migrations

```bash
python manage.py migrate
```

Populate the database with movies

> Download the TMDB_movie_sub_dataset CSV and place it in the project root as `TMDB_movie_dataset.csv`, then run:

```bash
python population_script.py
```

Start the development server

```bash
python manage.py runserver
```

The app will be available at `https://lukepalmer13.pythonanywhere.com`

## Project Structure

```
movie_master/
├── movie_app/
│   ├── models.py       # Movie, UserProfile, Rating, Follow models
│   ├── views.py        # All view logic
│   ├── urls.py         # URL routing
│   ├── forms.py        # User registration and profile forms
│   └── templates/      # HTML templates
├── static/             # CSS and static assets
├── population_script.py
├── manage.py
└── requirements.txt
```

## Data Models

- **Movie** — title, release date, overview, poster, average rating
- **UserProfile** — linked to Django's User, with biography and watchlist
- **Rating** — user review and star rating for a movie
- **Follow** — follower/following relationships between users
