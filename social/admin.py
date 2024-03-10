from django.contrib import admin
from .models import Profile, Post, Relationship, Address, Event

admin.site.register(Address)
admin.site.register(Profile)
admin.site.register(Event)
admin.site.register(Post)
admin.site.register(Relationship)
