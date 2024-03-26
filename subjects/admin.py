from django.contrib import admin
from .models import Subject, Degree, University, SubjectRating, TimeTable, SubjectMaterial, SubjectSchedule, ExtraCurricularCredits, Dossier, SubjectInDossier


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'year', 'credits')
    search_fields = ('name',)
    list_filter = ('university', 'year', 'credits')

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Degree)
admin.site.register(University)
admin.site.register(SubjectRating)
admin.site.register(TimeTable)
admin.site.register(SubjectMaterial)
admin.site.register(SubjectSchedule)
admin.site.register(Dossier)
admin.site.register(SubjectInDossier)
admin.site.register(ExtraCurricularCredits)
