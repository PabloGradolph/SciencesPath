from django.contrib import admin
from .models import Profile, Post, Relationship, Address

admin.site.register(Address)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Relationship)
