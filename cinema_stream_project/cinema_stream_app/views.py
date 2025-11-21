from django.shortcuts import render , redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import models

def home(request):
    trending = models.get_trending_movies()
    latest = models.get_all_movies()[:12]

    context = {
        'trending_movies': trending,
        'latest_movies': latest,
        'page_title': 'Cinema Stream - Home'
    }
    return render(request, 'home.html', context)

def browse(request):
    genres = models.Genre.objects.all()

    query = request.GET.get('q')
    genre = request.GET.get('genre')
    year = request.GET.get('year')
    ctype = request.GET.get('type')

    if query:
        movies = models.search_movies(query)
    else:
        movies = models.filter_movies(genre=genre, year=year, content_type=ctype)

    context = {
        'movies': movies,
        'genres': genres,
        'current_genre': genre,
        'current_year': year,
        'current_type': ctype,
        'query': query,
        'page_title': 'Browse Movies & Series'
    }
    return render(request, 'browse.html', context)

def movie_detail(request, slug):
    movie = models.get_movie_by_slug(slug)

    is_fav = False
    user_review = None

    if 'user_id' in request.session:
        user = models.get_logged_user(request)
        is_fav = models.is_favorite(user, movie)
        user_review = movie.reviews.filter(user=user).first()

    context = {
        'movie': movie,
        'is_favorite': is_fav,
        'user_review': user_review,
        'page_title': movie.title
    }
    return render(request, 'movie_detail.html', context)