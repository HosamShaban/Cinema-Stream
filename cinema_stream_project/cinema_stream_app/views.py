from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render , redirect
from django.core.paginator import Paginator
from django.contrib import messages
from .utils.tmdb import get_trailer_url
from . import models
import json
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from itertools import chain


def home(request):
    
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



def api_home(request):

    def movie_dict(m):
        return {
            'id': m.id, 'title': m.title, 'slug': m.slug,
            'poster': m.get_poster_url,
            'rating': float(m.overall_rating),
            'year': m.release_year,
            'content_type': getattr(m, 'content_type', 'movie'),
            'duration': getattr(m, 'duration', None),
            'poster_path': m.poster_path,
        }

    def series_dict(s):
        return {
            'id': s.id, 'title': s.title, 'slug': s.slug,
            'poster': s.get_poster_url,
            'rating': float(s.overall_rating),
            'year': s.first_air_date,
            'content_type': 'series',
            'seasons_count': s.seasons_count,
            'poster_path': s.poster_path,
        }

    recent_movies = list(models.Movie.objects.order_by('-created_at')[:15])
    recent_series = list(models.Series.objects.order_by('-created_at')[:15])
    recently_added = sorted(
        recent_movies + recent_series,
        key=lambda x: x.overall_rating,
        reverse=True
    )[:20]

    trend_movies = list(models.Movie.objects.filter(release_year__gte=2022).order_by('-overall_rating')[:10])
    trend_series = list(models.Series.objects.filter(first_air_date__gte=2022).order_by('-overall_rating')[:10])
    trending = sorted(trend_movies + trend_series, key=lambda x: x.overall_rating, reverse=True)[:20]

    top_movies = list(models.Movie.objects.filter(language__icontains='en').order_by('-overall_rating')[:8])

    top_series = list(models.Series.objects.filter(language__icontains='en').order_by('-overall_rating')[:8])

    def to_dict(item):
        return series_dict(item) if hasattr(item, 'seasons_count') else movie_dict(item)

    return JsonResponse({
        'recently_added': [to_dict(i) for i in recently_added],
        'trending':       [to_dict(i) for i in trending],
        'top_movies':     [movie_dict(m) for m in top_movies],
        'top_series':     [series_dict(s) for s in top_series],
    })


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


def api_browse(request):
    query        = request.GET.get('q',     '').strip()
    genre        = request.GET.get('genre', '').strip()
    year         = request.GET.get('year',  '').strip()
    content_type = request.GET.get('type',  'all')
    page_num     = int(request.GET.get('page', 1))
    per_page     = 20

    movies = models.Movie.objects.all()
    series = models.Series.objects.all()

    if query:
        movies = movies.filter(title__icontains=query)
        series = series.filter(title__icontains=query)

    if genre:
        movies = movies.filter(genres__slug=genre)
        series = series.filter(genres__slug=genre)

    if year:
        try:
            movies = movies.filter(release_year=int(year))
            series = series.filter(first_air_date=int(year))
        except ValueError:
            pass

    if content_type == 'movie':
        series = series.none()
    elif content_type == 'series':
        movies = movies.none()

    def movie_to_dict(m):
        return {
            'id': m.id, 'title': m.title, 'slug': m.slug,
            'poster': m.get_poster_url,
            'rating': float(m.overall_rating),
            'year': m.release_year,
            'content_type': 'movie',
            'duration': m.duration,
            'genres': [g.name for g in m.genres.all()[:2]],
            'poster_path': m.poster_path,
        }

    def series_to_dict(s):
        return {
            'id': s.id, 'title': s.title, 'slug': s.slug,
            'poster': s.get_poster_url,
            'rating': float(s.overall_rating),
            'year': s.first_air_date,
            'content_type': 'series',
            'seasons_count': s.seasons_count,
            'episodes_count': s.episodes_count,
            'genres': [g.name for g in s.genres.all()[:2]],
            'poster_path': s.poster_path,
        }

    all_items = sorted(
        list(movies.distinct()) + list(series.distinct()),
        key=lambda x: x.overall_rating,
        reverse=True
    )

    total   = len(all_items)
    start   = (page_num - 1) * per_page
    end     = start + per_page
    page    = all_items[start:end]

    results = []
    for item in page:
        if hasattr(item, 'duration'):
            results.append(movie_to_dict(item))
        else:
            results.append(series_to_dict(item))

    genres = [{'name': g.name, 'slug': g.slug} for g in models.Genre.objects.all()[:30]]

    return JsonResponse({
        'results':    results,
        'total':      total,
        'page':       page_num,
        'has_next':   end < total,
        'genres':     genres,
    })



