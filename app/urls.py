from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('scholarship/<str:id>/', views.scholarship, name='scholarship'),

    path('login/', views.login, name='login'),
    path('signUp/', views.signUp, name='signUp'),

    # Auth required Pages
    path('liked/', views.liked, name='liked'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('new/', views.new, name='new'),
    # post operations
    path('post_like/<str:id>', views.post_like, name='post_like'),
    path('post_report/<str:id>', views.post_report, name='post_report'),
    path('post_comment/', views.post_comment, name='post_comment'),
    path('post_delete/', views.post_delete, name='post_delete'),
    # Only Admin authorized
    path('admin/', views.admin, name='admin'),
    path('admin/verify/', views.admin_verify, name='admin_verify'),
    path('admin/users/', views.admin_users, name='admin_users'),
]
