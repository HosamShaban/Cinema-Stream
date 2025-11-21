from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home')
    path('browse/', views.browse, name='browse'),
    path('movie/<slug:slug>/', views.movie_detail, name='movie_detail'),
]