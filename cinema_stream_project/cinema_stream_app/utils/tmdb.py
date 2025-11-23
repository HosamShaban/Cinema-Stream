import requests
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"

def tmdb_request(endpoint, params=None):
    default_params = {"api_key": settings.TMDB_API_KEY}
    if params:
        default_params.update(params)
    
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, params=default_params)
    response.raise_for_status()
    return response.json()

def get_popular_movies(page=1):
    return tmdb_request("/movie/popular", {"page": page})

def get_movie_details(tmdb_id):
    return tmdb_request(f"/movie/{tmdb_id}", {"append_to_response": "videos,credits"})