def movie_detail(request, slug):
    movie = get_object_or_404(models.Movie, slug=slug)

    is_fav = False
    user_review = None

    if request.user.is_authenticated:
        user = request.user
        is_fav = models.Favorite.objects.filter(user=user, movie=movie).exists()
        user_review = movie.reviews.filter(user=user).first()

    if not movie.trailer_url and movie.tmdb_id:
        trailer = get_trailer_url(movie.tmdb_id, content_type='movie')
        if trailer:
            movie.trailer_url = trailer
            movie.save(update_fields=['trailer_url'])    

    context = {
        'movie': movie,
        'is_favorite': is_fav,
        'user_review': user_review,
        'page_title': movie.title
    }
    return render(request, 'movie_detail.html', context)

def series_detail(request, slug):
    series = get_object_or_404(models.Series, slug=slug)
    
    reviews = models.Review.objects.filter(series=series)
    
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    is_fav = False
    if request.user.is_authenticated:
        is_fav = models.Favorite.objects.filter(user=request.user, series=series).exists()

    context = {
        'series': series,
        'reviews': reviews,
        'user_review': user_review,
        'is_favorite': is_fav,
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


def api_movies(request):
    movies = models.Movie.objects.all().order_by('-created_at')
    data = []
    for m in movies:
        data.append({
            'id': m.id,
            'title': m.title,
            'slug': m.slug,
            'description': m.description,
            'poster': m.get_poster_url, 
            'rating': float(m.overall_rating),
            'year': m.release_year,
        })
    return JsonResponse({'results': data})

def api_trending(request):
    trending = models.Movie.objects.all().order_by('-overall_rating')[:10]
    data = []
    for m in trending:
        data.append({
            'id': m.id,
            'title': m.title,
            'slug': m.slug,
            'description': m.description,
            'poster': m.get_poster_url, 
            'rating': float(m.overall_rating),
            'year': m.release_year,
        })
    return JsonResponse({'results': data})

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

    favorites = models.Favorite.objects.filter(user=user).select_related('movie', 'series')
    
    favorite_movies = []
    favorite_series = []
    
    for fav in favorites:
        if fav.movie:
            favorite_movies.append(fav.movie)
        elif fav.series:
            favorite_series.append(fav.series)

    reviews = []
    
    movie_reviews = models.Review.objects.filter(user=user, movie__isnull=False).select_related('movie')
    for review in movie_reviews:
        if review.movie:
            reviews.append({
                'review': review,
                'type': 'movie',
                'content': review.movie,
                'title': review.movie.title,
                'slug': review.movie.slug,
                'poster_url': review.movie.poster.url if review.movie.poster else (
                    f"https://image.tmdb.org/t/p/w300{review.movie.poster_path}" if review.movie.poster_path else 
                    "https://via.placeholder.com/300x450/333333/FFFFFF?text=No+Poster"
                ),
                'year': review.movie.release_year
            })

    series_reviews = models.Review.objects.filter(user=user, series__isnull=False).select_related('series')
    for review in series_reviews:
        if review.series:
            reviews.append({
                'review': review,
                'type': 'series',
                'content': review.series,
                'title': review.series.title,
                'slug': review.series.slug,
                'poster_url': review.series.poster.url if review.series.poster else (
                    f"https://image.tmdb.org/t/p/w300{review.series.poster_path}" if review.series.poster_path else 
                    "https://via.placeholder.com/300x450/333333/FFFFFF?text=No+Poster"
                ),
                'year': review.series.first_air_date
            })

    context = {
        'user': user,
        'profile': user.profile,
        'favorite_movies': favorite_movies,
        'favorite_series': favorite_series,
        'favorites_count': len(favorite_movies) + len(favorite_series),
        'reviews': reviews,
        'page_title': 'My Profile'
    }

    return render(request, 'profile.html', context)

def edit_profile(request):
    user = request.user
    profile = user.profile

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

        if User.objects.exclude(pk=user.pk).filter(email=email).exists():
            errors['email'] = "This email is already taken."

        if errors:
            for key, value in errors.items():
                messages.error(request, value)
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            if avatar_file:
                profile.avatar = avatar_file
            user.save()
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')

    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'edit_profile.html', context)


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

@login_required
def api_delete_review(request, review_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        print(f"Deleting review {review_id} for user {request.user}")
        
        review = get_object_or_404(models.Review, id=review_id, user=request.user)
        
        movie = review.movie
        series = review.series
        
        review.delete()
        
        print("Review deleted successfully and rating updated automatically")

        return JsonResponse({
            'success': True, 
            'message': 'Review deleted successfully'
        })

    except Exception as e:
        print(f"Error deleting review: {e}")
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)

def about(request):
    return render(request, 'about.html', {'page_title': 'About Us'})

