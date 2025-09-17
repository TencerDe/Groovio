from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .spotify_api_utils import get_spotify_auth_url, get_spotify_tokens, get_user_profile, refresh_spotify_token
# Create your views here.



