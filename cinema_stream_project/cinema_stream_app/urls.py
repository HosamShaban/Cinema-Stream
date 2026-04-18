from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('browse/', views.browse, name='browse'),
    path('series/<slug:slug>/', views.series_detail, name='series_detail'),
    path('movie/<str:slug>/', views.movie_detail, name='movie_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('movie/<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('movie/<slug:slug>/review/', views.add_review, name='add_review'),
    path('api/review/<int:review_id>/delete/', views.api_delete_review, name='api_delete_review'),
    path('about/', views.about, name='about'),
    path('api/favorite/toggle/', views.ToggleFavoriteView.as_view(), name='api_toggle_favorite'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('api/update-ratings/', views.update_all_ratings, name='update_ratings'),
    path('api/movies/', views.api_movies, name='api_movies'),
    path('api/trending/', views.api_trending, name='api_trending'),
   
    path('api/favorites/', views.api_favorites, name='api_favorites'),
    path('api/my-reviews/', views.api_my_reviews, name='api_my_reviews'),
    path('api/auth/login/',    views.api_login,    name='api_login'),
    path('api/auth/register/', views.api_register, name='api_register'),
    path('api/auth/me/',       views.api_me,       name='api_me'),
    path('api/auth/logout/',   views.api_logout,   name='api_logout'),
    path('api/movie/<slug:slug>/',  views.api_movie_detail,  name='api_movie_detail'),
    path('api/series/<slug:slug>/', views.api_series_detail, name='api_series_detail'),
   path('api/review/', views.api_reviews, name='api_reviews'),
path('api/review/submit/', views.api_post_review, name='api_post_review'),  # POST - إرسال review
path('api/review/<int:review_id>/delete/', views.api_delete_review, name='api_delete_review'),
path('api/user-reviews/', views.api_user_reviews, name='api_user_reviews'),
path('api/auth/edit-profile/', views.api_edit_profile, name='api_edit_profile'),
path('api/home/', views.api_home, name='api_home'),
path('api/browse/', views.api_browse, name='api_browse'),


]