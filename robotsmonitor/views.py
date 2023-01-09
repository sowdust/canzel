from django.shortcuts import render, get_object_or_404
from django_countries.fields import Country
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from .models import Media, RobotsEntry

def index(request):
	return medias(request)

@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: *",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def robots_entries(request):
	entries = RobotsEntry.objects.order_by('-inserted_at')
	paginator = Paginator(entries, 50)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	return render(request, 'entries.html', {'entries': page_obj})

def robots_entries_country(request, country):
	entries = RobotsEntry.objects.filter(media__country=country).order_by('-inserted_at')
	paginator = Paginator(entries, 50)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	return render(request, 'entries.html', {'entries': page_obj})

def countries(request):
	medias = Media.objects.all()
	country_codes = medias.order_by().values_list('country', flat=True).distinct()
	countries = [Country(code) for code in country_codes]
	context = {'countries' : countries}
	return render(request, 'countries.html', context)

def medias(request):
	medias = Media.objects.all()
	context = {'medias' : medias}
	return render(request, 'medias.html', context)

def medias_country(request,country):
	medias = Media.objects.filter(country=country)
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

def rss_index(request):
	medias = Media.objects.all()
	country_codes = medias.order_by().values_list('country', flat=True).distinct()
	countries = [Country(code) for code in country_codes]
	context = {'medias' : medias, 'countries' : countries}
	return render(request, 'rss.html', context)

def search(request):
	if request.method == 'GET':
		return render(request, 'search.html')

	field = request.POST.get('field')
	text = request.POST.get('text')
	if field == 'title':
		objects = RobotsEntry.objects.filter(title__contains=text)
	elif field == 'url':
		objects = RobotsEntry.objects.filter(content__contains=text)
	elif field == 'html':
		objects = RobotsEntry.objects.filter(html__contains=text)
	else:
		objects = []
	paginator = Paginator(objects, 50)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	return render(request, 'entries.html', {'entries': page_obj})

