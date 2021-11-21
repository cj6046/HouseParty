"""
Handle the creation and updating of spotify api tokens
"""

from requests import post, put, get
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET

BASE_URL = "https://api.spotify.com/v1/me/"

def update_or_create_user_tokens(session_id, refresh_token, access_token, expires_in, token_type):
    """Update current spotify token with new fields"""
    tokens = get_user_tokens(session_id)
    # print(expires_in)
    expires_in = timezone.now() + timedelta(seconds=expires_in)
    if tokens:
        tokens.refresh_token = refresh_token
        tokens.access_token = access_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['refresh_token', 'access_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyToken(user=session_id, refresh_token=refresh_token, access_token=access_token, token_type=token_type, expires_in=expires_in)
        tokens.save()

def get_user_tokens(session_id):
    """Return user tokens from SpotifyToken model"""
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None

def is_spotify_authenticated(session_id):
    """Return True if spotify token is still valid"""
    tokens = get_user_tokens(session_id)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(session_id)
        return True
    return False

def refresh_spotify_token(session_id):
    """Post new refresh token to spotify api"""
    refresh_token = get_user_tokens(session_id).refresh_token

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    refresh_token = response.get('refresh_token')

    update_or_create_user_tokens(session_id, refresh_token, access_token, expires_in, token_type)

def execute_spotify_api_request(session_id, endpoint, post_=False, put_=False):
    """Handle different types of requests to spotify api"""
    tokens = get_user_tokens(session_id)
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : "Bearer " + tokens.access_token
    }

    # Handle post request
    if post_:
        post(BASE_URL + endpoint, headers=headers)
    
    # Handle put request
    if put_:
        put(BASE_URL + endpoint, headers=headers)

    # Handle get request as default and transcribe info into json
    response = get(BASE_URL + endpoint, {}, headers=headers)
    try:
        return response.json()
    except:
        return {'Error' : 'Could not execute spotify api request'}