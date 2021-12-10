# -*- coding: utf-8 -*- 
 
import logging
import django 
import os 
import sys 
 
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')) 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canzelculture.settings") 
django.setup() 

from robotsmonitor.models import Media, RobotsEntry

#logging.info("Updating robots.txt rules")

medias = Media.objects.filter(enabled=True)
for m in medias:
    logging.info("[%s] Updating robots entries..." % m.name)
    new_entries = m.compare_entries()
    if new_entries > 0:
        logging.info('Found %d new entries for %s' % (new_entries, m.name))
        print('Found %d new entries for %s' % (new_entries, m.name))
    logging.info("[%s] Added %d new entries" % (m.name, new_entries))
