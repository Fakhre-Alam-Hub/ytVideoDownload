from django.urls import path
from Home import views

urlpatterns = [
    path('', views.index, name='home_index'),
    path('download/<str:addPrefix>/<str:counter>/<path:video_url>/<str:resolution>/', views.download_video, name='download_video'),
    path('playlist/', views.playlist, name='home_playlist'),
    path('about/', views.about, name='home_about'),
]

