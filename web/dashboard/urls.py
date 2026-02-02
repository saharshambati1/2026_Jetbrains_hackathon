from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/macro/', views.api_macro, name='api_macro'),
    path('api/predictor/', views.api_predictor, name='api_predictor'),
    path('api/chat/', views.api_chat, name='api_chat'),
]