def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})

    results = []

    movies = models.Movie.objects.filter(
        Q(title__icontains=query)
    ).only('title', 'slug', 'poster', 'release_year')[:6]

    for m in movies:
        results.append({
            'title': m.title,
            'year': m.release_year or 2024,
            'poster': m.poster.url if m.poster else None,
            'url': f"/movie/{m.slug}/",
            'type': 'movie'
        })

    series = models.Series.objects.filter(
        Q(title__icontains=query)
    ).only('title', 'slug', 'poster', 'first_air_date')[:6]

    for s in series:
        results.append({
            'title': s.title,
            'year': s.first_air_date or 2024,
            'poster': s.poster.url if s.poster else None,
            'url': f"/series/{s.slug}/",
            'type': 'series'
        })

    return JsonResponse({'results': results[:10]})

@login_required
def api_post_review(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

    try:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        slug = request.POST.get('slug')
        content_type_str = request.POST.get('content_type', 'movie')

        print(f"DEBUG → slug: {slug}, type: {content_type_str}, rating: {rating}")

        if not slug or not rating:
            return JsonResponse({'success': False, 'error': 'Missing slug or rating'})

        rating = int(rating)

        if content_type_str == 'series':
            content = models.Series.objects.get(slug=slug)
            review, created = models.Review.objects.update_or_create(
                user=request.user,
                series=content,
                defaults={'rating': rating, 'comment': comment}
            )
            print(f"Series Review {'created' if created else 'updated'} → ID: {review.id}")
            
            content.update_rating()
            
        else:
            content = models.Movie.objects.get(slug=slug)
            review, created = models.Review.objects.update_or_create(
                user=request.user,
                movie=content,
                defaults={'rating': rating, 'comment': comment}
            )
            print(f"Movie Review {'created' if created else 'updated'} → ID: {review.id}")
            
            content.update_rating()

        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully!',
            'rating': review.rating,
            'comment': review.comment,
            'overall_rating': float(content.overall_rating),
            'reviews_count': content.reviews.count()
        })

    except models.Series.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Series not found'})
    except models.Movie.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Movie not found'})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Rating must be a number'})
    except Exception as e:
        print("Error in api_post_review:", e)
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Internal server error'}, status=500) 


