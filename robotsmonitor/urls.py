from django.urls import path
from . import views
from .models import LatestEntriesFeed, CountryFeed, MediaFeed

urlpatterns = [
#    path('', views.index, name='index'),
    path('', views.robots_entries, name='index'),
    path('websites/', views.medias, name='medias'),
    path('website/<slug:slug>/', views.media, name='media'),
    path('entry/<int:entry_id>/', views.robots_entry, name='robots_entry'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('feed/', views.rss_index, name='rss_index'),
    path('feed/rss/', LatestEntriesFeed(), name='all_feed'),
    path('feed/rss/country/<str:country>/', CountryFeed(), name='country_feed'),
    path('feed/rss/website/<slug:media_slug>/', MediaFeed(), name='media_feed'),

]