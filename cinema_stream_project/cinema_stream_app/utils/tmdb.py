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