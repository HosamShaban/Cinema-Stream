from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render , redirect
from django.contrib import messages
from . import models

def home(request):
    trending = models.get_trending_movies()
    latest = models.get_all_movies()[:12]

    context = {
        'trending_movies': trending,
        'latest_movies': latest,
        'page_title': 'Cinema Stream'
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
    active_tab = 'register'

    if request.method == "POST":
        avatar_file = request.FILES.get('avatar')
        errors = models.register_validator(request.POST, avatar_file=avatar_file)

        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='register')
        else:
            user = models.create_user(request.POST, avatar_file=avatar_file)
            request.session['user_id'] = user.id
            messages.success(request, f"Welcome {user.first_name}! Account created successfully.", extra_tags='register')
            return redirect('home')

    return render(request, 'auth.html', {'active_tab': active_tab})


def login_view(request):
    active_tab = 'login'

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = models.authenticate_user(email, password)

        if user:
            request.session['user_id'] = user.id
            messages.success(request, f"Welcome back, {user.first_name}!", extra_tags='login')
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.", extra_tags='login')

    return render(request, 'auth.html', {'active_tab': active_tab})

def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('home')


def profile(request):
    user = models.get_logged_user(request)
    if not user:
        messages.error(request, "Please login first.")
        return redirect('login')

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

def edit_profile(request):
    user = models.get_logged_user(request)
    if not user:
        messages.error(request, "Please login first.")
        return redirect('login')

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        avatar_file = request.FILES.get('avatar')

        errors = {}
        if not first_name:
            errors['first_name'] = "First name is required."
        if not last_name:
            errors['last_name'] = "Last name is required."
        if not email:
            errors['email'] = "Email is required."

        if errors:
            for key, value in errors.items():
                messages.error(request, value)
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            if avatar_file:
                user.profile.avatar = avatar_file
            user.save()
            user.profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')

    return render(request, 'edit_profile.html', {'profile': user.profile})


def toggle_favorite(request, slug):
    user = models.get_logged_user(request)
    if not user:
        messages.error(request, "Please login first.")
        return redirect('login')

    movie = models.get_movie_by_slug(slug)

    if models.is_favorite(user, movie):
        models.remove_from_favorites(user, movie)
        messages.info(request, f"Removed {movie.title} from favorites.")
    else:
        models.add_to_favorites(user, movie)
        messages.success(request, f"Added {movie.title} to favorites!")

    return redirect('movie_detail', slug=slug)

def add_review(request, slug):
    movie = models.get_movie_by_slug(slug)
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            models.create_review(request.user, movie, int(rating), comment)
            messages.success(request, "Thank you! Your review has been submitted.")
        else:
            messages.error(request, "Please provide both rating and comment.")
    return redirect('movie_detail', slug=slug)

def about(request):
    return render(request, 'about.html', {'page_title': 'About Us'})

def api_toggle_favorite(request):
    if request.method != "POST":
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed. Use POST.'
        }, status=405)

    user = models.get_logged_user(request)
    if not user:
        return JsonResponse({
            'success': False,
            'message': 'Please login to continue.'
        }, status=401)

    slug = request.POST.get('slug')
    if not slug:
        return JsonResponse({
            'success': False,
            'message': 'Movie slug is required.'
        }, status=400)

    movie = get_object_or_404(models.Movie, slug=slug)
    favorite, created = models.Favorite.objects.get_or_create(user=user, movie=movie)
    
    if not created:
        favorite.delete()
        action = "removed"
        is_favorite = False
    else:
        action = "added"
        is_favorite = True
    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
        'action': action,
        'total_favorites': movie.favorite_set.count(),
        'message': f"Movie {action} to favorites successfully!"
    })