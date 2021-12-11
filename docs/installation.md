---
layout: page
title: Install
nav_order: 2
description: "How to install Canzel."
permalink: /install/
---

# Getting started

Canzel is a web application based on django.

## Requirements 

Canzel is written in Python 3 and uses the following python libraries:

 - django
 - django-countries
 - django-autoslug
 - waybackpy (not necessary: used to archive webpages)
 - pillow (not necessary: used to take screenshots)
 - selenium (not necessary: used to take screenshots)
 - tweepy ( (not necessary: used to post tweets)

## Installation


```bash
git clone https://github.com/sowdust/canzel.git
pip install -r requirements.txt
```


## Set up the application

You can configure some entries in the file settings.py. Also, remember to **change the default value of SECRET_KEY** with any random string of that length (50 characters - no whitespaces).

Prepare the database and create an admin user:
```bash
python manage.py makemigrations
python manage.py makemigrations robotsmonitor
python manage.py migrate
python manage.py createsuperuser
# Follow the instructions to create one admin user
```

Set up a cron job for the user running the web application that executes the script scripts/update_rules.py

Now go to the admin section and set up the websites (called "Media") you want to monitor.


## Screenshots

When running the application on a VPS, it might be difficult to take screenshots of live pages using selenium.

This is how I manged (unfortunately worked only with Chromium and not Firefox):  

sudo apt install -y xvfb
sudo apt -y install xorg xvfb gtk2-engines-pixbuf
sudo apt -y install dbus-x11 xfonts-base xfonts-100dpi xfonts-75dpi xfonts-cyrillic xfonts-scalable
sudo apt -y install imagemagick x11-apps
sudo apt install -y google-chrome

Xvfb -ac :99 -screen 0 1280x1024x16 &
export DISPLAY=:99

Remember to download the [chromedriver executable](chromedriver.chromium.org/) for your Chrome/Chromium version and configure its path in the settings.py file.