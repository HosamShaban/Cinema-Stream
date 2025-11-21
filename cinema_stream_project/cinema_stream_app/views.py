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
