from datetime import date
import re
import bcrypt
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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
    tmdb_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    backdrop = models.ImageField(upload_to='backdrops/', blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    release_year = models.PositiveIntegerField(null=True, blank=True, default=2020)
    poster_path   = models.CharField(max_length=200, blank=True, null=True)
    backdrop_path = models.CharField(max_length=200, blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    language = models.CharField(max_length=50, default='English')
    is_premium = models.BooleanField(default=False)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='movie')
    genres = models.ManyToManyField(Genre, related_name='movies')
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_poster_url(self):
        if self.poster and hasattr(self.poster, 'url'):
            return self.poster.url
        
        elif self.poster_path:
            if self.poster_path.startswith('http'):
                return self.poster_path
            else:
                return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        
        return '/static/images/default_poster.jpg'


class Series(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    first_air_date = models.PositiveIntegerField(null=True, blank=True, default=2020)
    seasons_count = models.IntegerField(default=0)
    episodes_count = models.IntegerField(default=0)
    overall_rating = models.FloatField(default=0)
    genres = models.ManyToManyField(Genre, related_name='series', blank=True)
    language = models.CharField(max_length=100, default='English')
    poster_path = models.CharField(max_length=200, null=True, blank=True)
    backdrop_path = models.CharField(max_length=200, null=True, blank=True)
    poster = models.ImageField(upload_to='series_posters/', null=True, blank=True)
    backdrop = models.ImageField(upload_to='series_backdrops/', null=True, blank=True)
    trailer_url = models.URLField(null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    content_type = models.CharField(max_length=10, default='series') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    @property
    def get_poster_url(self):
        if self.poster and hasattr(self.poster, 'url'):
            return self.poster.url
        elif self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return '/static/images/default_poster.jpg'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews', null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 11)])
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('movie', 'user')

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, null=True, blank=True)
    series = models.ForeignKey('Series', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = [['user', 'movie'], ['user', 'series']]

    def __str__(self):
        if self.movie:
            return f"{self.user.username} - {self.movie.title}"
        elif self.series:
            return f"{self.user.username} - {self.series.title}"
        return f"{self.user.username} - Favorite"

    def clean(self):
        if self.movie and self.series:
            raise ValidationError("Favorite cannot have both movie and series")
        if not self.movie and not self.series:
            raise ValidationError("Favorite must have either movie or series")

def register_validator(postData, avatar_file=None):
    errors = {}
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    today = date.today()

    if len(postData['first_name']) < 2 or not postData['first_name'].isalpha():
        errors['first_name'] = "First name must be at least 2 letters."

    if len(postData['last_name']) < 2 or not postData['last_name'].isalpha():
        errors['last_name'] = "Last name must be at least 2 letters."

    if not EMAIL_REGEX.match(postData['email']):
        errors['email'] = "Invalid email format."
    elif User.objects.filter(email=postData['email']).exists():
        errors['email_unique'] = "Email already registered."

    if len(postData['password']) < 8:
        errors['password'] = "Password must be at least 8 characters."

    if postData['password'] != postData['confirm_pw']:
        errors['confirm_pw'] = "Passwords do not match."

    try:
        dob = postData.get('date_of_birth')
        if dob:
            year, month, day = map(int, dob.split('-'))
            dob_date = date(year, month, day)
            age = today.year - dob_date.year - ((today.month, today.day) < (month, day))
            if age < 15:
                errors['date_of_birth'] = "You must be at least 15 years old."
            if dob_date > today:
                errors['date_of_birth'] = "Date of birth cannot be in the future."
    except:
        errors['date_of_birth'] = "Invalid date format."

    if avatar_file:
        if avatar_file.size > 5 * 1024 * 1024:
            errors['avatar'] = "Image size should not exceed 5MB."
        if not avatar_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            errors['avatar'] = "Only PNG, JPG, JPEG, GIF allowed."

    return errors


def create_user(postData, avatar_file=None):
    username = postData['email']
    
    counter = 1
    base_username = username
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    user = User.objects.create_user(
        username=username,
        email=postData['email'],
        password=postData['password'],
        first_name=postData['first_name'],
        last_name=postData['last_name']
    )

    UserProfile.objects.create(
        user=user,
        date_of_birth=postData.get('date_of_birth'),
        avatar=avatar_file if avatar_file else None
    )
    return user

def authenticate_user(email, password):
    user = User.objects.filter(email=email).first()
    if user and bcrypt.checkpw(password.encode(), user.password.encode()):
        return user
    return None

def get_logged_user(request):
    if "user_id" in request.session:
        try:
            return User.objects.get(id=request.session['user_id'])
        except User.DoesNotExist:
            return None
    return None


def get_all_movies():
    return Movie.objects.all().order_by('-created_at')

def get_trending_movies():
    return Movie.objects.all().order_by('-rating_count')[:10]

def get_top_movies_by_language(language, limit=8):
    return Movie.objects.filter(language=language).order_by('-overall_rating')[:limit]

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
        movie.overall_rating = round(avg, 2)
        movie.rating_count = reviews.count()
    else:
        movie.overall_rating = 0.00
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
            filters['release_year'] = int(year)
        except:
            pass

    if content_type in ['movie', 'series']:
        filters['content_type'] = content_type

    return Movie.objects.filter(**filters).distinct()

def get_poster_url(self):
        if self.poster:
            return self.poster.url
        elif self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return '/static/default_poster.jpg'

def get_poster_url(self):
        if self.poster and hasattr(self.poster, 'url'):
            return self.poster.url
        elif self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return '/static/default_poster.jpg'