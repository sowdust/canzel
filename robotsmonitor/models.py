from django_countries.fields import CountryField
from django.conf import settings
from django.urls import reverse
from django.db import models
from autoslug import AutoSlugField

import threading
import requests
import logging
import time
import re
import os

OK_STATUS_CODES = [200]

logger = logging.getLogger(__name__)


def parse_rules(text):
    rules = []
    status = 0
    for line in text.split('\n'):
        if re.match('\s*User-agent\s*:\s+\*\s*', line):
            status = 1
        else:
            if (status == 1):
                z = re.match('\s*Disallow\s*:\s*(.+)', line)
                if z:
                    rules.append(z.groups()[0])
                    continue
                if re.match('\s*User-agent\s*:\s+\*\s*', line):
                    break
    return set(rules)


# Create your models here.
class Media(models.Model):
    name = models.CharField(max_length=2083, help_text='Actual term(s) to be tracked')
    country = CountryField()
    homepage = models.URLField(max_length=2048, help_text='Media homepage URL')
    base_url = models.URLField(max_length=2048, help_text='Media base URL')
    slug = AutoSlugField(populate_from='name')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    disclaimer_button_xpath = models.CharField(max_length=255,
                                               help_text='XPath of the button/link to click to remove privacy disclaimer',
                                               default='//button[normalize-space()="Agree"]')
    inserted_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('media', args=[self.id])

    def get_live_entries(self):
        robots_url = self.base_url.rstrip('/') + '/robots.txt'
        rules = []
        try:
            r = requests.get(robots_url)
            if r.status_code not in OK_STATUS_CODES:
                logger.error('Could not get robots page %s: received %d status code' % (robots_url, r.status_code))
            rules = parse_rules(r.text)
        except Exception as ex:
            logger.error(ex)
        return rules

    def add_entry(self, content):
        entry = RobotsEntry(
            media=self,
            content=content)
        entry.save()
        try:
            r = requests.get(self.base_url.rstrip('/') + content)
            entry.set_status_code(r.status_code)
            if r.status_code in OK_STATUS_CODES and settings.SCREENSHOT:
                # t = threading.Thread(target=RobotsEntry.screenshot, args=(entry,))
                # t.start()
                entry.take_screenshot()
            if r.status_code in OK_STATUS_CODES and settings.ARCHIVE:
                t = threading.Thread(target=RobotsEntry.archive, args=(entry,))
                t.start()
                t.join()
            if r.status_code in OK_STATUS_CODES and settings.STORE_HTML:
                entry.store_html(r.text)
            if settings.TWITTER_NOTIFICATIONS:
                entry.twitter_notify()
        except Exception as ex:
            print(ex)
            logger.error(ex)

    def compare_entries(self):
        old_entries = self.robots_entries.values_list('content', flat=True)
        new_entries = self.get_live_entries()
        c = 0
        for rule in new_entries:
            if rule not in list(old_entries):
                self.add_entry(rule)
                c += 1
        return c

    def entries(self):
        entries = self.robots_entries.values_list('content')
        return entries

    def __str__(self):
        return self.name


class RobotsEntry(models.Model):
    media = models.ForeignKey('Media', null=True, on_delete=models.SET_NULL, related_name='robots_entries')
    content = models.CharField(max_length=2048, help_text='Entry content')
    status_code = models.PositiveSmallIntegerField(help_text='HTTP status', null=True)
    archive_url = models.URLField(max_length=2048, null=True, blank=True, help_text='URL of the archived page')
    archive_time = models.DateTimeField(null=True, blank=True)
    archive_oldest_url = models.URLField(max_length=2048, null=True, blank=True,
                                         help_text='URL of the oldest copy of the archived page')
    archive_oldest_time = models.DateTimeField(null=True, blank=True)
    screenshot = models.ImageField(upload_to='screenshots/', null=True)
    # screenshot_path = models.CharField(max_length=2049, null=True, blank=True)
    inserted_at = models.DateTimeField(auto_now_add=True)
    html = models.TextField(null=True, blank=True, help_text='HTML of the page')

    def url(self):
        return self.media.base_url.rstrip('/') + self.content

    def get_absolute_url(self):
        return reverse('robots_entry', args=[self.id])

    def set_status_code(self, status_code):
        self.status_code = int(status_code)
        self.save()

    def take_screenshot(self):
        import tempfile
        from selenium import webdriver
        from django.core.files import File
        from selenium.webdriver.chrome.service import Service
        url = self.url()
        path = '%s/%d.png' % (tempfile.gettempdir().rstrip('/'), self.id)
        options = webdriver.ChromeOptions()
        options.headless = True
        # most of the following are probably unnecessary
        # but now it works on a VPS
        chromeOptions.add_argument("--no-sandbox") 
        chromeOptions.add_argument("--disable-setuid-sandbox") 
        chromeOptions.add_argument("--remote-debugging-port=9222")
        chromeOptions.add_argument("--disable-dev-shm-using") 
        chromeOptions.add_argument("--disable-extensions") 
        chromeOptions.add_argument("--disable-gpu") 
        chromeOptions.add_argument("start-maximized") 
        chromeOptions.add_argument("disable-infobars")
        driver = webdriver.Chrome(service=Service(settings.CHROME_WEBDRIVER_PATH), options=options)
        logger.info('Taking screenshot of %s, saving it to %s' % (url, path))
        print('Taking screenshot of %s, saving it to %s' % (url, path))
        driver.get(url)
        time.sleep(1)
        try:
            accept_button = driver.find_element_by_xpath(self.media.disclaimer_button_xpath)
            accept_button.click()
        except Exception as ex:
            logger.error(ex)
        time.sleep(1)
        required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
        required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
        driver.set_window_size(required_width, required_height)
        el = driver.find_element_by_tag_name('body')
        el.screenshot(path)
        self.screenshot.save(
            os.path.basename('%d.png' % self.id),
            File(open(path, 'rb'))
        )
        self.save()
        driver.quit()

    def archive(self):
        import waybackpy
        wayback = waybackpy.Url(self.url(), settings.ARCHIVE_USERAGENT)
        logger.info("Archiving page %s" % self.url())
        archive = wayback.save()
        self.archive_url = archive.archive_url
        self.archive_time = archive.timestamp
        oldest_archive = wayback.oldest()
        self.archive_oldest_url = oldest_archive.archive_url
        self.archive_oldest_time = oldest_archive.timestamp
        logger.info("Archived at page %s" % self.archive_url)
        self.save()

    def store_html(self, html):
        self.html = html
        self.save()

    def __str__(self):
        return self.content

    def twitter_notify(self):
        import tweepy
        logger.info("Authenticating on Twitter")
        auth = tweepy.OAuthHandler(settings.TWITTER_API_KEY, settings.TWITTER_API_KEY_SECRET)
        auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        try:
            status = "The media %s has added a new entry to its robots: %s %s" % (
            self.media, self.url(), settings.BASE_URL.rstrip('/') + self.get_absolute_url())
            if self.screenshot.path is not None:
                posted_status = api.update_status_with_media(status, self.screenshot.path)
                logger.info("Posting status %s with media" % (status, self.screenshot.path))
            else:
                posted_status = api.update_status(status)
            logger.info("Posted status %s" % posted_status.id)
        except Exception as ex:
            logger.error(ex)
