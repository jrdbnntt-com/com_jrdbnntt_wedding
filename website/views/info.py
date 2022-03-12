from django.http.request import HttpRequest
from django.shortcuts import render

from website.core.auth.user import groups


def venue(request: HttpRequest):
    return render(request, "info/venue/index.html", {
        'page_title': 'Venue',
    })


def photos(request: HttpRequest):
    return render(request, "info/photos/index.html", {
        'page_title': 'Photos'
    })


def story(request: HttpRequest):
    return render(request, "info/story/index.html", {
        'page_title': 'Our Story'
    })


def travel_and_stay(request: HttpRequest):
    return render(request, "info/travel_and_stay/index.html", {
        'page_title': 'Travel'
    })


def wedding_party(request: HttpRequest):
    return render(request, "info/wedding_party/index.html", {
        'page_title': 'Wedding Party'
    })
