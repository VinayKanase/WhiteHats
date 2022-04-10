from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('search/', views.search, name='search'),
    path('login/', views.login, name='login'),
    path('signUp/', views.signUp, name='signUp'),
    path('sholarship/', views.sholarship, name='sholarship'),


    # Login Required
    path('new/', views.new, name='new'),
    path('liked/', views.liked, name='liked'),
    path('profile/', views.liked, name='liked'),

    # Only admin
    path('admin/', views.admin, name='admin'),
    path('admin_verify/', views.admin_verify, name='admin_verify'),
    path('admin_users/', views.admin_users, name='admin_users'),
]
