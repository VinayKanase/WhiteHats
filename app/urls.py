from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('search/', views.search, name='search'),
    path('login/', views.login, name='login'),
    path('signUp/', views.signUp, name='signUp'),


    # Login Required
    path('new/', views.new, name='new'),

]
