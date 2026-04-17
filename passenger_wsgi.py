from asgiref.wsgi import WsgiToAsgi
from app.main import app as fastapi_app

application = WsgiToAsgi(fastapi_app)