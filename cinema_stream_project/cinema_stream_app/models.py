from django.db import models

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