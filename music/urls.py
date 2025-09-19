from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.home, name='home'),
    path('login/spotify/', views.spotify_login, name = 'spotify_login'),
    path('callback/', views.spotify_call_back, name='spotify_call_back'),
    path('logout/spotify/', views.spotify_logout, name='spotify_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search, name='search'),
]