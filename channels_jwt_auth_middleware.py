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
  """
  Middleware class for JWT authentication in Channels.

  This middleware extracts the JWT token from the request headers, decodes it,
  and retrieves the logged-in user based on the user ID stored in the token.
  The user object is then added to the scope for further processing.

  If the token is invalid or expired, or if an error occurs during the decoding
  process, the user is set to AnonymousUser.

  Args:
    app (callable): The next application or middleware in the chain.

  Attributes:
    app (callable): The next application or middleware in the chain.
  """

  def __init__(self, app):
    self.app = app

  @database_sync_to_async
  def get_user(self, user_id):
    """
    Retrieve the user object based on the user ID.

    This method is executed asynchronously to perform a database query
    to retrieve the user object based on the provided user ID.

    Args:
      user_id (int): The ID of the user.

    Returns:
      User: The user object if found, otherwise AnonymousUser.
    """
    try:
      return User.objects.get(id=user_id)
    except User.DoesNotExist:
      return AnonymousUser()

  async def get_logged_in_user(self, user_id):
    """
    Retrieve the logged-in user based on the user ID.

    This method calls the `get_user` method asynchronously to retrieve
    the user object based on the provided user ID.

    Args:
      user_id (int): The ID of the user.

    Returns:
      User: The logged-in user object.
    """
    user = await self.get_user(user_id)
    return user

  async def __call__(self, scope, receive, send):
    """
    Process the incoming request.

    This method is called for each incoming request and performs the following steps:
    1. Extract the access token from the request headers.
    2. Decode the access token using the secret key.
    3. Retrieve the logged-in user based on the user ID stored in the token.
    4. Add the user object to the scope for further processing.
    5. If any error occurs during the decoding process, set the user to AnonymousUser.

    Args:
      scope (dict): The ASGI scope dictionary.
      receive (callable): The ASGI receive function.
      send (callable): The ASGI send function.

    Returns:
      coroutine: The response from the next application or middleware in the chain.
    """
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