from django.db import models
from django.contrib.auth.models import User

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Movie(models.Model):
    CONTENT_TYPES = (('movie', 'Movie'), ('series', 'Series'))

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=210, unique=True)
    description = models.TextField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    backdrop = models.ImageField(upload_to='backdrops/', blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    release_year = models.DateField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    language = models.CharField(max_length=50,default='English')
    is_premium = models.BooleanField(default=False)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='movie')
    genres = models.ManyToManyField(Genre, related_name='movies')
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('movie', 'user')

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'movie')

def get_all_movies():
    return Movie.objects.all().order_by('-created_at')

def get_trending_movies():
    return Movie.objects.all().order_by('-rating_count')[:10]

def get_movie_by_slug(slug):
    return Movie.objects.get(slug=slug)

def add_to_favorites(user, movie):
    return Favorite.objects.get_or_create(user=user, movie=movie)

def remove_from_favorites(user, movie):
    Favorite.objects.filter(user=user, movie=movie).delete()

def is_favorite(user, movie):
    return Favorite.objects.filter(user=user, movie=movie).exists()

def create_review(user, movie, rating, comment):
    review, created = Review.objects.update_or_create(
        user=user, movie=movie,
        defaults={'rating': rating, 'comment': comment}
    )
    update_movie_rating(movie)
    return review

def update_movie_rating(movie):
    reviews = movie.reviews.all()
    if reviews.exists():
        avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
        count = reviews.count()
        movie.average_rating = round(avg, 2)
        movie.rating_count = count
    else:
        movie.average_rating = 0.00
        movie.rating_count = 0
    movie.save()

def search_movies(query):
    return Movie.objects.filter(
        models.Q(title__icontains=query) | 
        models.Q(description__icontains=query)
    )

def filter_movies(genre=None, year=None, content_type=None):
    filters = {}
    if genre:
        filters['genres__slug'] = genre
    if year:
        try:
            filters['release_date__year'] = int(year)
        except ValueError:
            pass
    if content_type in ['movie', 'series']:
        filters['content_type'] = content_type

    return Movie.objects.filter(**filters).distinct()