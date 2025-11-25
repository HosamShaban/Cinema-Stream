from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render , redirect
from django.core.paginator import Paginator
from django.contrib import messages
from . import models
import json
from django.db.models import Q
from django.contrib.auth.models import User

def home(request):
    current_year = 2024
    
    recent_movies = models.Movie.objects.filter(
        release_year__gte=2023
    ).order_by('-release_year', '-created_at')[:15] 
    
    recent_series = models.Series.objects.filter(
        first_air_date__gte=2023
    ).order_by('-first_air_date', '-created_at')[:15]

    if not recent_movies.exists():
        recent_movies = models.Movie.objects.order_by('-release_year', '-created_at')[:15]
        print("No recent movies found, using fallback")
    
    if not recent_series.exists():
        recent_series = models.Series.objects.order_by('-first_air_date', '-created_at')[:15]
        print("No recent series found, using fallback")

    recently_added = list(recent_movies) + list(recent_series)
    
    def get_content_year(item):
        if hasattr(item, 'release_year') and item.release_year:
            return item.release_year
        elif hasattr(item, 'first_air_date') and item.first_air_date:
            return item.first_air_date
        return 0
    
    recently_added.sort(key=get_content_year, reverse=True)
    recently_added = recently_added[:20]

    featured = models.Movie.objects.filter(
        release_year__gte=2023,
        overall_rating__gte=7.0
    ).order_by('-overall_rating').first()
    
    if not featured:
        featured = models.Movie.objects.filter(is_premium=True).order_by('-overall_rating').first()
    if not featured:
        featured = models.Movie.objects.order_by('-overall_rating').first()

    trending_movies = models.Movie.objects.filter(
        release_year__gte=2022
    ).order_by('-overall_rating')[:15]
    
    trending_series = models.Series.objects.filter(
        first_air_date__gte=2022
    ).order_by('-overall_rating')[:15]
    
    trending = list(trending_movies) + list(trending_series)
    trending.sort(key=lambda x: x.overall_rating, reverse=True)
    trending = trending[:20]

    top_english_movies = models.Movie.objects.filter(
        language__icontains='en',
        release_year__gte=2022
    ).order_by('-overall_rating')[:8]
    
    if not top_english_movies.exists():
        top_english_movies = models.Movie.objects.filter(
            language__icontains='en'
        ).order_by('-overall_rating')[:8]
    
    top_english_series = models.Series.objects.filter(
        language__icontains='en', 
        first_air_date__gte=2022
    ).order_by('-overall_rating')[:8]
    
    if not top_english_series.exists():
        top_english_series = models.Series.objects.filter(
            language__icontains='en'
        ).order_by('-overall_rating')[:8]

    user_favorites = []
    if request.user.is_authenticated:
        movie_favs = request.user.favorites.filter(movie__isnull=False).values_list('movie__slug', flat=True)
        series_favs = request.user.favorites.filter(series__isnull=False).values_list('series__slug', flat=True)
        user_favorites = list(movie_favs) + list(series_favs)
    
    print(f"User favorites: {user_favorites}")

    genres = models.Genre.objects.all()[:20]
    context = {
        'recently_added': recently_added,
        'featured': featured,
        'trending': trending,
        'top_english_movies': top_english_movies,
        'top_english_series': top_english_series,
        'genres': genres,
        'user_favorites': user_favorites,
    }
    
    for item in recently_added[:5]:
        year = get_content_year(item)
        print(f" - {item.title} ({year}) - {item.content_type}")

    return render(request, 'home.html', context)

def browse(request):
    genres = models.Genre.objects.all()
    query = request.GET.get('q')
    genre = request.GET.get('genre')
    year = request.GET.get('year')
    content_type = request.GET.get('type', 'all')

    movies = models.Movie.objects.all()
    series = models.Series.objects.all()

    if query:
        movies = movies.filter(title__icontains=query)
        series = series.filter(title__icontains=query)
    
    if genre:
        movies = movies.filter(genres__slug=genre)
        series = series.filter(genres__slug=genre)
    
    if year:
        movies = movies.filter(release_year=year)
        series = series.filter(first_air_date=year)
    
    if content_type != 'all':
        if content_type == 'movie':
            series = series.none()
        elif content_type == 'series':
            movies = movies.none()

    from itertools import chain
    from operator import attrgetter
    
    all_content = sorted(
        chain(movies, series),
        key=attrgetter('overall_rating'),
        reverse=True
    )

    paginator = Paginator(all_content, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'content': page_obj,
        'genres': genres,
        'current_genre': genre,
        'current_year': year,
        'current_type': content_type,
        'query': query,
        'page_title': 'Browse Content'
    }
    
    return render(request, 'browse.html', context)

def movie_detail(request, slug):
    movie = get_object_or_404(models.Movie, slug=slug)

    is_fav = False
    user_review = None

    if request.user.is_authenticated:
        user = request.user
        is_fav = models.Favorite.objects.filter(user=user, movie=movie).exists()
        user_review = movie.reviews.filter(user=user).first()

    context = {
        'movie': movie,
        'is_favorite': is_fav,
        'user_review': user_review,
        'page_title': movie.title
    }
    return render(request, 'movie_detail.html', context)

def series_detail(request, slug):
    series = get_object_or_404(models.Series, slug=slug)
    
    is_fav = False
    if request.user.is_authenticated:
        is_fav = models.Favorite.objects.filter(user=request.user, series=series).exists()

    context = {
        'series': series,
        'is_favorite': is_fav,
        'page_title': series.title
    }
    return render(request, 'series_detail.html', context)


