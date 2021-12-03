from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('websites/', views.medias, name='medias'),
    path('website/<slug:slug>/', views.media, name='media'),
    path('entry/<int:entry_id>/', views.robots_entry, name='robots_entry'),
    path('about/', views.about, name='about'),
]