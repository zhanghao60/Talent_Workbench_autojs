# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 示例：当 client_id 为 abc123 时，完整请求路径为 consumers/forward/abc123/
    path('forward/<str:client_id>/', views.forward_to_specific_websocket, name='forward_to_specific'),  #路由格式：consumers/forward/{client_id}/  
]