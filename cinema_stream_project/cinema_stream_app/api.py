from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Movie, Favorite

def api_toggle_favorite(request):
    slug = request.POST.get('slug')
    if not slug:
        return JsonResponse({'success': False, 'message': 'Slug is required'}, status=400)

    movie = get_object_or_404(Movie, slug=slug)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        favorite.delete()
        action = "removed"
    else:
        action = "added"

    return JsonResponse({
        'success': True,
        'action': action,
        'is_favorite': created,
        'total_favorites': movie.favorite_set.count(),
        'message': f"Movie {action} to favorites!"
    })