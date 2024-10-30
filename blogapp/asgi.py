import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from blog.routing import websocket_urlpatterns  # Import your WebSocket routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogapp.settings')

# Create the ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(  # Handles WebSocket connections
        URLRouter(
            websocket_urlpatterns  # Your defined WebSocket URL patterns
        )
    ),
})
