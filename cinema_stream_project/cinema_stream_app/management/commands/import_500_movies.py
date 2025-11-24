import urllib.request
from django.core.management.base import BaseCommand
from django.core.files.temp import NamedTemporaryFile
from cinema_stream_app.utils.tmdb import get_popular_movies, get_movie_details
from cinema_stream_app.models import Movie, Genre
from datetime import datetime
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import 500+ movies from TMDB slug'

    def handle(self, *args, **options):
        added = 0
        for page in range(1, 26):
            self.stdout.write(f"load {page}...")
            data = get_popular_movies(page)
            
            for item in data['results']:
                if Movie.objects.filter(tmdb_id=item['id']).exists():
                    continue

                details = get_movie_details(item['id'])

                release_date_str = item.get('release_date')
                if release_date_str:
                    try:
                        release_year = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                    except:
                        release_year = datetime.now().date()
                else:
                    release_year = datetime.now().date()

                base_slug = slugify(item['title'])
                slug = base_slug
                counter = 1
                while Movie.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{item['id']}" if counter > 5 else f"{base_slug}-{counter}"
                    counter += 1

                movie = Movie(
                    tmdb_id=item['id'],
                    title=item['title'],
                    slug=slug,
                    description=item.get('overview') or "No description available.",
                    release_year=release_year,
                    duration=details.get('runtime', 120) or 120,
                    overall_rating=round(item.get('vote_average', 0), 2),
                    rating_count=0,
                    language="English",
                    is_premium=False,
                    content_type='movie',
                )
                movie.save()

                for g in details.get('genres', []):
                    genre, _ = Genre.objects.get_or_create(
                        name=g['name'],
                        defaults={'slug': slugify(g['name']), 'description': ''}
                    )
                    movie.genres.add(genre)

                videos = details.get('videos', {}).get('results', [])
                for vid in videos:
                    if vid['site'] == 'YouTube' and vid['type'] == 'Trailer':
                        movie.trailer_url = f"https://www.youtube.com/watch?v={vid['key']}"
                        movie.save()
                        break

                if item.get('poster_path'):
                    try:
                        poster_url = f"https://image.tmdb.org/t/p/w500{item['poster_path']}"
                        img_temp = NamedTemporaryFile(delete=True)
                        img_temp.write(urllib.request.urlopen(poster_url).read())
                        img_temp.flush()
                        movie.poster.save(f"poster_{item['id']}.jpg", img_temp, save=False)
                    except:
                        pass

                if item.get('backdrop_path'):
                    try:
                        backdrop_url = f"https://image.tmdb.org/t/p/original{item['backdrop_path']}"
                        img_temp = NamedTemporaryFile(delete=True)
                        img_temp.write(urllib.request.urlopen(backdrop_url).read())
                        img_temp.flush()
                        movie.backdrop.save(f"backdrop_{item['id']}.jpg", img_temp, save=False)
                    except:
                        pass

                movie.save()
                added += 1
                self.stdout.write(self.style.SUCCESS(f"done {added}: {movie.title} ({release_year.year})"))

                if added >= 500:
                    self.stdout.write(self.style.SUCCESS("done add 500 movies"))
                    return

        self.stdout.write(self.style.SUCCESS(f"done {added} movies"))