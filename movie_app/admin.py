from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, Movie, Comment, Rating, User

admin.site.register(Category)
admin.site.register(Movie)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(User, UserAdmin)