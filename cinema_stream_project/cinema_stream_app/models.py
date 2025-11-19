from datetime import date
import re
import bcrypt
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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True)
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

def register_validator(postData,avatar_file=None):
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
    except (ValueError, AttributeError):
        errors['date_of_birth'] = "Invalid date format."

    if avatar_file:
        if avatar_file.size > 5 * 1024 * 1024:
            errors['avatar'] = "Image size should not exceed 5MB."
        if not avatar_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            errors['avatar'] = "Only PNG, JPG, JPEG, GIF allowed."       

    return errors

def create_user(postData):
    pw_hash = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt()).decode()
    user = User.objects.create(
        first_name=postData['first_name'],
        last_name=postData['last_name'],
        email=postData['email'],
        password=pw_hash
    )
    return user

def authenticate_user(email, password):
    user = User.objects.filter(email=email).first()
    if user and bcrypt.checkpw(password.encode(), user.password.encode()):
        return user
    return None

def get_logged_user(request):
    if "user_id" in request.session:
        return User.objects.get(id=request.session['user_id'])
    return None


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