def login_view(request):
    active_tab = 'login'

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = models.authenticate_user(email, password)

        if user:
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!", extra_tags='login')
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.", extra_tags='login')

    return render(request, 'auth.html', {'active_tab': active_tab})

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
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, f"Welcome {user.first_name}! Account created successfully.", extra_tags='register')
            return redirect('home')

    return render(request, 'auth.html', {'active_tab': active_tab})

def logout_view(request):
    from django.contrib.auth import logout
    storage = messages.get_messages(request)
    storage.used = True
    logout(request)
    
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

def profile(request):
    user = request.user
    if not user.is_authenticated:
        messages.error(request, "Please login first.")
        return redirect('login')

    print(f"PROFILE DEBUG - User: {user.username}")

    favorites = models.Favorite.objects.filter(user=user).select_related('movie', 'series')
    print(f"Total favorites in DB: {favorites.count()}")

    favorite_movies = []
    favorite_series = []
    
    for fav in favorites:
        print(f"Processing favorite: {fav}")
        if fav.movie:
            print(f"Movie found: {fav.movie.title} (Slug: {fav.movie.slug})")
            favorite_movies.append(fav.movie)
        elif fav.series:
            print(f" Series found: {fav.series.title} (Slug: {fav.series.slug})")
            favorite_series.append(fav.series)
        else:
            print(" Invalid favorite")

    print(f"🎬 Final movies list: {[m.title for m in favorite_movies]}")
    print(f"📺 Final series list: {[s.title for s in favorite_series]}")

    context = {
        'user': user,
        'profile': user.profile,
        'favorite_movies': favorite_movies,
        'favorite_series': favorite_series,
        'favorites_count': len(favorite_movies) + len(favorite_series),
        'reviews': models.Review.objects.filter(user=user),
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

def toggle_series_favorite(request, slug):
    user = models.get_logged_user(request)
    if not user:
        messages.error(request, "Please login first.")
        return redirect('login')

    series = models.Series.objects.get(slug=slug)

    is_fav = models.Favorite.objects.filter(user=user, series=series).exists()
    
    if is_fav:
        models.Favorite.objects.filter(user=user, series=series).delete()
        messages.info(request, f"Removed {series.title} from favorites.")
    else:
        fav, created = models.Favorite.objects.get_or_create(
            user=user, 
            series=series,
            defaults={'series': series}
        )
        messages.success(request, f"Added {series.title} to favorites!")
    
    return redirect('series_detail', slug=slug)

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


def api_search_suggestions(request):
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 5))
    
    if len(query) < 1:
        return JsonResponse([])
    
    movies = models.Movie.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )[:limit]
    
    series = models.Series.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )[:limit]
    
    suggestions = []
    
    for movie in movies:
        suggestions.append({
            'id': movie.id,
            'title': movie.title,
            'slug': movie.slug,
            'content_type': 'movie',
            'poster_path': movie.poster_path,
            'release_year': movie.release_year,
            'overall_rating': float(movie.overall_rating) if movie.overall_rating else None
        })
    
    for series in series:
        suggestions.append({
            'id': series.id,
            'title': series.title,
            'slug': series.slug,
            'content_type': 'series',
            'poster_path': series.poster_path,
            'first_air_date': series.first_air_date,
            'overall_rating': float(series.overall_rating) if series.overall_rating else None
        })
    
    suggestions.sort(key=lambda x: x['overall_rating'] or 0, reverse=True)
    
    return JsonResponse(suggestions[:limit], safe=False)

@csrf_exempt
def api_post_review(request):
    if request.method == 'POST':
        try:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            slug = request.POST.get('slug')

            if not slug or not rating:
                return JsonResponse({'success': False, 'error': 'Missing data'}, status=400)

            movie = get_object_or_404(models.Movie, slug=slug)
            user = request.user

            review, created = models.Review.objects.update_or_create(
                user=user, movie=movie,
                defaults={'rating': int(rating), 'comment': comment}
            )

            models.update_movie_rating(movie)

            return JsonResponse({
                'success': True,
                'message': 'Review submitted successfully!',
                'rating': review.rating,
                'comment': review.comment,
                'date': review.created_at.strftime("%b %d, %Y")
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)

@method_decorator(csrf_exempt, name='dispatch')
class ToggleFavoriteView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            slug = data.get('slug')
            content_type = data.get('content_type', 'movie')
            
            print(f"🔍 ToggleFavoriteView: slug={slug}, type={content_type}")
            
            if not slug:
                return JsonResponse({'success': False, 'error': 'Slug required'}, status=400)

            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'login_required': True,
                    'error': 'Please login first'
                }, status=200)

            user = request.user
            print(f"User: {user.username or user.email}")

            if content_type == 'movie':
                content = models.Movie.objects.get(slug=slug)
                print(f"Movie: {content.title}")
                
                existing = models.Favorite.objects.filter(user=user, movie=content).first()
                if existing:
                    existing.delete()
                    is_favorite = False
                    print("Removed from favorites")
                else:
                    models.Favorite.objects.create(user=user, movie=content)
                    is_favorite = True
                    print("Added to favorites")
                    
            elif content_type == 'series':
                content = models.Series.objects.get(slug=slug)
                print(f"Series: {content.title}")
                
                existing = models.Favorite.objects.filter(user=user, series=content).first()
                if existing:
                    existing.delete()
                    is_favorite = False
                    print("Removed from favorites")
                else:
                    models.Favorite.objects.create(user=user, series=content)
                    is_favorite = True
                    print("Added to favorites")
            else:
                return JsonResponse({'success': False, 'error': 'Invalid content type'}, status=400)

            return JsonResponse({
                'success': True,
                'is_favorite': is_favorite
            })

        except (models.Movie.DoesNotExist, models.Series.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Content not found'}, status=404)
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            return JsonResponse({'success': False, 'error': 'Server error'}, status=500)
        

