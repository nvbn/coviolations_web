from django.contrib.sites.models import Site
import requests
import json


def make_https(url):
    """Return https version for url"""
    current_full = 'http://{}{}'.format(
        Site.objects.get_current().domain, url,
    )
    response = requests.post(
        'https://www.googleapis.com/urlshortener/v1/url',
        data=json.dumps({'longUrl': current_full}),
        headers={
            'Content-type': 'application/json',
            'Accept': 'text/plain',
        },
    )
    return response.json()['id'].replace('http://', 'https://')
