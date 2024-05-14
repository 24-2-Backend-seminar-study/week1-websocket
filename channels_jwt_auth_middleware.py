import base64
from channels.db import database_sync_to_async
import traceback

from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.auth.models import User

from jwt import decode
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError

class ChannelsJWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    @database_sync_to_async
    def get_user(self, user_id):
      try:
        return User.objects.get(id=user_id)
      except User.DoesNotExist:
        return AnonymousUser()

    async def get_logged_in_user(self, user_id):
        user = await self.get_user(user_id)
        return user
    
    async def __call__(self, scope, receive, send):
      header = dict(scope['headers'])
      try:
        access_token = header[b'cookie'].decode().split('; ')[-1][len('access_token='):]
        user_info = decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        user = await self.get_logged_in_user(user_info['user_id'])
        scope['user'] = user
      except (InvalidSignatureError, KeyError, ExpiredSignatureError, DecodeError):
          traceback.print_exc()
          scope['user'] = AnonymousUser()
      except:
          scope['user'] = AnonymousUser()
      return await self.app(scope, receive, send)

def ChannelsJWTAuthMiddlewareStack(app):
    return ChannelsJWTAuthMiddleware(AuthMiddlewareStack(app))