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
    path('api/review/', views.api_post_review, name='api_post_review'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
]