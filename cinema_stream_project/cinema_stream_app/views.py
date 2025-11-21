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

def register(request):
    if request.method == "POST":
        avatar_file = request.FILES.get('avatar')
        errors = models.register_validator(request.POST, avatar_file=avatar_file)

        if errors:
            for key, value in errors.items():
                messages.error(request, value)
        else:
            user = models.create_user(request.POST, avatar_file=avatar_file)
            request.session['user_id'] = user.id
            messages.success(request, f"Welcome {user.first_name}! Account created successfully.")
            return redirect('home')
    return render(request, 'register.html')


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = models.authenticate_user(email, password)

        if user:
            request.session['user_id'] = user.id
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('home')


def profile(request):
    user = request.user
    profile = user.profile
    favorites = models.Favorite.objects.filter(user=user).select_related('movie')
    reviews = models.Review.objects.filter(user=user).select_related('movie')

    context = {
        'profile': profile,
        'favorites': favorites,
        'reviews': reviews,
        'page_title': 'My Profile'
    }
    return render(request, 'profile.html', context)

def toggle_favorite(request, slug):
    movie = models.get_movie_by_slug(slug)
    if models.is_favorite(request.user, movie):
        models.remove_from_favorites(request.user, movie)
        messages.info(request, f"Removed {movie.title} from favorites.")
    else:
        models.add_to_favorites(request.user, movie)
        messages.success(request, f"Added {movie.title} to favorites!")
    return redirect('movie_detail', slug=slug)

def add_review(request, slug):
    movie = get_movie_by_slug(slug)
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            create_review(request.user, movie, int(rating), comment)
            messages.success(request, "Thank you! Your review has been submitted.")
        else:
            messages.error(request, "Please provide both rating and comment.")
    return redirect('movie_detail', slug=slug)