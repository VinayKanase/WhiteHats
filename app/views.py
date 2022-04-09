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
    return HttpResponse("Search Page")


def new(request):
    """
        Controller to add new scholarships
        Authorized to logged in users only 
    """
    return HttpResponse("New")


def login(request):
    """
        Controller to login page
    """
    return HttpResponse("Login")


def signUp(request):
    """
        Controller to sign up new user
    """
    return HttpResponse("sign up")
