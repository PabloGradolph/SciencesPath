from django.contrib import admin
from .models import Subject, Degree, University


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'year', 'credits')
    search_fields = ('name',)
    list_filter = ('university', 'year', 'credits')

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Degree)
admin.site.register(University)