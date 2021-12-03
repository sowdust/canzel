from django.shortcuts import render, get_object_or_404
from .models import Media, RobotsEntry

def index(request):
	return medias(request)

def medias(request):
	medias = Media.objects.all()
	context = {'medias' : medias}
	return render(request, 'medias.html', context)

def media(request, slug):
	media = get_object_or_404(Media, slug=slug)
	entries = media.robots_entries.all()
	context = {'media': media, 'entries': entries}
	return render(request, 'media.html', context)

def robots_entry(request, entry_id):
	entry = get_object_or_404(RobotsEntry, pk=entry_id)
	context = {'entry' : entry}
	return render(request, 'entry.html', context)

def about(request):
	return render(request, 'about.html')