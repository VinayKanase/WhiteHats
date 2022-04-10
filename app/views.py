from django.http import HttpResponse
from django.shortcuts import render
from decouple import config
import pyrebase

# FIREBASE CONIFGURATION
firebaseConfig = {
    'apiKey': config('FIREBASE_APIKEY'),
    'authDomain': config('FIREBASE_AUTHDOMAIN'),
    'projectId': config('FIREBASE_PROJECTID'),
    'storageBucket': config('FIREBASE_STORAGEBUCKET'),
    'messagingSenderId': config('FIREBASE_MESSAGINGSENDERID'),
    'appId': config('FIREBASE_APPID'),
    'measurementId': config('FIREBASE_MEASUREMENTID'),
    'databaseURL': config('FIREBASE_DATABASEURL')
}

app = pyrebase.initialize_app(firebaseConfig)
auth = app.auth()
database = app.database()
storage = app.storage()

print(database.child('users').get().val())


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


def scholarship(request):
    """
        Controller to see information of each scholarship
    """
    return render(request, 'scholarship.html')


def liked(request):
    """
        Controller to see total liked scholarships by you
        Authorized to logged in users only 
    """
    return render(request, 'liked.html')


def profile(request):
    """
        Controller to profile 
        Authorized to logged in users only 
    """
    return render(request, 'profile.html')


def admin(request):
    """
        Controller to admin page
        Only admin can be allowed
    """
    return render(request, 'admin.html')


def admin_verify(request):
    """
        Controller to admin verify/unverify scholarships page
        Only admin can be allowed
    """
    return render(request, 'admin_verify.html')


def admin_users(request):
    """
        Controller to admin to veiw users page
        Only admin can be allowed
    """
    return render(request, 'admin_users.html')
