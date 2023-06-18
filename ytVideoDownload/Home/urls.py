from django.urls import path
from Home import views

urlpatterns = [
    path('', views.index, name='home_index'),
    path('download/<path:video_url>/<str:resolution>/', views.download_video, name='download_video'),
    path('about/', views.about, name='home_about'),
]

