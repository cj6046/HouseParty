"""
Handle the creation and updating of spotify api tokens
"""

from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta


def update_or_create_user_tokens(session_id, refresh_token, access_token, expires_in, token_type):
    tokens = get_user_tokens(session_id)
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
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None