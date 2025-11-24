import os
import ssl
import urllib.request
from datetime import datetime
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from urllib3.exceptions import InsecureRequestWarning

from cinema_stream_app.models import Movie, Series, Genre
from cinema_stream_app.utils.tmdb import (
    get_popular_movies, get_movie_details,
    get_popular_tv, get_tv_details
)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Command(BaseCommand):
    help = 'Import 500 movies + 300 TV series from TMDB | Use --fix-images to repair missing posters'

    def add_arguments(self, parser):
        parser.add_argument('--fix-images', action='store_true', help='Fix missing poster/backdrop images')
        parser.add_argument('--fix-movie-paths', action='store_true', help='Fix missing poster_path and backdrop_path for movies')

    def handle(self, *args, **options):
        if options['fix_images']:
            self.fix_missing_images()
            return
            
        if options['fix_movie_paths']:
            self.fix_movie_paths()
            return

        movies_added = 0
        series_added = 0

        self.stdout.write("Starting to import movies...")
        for page in range(1, 26):
            try:
                self.stdout.write(f"Fetching movies - page {page}")
                data = get_popular_movies(page)
                
                if not data or 'results' not in data:
                    self.stdout.write(self.style.WARNING(f"No data found for movies page {page}"))
                    continue

                for item in data['results']:
                    try:
                        if Movie.objects.filter(tmdb_id=item['id']).exists():
                            continue

                        details = get_movie_details(item['id'])

                        release_date = item.get('release_date')
                        release_year = 2020
                        if release_date:
                            try:
                                release_year = datetime.strptime(release_date, '%Y-%m-%d').year
                            except:
                                release_year = 2020

                        base_slug = slugify(item['title'])
                        slug = base_slug
                        counter = 1
                        while Movie.objects.filter(slug=slug).exists():
                            slug = f"{base_slug}-{counter}"
                            counter += 1

                        movie = Movie(
                            tmdb_id=item['id'],
                            title=item['title'],
                            slug=slug,
                            description=item.get('overview') or "No description available.",
                            release_year=release_year or 2020,
                            duration=details.get('runtime') or 120,
                            overall_rating=round(item.get('vote_average', 0), 2),
                            language=item.get('original_language', 'en').upper(),
                            is_premium=False,
                            content_type='movie',
                            poster_path=item.get('poster_path'),
                            backdrop_path=item.get('backdrop_path')
                        )
                        movie.save()

                        for g in details.get('genres', []):
                            genre, _ = Genre.objects.get_or_create(
                                name=g['name'],
                                defaults={'slug': slugify(g['name'])}
                            )
                            movie.genres.add(genre)

                        for vid in details.get('videos', {}).get('results', []):
                            if vid['site'] == 'YouTube' and vid['type'] == 'Trailer':
                                movie.trailer_url = f"https://www.youtube.com/watch?v={vid['key']}"
                                movie.save()
                                break

                        if item.get('poster_path'):
                            self.download_image(
                                f"https://image.tmdb.org/t/p/w500{item['poster_path']}",
                                movie, 'poster',
                                f"movie_poster_{item['id']}.jpg"
                            )
                        if item.get('backdrop_path'):
                            self.download_image(
                                f"https://image.tmdb.org/t/p/original{item['backdrop_path']}",
                                movie, 'backdrop',
                                f"movie_backdrop_{item['id']}.jpg"
                            )

                        movies_added += 1
                        self.stdout.write(self.style.SUCCESS(f"Added movie {movies_added}: {movie.title}"))

                        if movies_added >= 10:
                            break
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing movie {item.get('title', 'Unknown')}: {str(e)}"))
                        continue

                if movies_added >= 10:
                    break
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching movies page {page}: {str(e)}"))
                continue

        self.stdout.write("Starting to import TV series...")
        for page in range(1, 16):
            try:
                self.stdout.write(f"Fetching TV series - page {page}")
                data = get_popular_tv(page)
                
                if not data or 'results' not in data:
                    self.stdout.write(self.style.WARNING(f"No data found for TV page {page}"))
                    continue

                for item in data['results']:
                    try:
                        if Series.objects.filter(tmdb_id=item['id']).exists():
                            continue

                        details = get_tv_details(item['id'])

                        first_air = item.get('first_air_date')
                        first_air_date = 2020
                        if first_air:
                            try:
                                first_air_date = datetime.strptime(item['first_air_date'], '%Y-%m-%d').year
                            except:
                                first_air_date = 2020

                        base_slug = slugify(item['name'])
                        slug = base_slug
                        counter = 1
                        while Series.objects.filter(slug=slug).exists():
                            slug = f"{base_slug}-{counter}"
                            counter += 1

                        series = Series(
                            tmdb_id=item['id'],
                            title=item['name'],
                            slug=slug,
                            description=item.get('overview') or "No description available.",
                            first_air_date=first_air_date,
                            overall_rating=round(item.get('vote_average', 0), 2),
                            seasons_count=details.get('number_of_seasons', 0),
                            episodes_count=details.get('number_of_episodes', 0),
                            language=item.get('original_language', 'en').upper(),
                            is_premium=False,
                            content_type='series',
                            poster_path=item.get('poster_path'),
                            backdrop_path=item.get('backdrop_path')
                        )
                        series.save()

                        for g in details.get('genres', []):
                            genre, _ = Genre.objects.get_or_create(
                                name=g['name'],
                                defaults={'slug': slugify(g['name'])}
                            )
                            series.genres.add(genre)

                        if item.get('poster_path'):
                            self.download_image(
                                f"https://image.tmdb.org/t/p/w500{item['poster_path']}",
                                series, 'poster',
                                f"series_poster_{item['id']}.jpg"
                            )
                        if item.get('backdrop_path'):
                            self.download_image(
                                f"https://image.tmdb.org/t/p/original{item['backdrop_path']}",
                                series, 'backdrop',
                                f"series_backdrop_{item['id']}.jpg"
                            )

                        series_added += 1
                        self.stdout.write(self.style.SUCCESS(f"Added series {series_added}: {series.title}"))

                        if series_added >= 300:
                            break
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing series {item.get('name', 'Unknown')}: {str(e)}"))
                        continue

                if series_added >= 300:
                    break
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching TV page {page}: {str(e)}"))
                continue

        self.stdout.write(self.style.SUCCESS(
            f"Import completed!\nMovies: {movies_added} | Series: {series_added} | Total: {movies_added + series_added}"
        ))

    def download_image(self, url, instance, field_name, filename):
        try:
            self.stdout.write(f"Downloading: {url}")

            response = requests.get(url, stream=True, verify=False, timeout=30)
            response.raise_for_status()

            img_temp = NamedTemporaryFile(delete=True, suffix='.jpg')
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    img_temp.write(chunk)
            img_temp.seek(0)

            getattr(instance, field_name).save(filename, File(img_temp), save=True)
            self.stdout.write(self.style.SUCCESS(f"Success: {filename}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed {filename}: {e}"))

    def fix_missing_images(self):
        self.stdout.write(self.style.SUCCESS("Fixing missing images..."))

        for movie in Movie.objects.all():
            if (not movie.poster or (movie.poster and not os.path.exists(movie.poster.path))) and movie.poster_path:
                url = f"https://image.tmdb.org/t/p/w500{movie.poster_path}"
                filename = f"movie_poster_{movie.tmdb_id}.jpg"
                self.download_image(url, movie, 'poster', filename)

            if (not movie.backdrop or (movie.backdrop and not os.path.exists(movie.backdrop.path))) and movie.backdrop_path:
                url = f"https://image.tmdb.org/t/p/original{movie.backdrop_path}"
                filename = f"movie_backdrop_{movie.tmdb_id}.jpg"
                self.download_image(url, movie, 'backdrop', filename)

        for series in Series.objects.all():
            if (not series.poster or (series.poster and not os.path.exists(series.poster.path))) and series.poster_path:
                url = f"https://image.tmdb.org/t/p/w500{series.poster_path}"
                filename = f"series_poster_{series.tmdb_id}.jpg"
                self.download_image(url, series, 'poster', filename)

            if (not series.backdrop or (series.backdrop and not os.path.exists(series.backdrop.path))) and series.backdrop_path:
                url = f"https://image.tmdb.org/t/p/original{series.backdrop_path}"
                filename = f"series_backdrop_{series.tmdb_id}.jpg"
                self.download_image(url, series, 'backdrop', filename)

        self.stdout.write(self.style.SUCCESS("All missing images fixed successfully!"))

    def fix_movie_paths(self):
        self.stdout.write("Fixing movie paths from TMDB...")
    
        for movie in Movie.objects.filter(poster_path__isnull=True):
            try:
                self.stdout.write(f"Fetching details for: {movie.title} (TMDB: {movie.tmdb_id})")
                details = get_movie_details(movie.tmdb_id)
            
                if details.get('poster_path'):
                    movie.poster_path = details['poster_path']
                    self.stdout.write(f"✓ Updated poster_path: {details['poster_path']}")
            
                if details.get('backdrop_path'):
                    movie.backdrop_path = details['backdrop_path']
                    self.stdout.write(f"✓ Updated backdrop_path: {details['backdrop_path']}")
            
                movie.save()
            
                if movie.poster_path and not movie.poster:
                    self.download_image(
                        f"https://image.tmdb.org/t/p/w500{movie.poster_path}",
                        movie, 'poster',
                        f"movie_poster_{movie.tmdb_id}.jpg"
                    )
            
                if movie.backdrop_path and not movie.backdrop:
                    self.download_image(
                        f"https://image.tmdb.org/t/p/original{movie.backdrop_path}",
                        movie, 'backdrop',
                        f"movie_backdrop_{movie.tmdb_id}.jpg"
                    )
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed for {movie.title}: {e}"))