def update_all_ratings(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Admin only'})
    
    updated_movies = 0
    updated_series = 0
    
    for movie in models.Movie.objects.all():
        movie.update_rating()
        updated_movies += 1
    
    for series in models.Series.objects.all():
        series.update_rating()
        updated_series += 1
    
    return JsonResponse({
        'success': True,
        'message': f'Updated {updated_movies} movies and {updated_series} series'
    })     

# أضف هذين الـ view في نهاية views.py

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        email    = data.get('email', '').strip()
        password = data.get('password', '')

        user = models.authenticate_user(email, password)
        if user:
            from django.contrib.auth import login
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'id':         user.id,
                    'email':      user.email,
                    'first_name': user.first_name,
                    'last_name':  user.last_name,
                    'username':   user.username,
                }
            })
        return JsonResponse({'success': False, 'error': 'Invalid email or password'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)

        # نبني postData بنفس الشكل اللي register_validator يتوقعه
        post_data = {
            'first_name':    data.get('first_name', ''),
            'last_name':     data.get('last_name', ''),
            'email':         data.get('email', ''),
            'password':      data.get('password', ''),
            'confirm_pw':    data.get('password', ''),  # React بيبعت password مرة واحدة
            'date_of_birth': data.get('date_of_birth', ''),
        }

        errors = models.register_validator(post_data)
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        user = models.create_user(post_data)
        from django.contrib.auth import login
        login(request, user)
        return JsonResponse({
            'success': True,
            'user': {
                'id':         user.id,
                'email':      user.email,
                'first_name': user.first_name,
                'last_name':  user.last_name,
                'username':   user.username,
            }
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_me(request):
    """يرجع بيانات المستخدم الحالي"""
    if request.user.is_authenticated:
        return JsonResponse({
            'success': True,
            'user': {
                'id':         request.user.id,
                'email':      request.user.email,
                'first_name': request.user.first_name,
                'last_name':  request.user.last_name,
                'username':   request.user.username,
            }
        })
    return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

def api_movie_detail(request, slug):
    try:
        m = models.Movie.objects.get(slug=slug)
        return JsonResponse({
            'id': m.id, 'title': m.title, 'slug': m.slug,
            'description': m.description, 'get_poster_url': m.get_poster_url,
            'backdrop_path': m.backdrop_path, 'overall_rating': float(m.overall_rating),
            'release_year': m.release_year, 'duration': m.duration,
            'language': m.language, 'trailer_url': m.trailer_url,
            'content_type': m.content_type,
        })
    except models.Movie.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


def api_series_detail(request, slug):
    try:
        s = models.Series.objects.get(slug=slug)
        return JsonResponse({
            'id': s.id, 'title': s.title, 'slug': s.slug,
            'description': s.description, 'get_poster_url': s.get_poster_url,
            'backdrop_path': s.backdrop_path, 'overall_rating': float(s.overall_rating),
            'first_air_date': s.first_air_date, 'seasons_count': s.seasons_count,
            'language': s.language, 'trailer_url': s.trailer_url,
            'content_type': 'series',
        })
    except models.Series.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

@login_required
def api_my_reviews(request):
    reviews = models.Review.objects.filter(user=request.user).select_related('movie', 'series')

    data = []

    for r in reviews:
        if r.movie:
            content = r.movie
            poster = content.get_poster_url
            content_type = 'movie'
        else:
            content = r.series
            poster = content.get_poster_url
            content_type = 'series'

        data.append({
            'id': r.id,
            'rating': r.rating,
            'comment': r.comment,
            'title': content.title,
            'slug': content.slug,
            'type': content_type,
            'poster': poster,
        })

    return JsonResponse({
        'success': True,
        'reviews': data
    })



@csrf_exempt
def api_edit_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    user    = request.user
    profile = user.profile

    first_name   = request.POST.get('first_name', '').strip()
    last_name    = request.POST.get('last_name',  '').strip()
    email        = request.POST.get('email',      '').strip()
    avatar_file  = request.FILES.get('avatar')

    errors = {}
    if not first_name: errors['first_name'] = 'First name is required.'
    if not last_name:  errors['last_name']  = 'Last name is required.'
    if not email:      errors['email']      = 'Email is required.'

    if email and User.objects.exclude(pk=user.pk).filter(email=email).exists():
        errors['email'] = 'This email is already taken.'

    if errors:
        return JsonResponse({'success': False, 'error': ' '.join(errors.values())}, status=400)

    user.first_name = first_name
    user.last_name  = last_name
    user.email      = email
    if avatar_file:
        profile.avatar = avatar_file
        profile.save()
    user.save()

    return JsonResponse({
        'success': True,
        'user': {
            'id':         user.id,
            'email':      user.email,
            'first_name': user.first_name,
            'last_name':  user.last_name,
            'username':   user.username,
        }
    })




def api_reviews(request):
    slug = request.GET.get('slug')
    content_type = request.GET.get('content_type', 'movie')
    if not slug:
        return JsonResponse({'results': []})
    if content_type == 'series':
        reviews = models.Review.objects.filter(series__slug=slug).select_related('user')
    else:
        reviews = models.Review.objects.filter(movie__slug=slug).select_related('user')
    data = [{
        'id': r.id, 'rating': r.rating, 'comment': r.comment,
        'created_at': r.created_at.isoformat(),
        'user': {'id': r.user.id, 'username': r.user.username or r.user.email}
    } for r in reviews]
    return JsonResponse({'results': data})


@csrf_exempt
def api_user_reviews(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

    user = request.user
    reviews = []

    for review in models.Review.objects.filter(user=user, movie__isnull=False).select_related('movie'):
        m = review.movie
        reviews.append({
            'review': {
                'id':         review.id,
                'rating':     review.rating,
                'comment':    review.comment,
                'created_at': review.created_at.isoformat(),
            },
            'type':       'movie',
            'title':      m.title,
            'slug':       m.slug,
            'poster_url': m.get_poster_url,
            'year':       m.release_year,
        })

    
    for review in models.Review.objects.filter(user=user, series__isnull=False).select_related('series'):
        s = review.series
        reviews.append({
            'review': {
                'id':         review.id,
                'rating':     review.rating,
                'comment':    review.comment,
                'created_at': review.created_at.isoformat(),
            },
            'type':       'series',
            'title':      s.title,
            'slug':       s.slug,
            'poster_url': s.get_poster_url,
            'year':       s.first_air_date,
        })

    return JsonResponse({'success': True, 'reviews': reviews})


@csrf_exempt
def api_favorites(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

    favs = models.Favorite.objects.filter(
        user=request.user
    ).select_related('movie', 'series')

    movies = []
    series = []

    for fav in favs:
        if fav.movie:
            m = fav.movie
            movies.append({
                'id': m.id, 'title': m.title, 'slug': m.slug,
                'poster': m.get_poster_url,
                'rating': float(m.overall_rating),
                'year': m.release_year,
                'content_type': 'movie',
            })
        elif fav.series:
            s = fav.series
            series.append({
                'id': s.id, 'title': s.title, 'slug': s.slug,
                'poster': s.get_poster_url,
                'rating': float(s.overall_rating),
                'year': s.first_air_date,
                'content_type': 'series',
            })

    return JsonResponse({'success': True, 'movies': movies, 'series': series})

@csrf_exempt  
def api_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return JsonResponse({'success': True})


@method_decorator(csrf_exempt, name='dispatch')
class ToggleFavoriteView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            slug = data.get('slug')
            content_type = data.get('content_type', 'movie')
            
            print(f"ToggleFavoriteView: slug={slug}, type={content_type}")
            
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