from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
    """
        Controller for index or home page
    """
    return render(request, 'index.html')


def search(request):
    """
        Controller for search scholarships page
    """
    return render(request, 'search.html')


def new(request):
    """
        Controller to add new scholarships
        Authorized to logged in users only 
    """
    return render(request, 'new.html')


def login(request):
    """
        Controller to login page
    """
    return render(request, 'login.html')


def signUp(request):
    """
        Controller to sign up new user
    """
    return render(request, 'signUp.html')
