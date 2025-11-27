import requests
from django.conf import settings

TMDB_API_KEY = settings.TMDB_API_KEY
BASE_URL = "https://api.themoviedb.org/3"

def get_popular_movies(page=1):
    try:
        url = f"{BASE_URL}/movie/popular"
        params = {
            "api_key": TMDB_API_KEY, 
            "page": page,
            "language": "en-US"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching popular movies: {e}")
        return {"results": []}

def get_movie_details(movie_id):
    try:
        url = f"{BASE_URL}/movie/{movie_id}"
        params = {
            "api_key": TMDB_API_KEY, 
            "append_to_response": "videos,credits"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie details {movie_id}: {e}")
        return {}

def get_popular_tv(page=1):
    try:
        url = f"{BASE_URL}/tv/popular"
        params = {
            "api_key": TMDB_API_KEY, 
            "page": page,
            "language": "en-US"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching popular TV: {e}")
        return {"results": []}

def get_tv_details(tv_id):
    try:
        url = f"{BASE_URL}/tv/{tv_id}"
        params = {
            "api_key": TMDB_API_KEY,
            "append_to_response": "videos,credits"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching TV details {tv_id}: {e}")
        return {}
    

def get_trailer_url(tmdb_id, content_type='movie'):
    try:
        type_path = "movie" if content_type == 'movie' else "tv"
        url = f"{BASE_URL}/{type_path}/{tmdb_id}/videos"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        trailers = [
            v for v in data.get('results', [])
            if v['site'] == 'YouTube' and v['type'] == 'Trailer'
        ]

        official = [t for t in trailers if 'official' in t['name'].lower()]
        if official:
            key = official[0]['key']
        elif trailers:
            key = trailers[0]['key']
        else:
            return None

        return f"https://www.youtube.com/embed/{key}?autoplay=1&rel=0&modestbranding=1&showinfo=0"

    except Exception as e:
        print(f"Error fetching trailer for {tmdb_id}: {e}")
        return None