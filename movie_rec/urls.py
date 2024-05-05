"""
URL configuration for movie_rec project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from movie_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome, ),
    path('login/', views.user_login),
    path('movies/', views.movie_list, name='movies'),
    path('register/', views.register),
    path('add_movie/', views.add_movie, name='add_movie'),
    path('category/<int:category_id>/', views.category_movies, name='category_movies'),
    path('add_comments/<int:movie_id>/', views.add_comments, name='add_comments'),
    path('edit_movie/<int:movie_id>/', views.edit_movie, name='edit_movie'),
    path('delete_movie/<int:movie_id>/', views.delete_movie, name='delete_movie'),
    path('movie_details/<int:movie_id>/', views.movie_detail, name='movie_details'),
    path('rate_movie/<int:movie_id>/', views.rate_movie, name='rate_movie'),
    path('search/', views.search_movies, name='search_movies'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('password_change/', views.password_change, name='password_change'),
    path('logout/', views.logout_view, name='logout')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)