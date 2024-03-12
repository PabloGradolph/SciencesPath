from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('detail/<int:subject_id>', views.detail, name='detail'),
    path('delete_review/<int:review_id>/<int:subject_id>', views.delete_review, name='delete_review'),
    path('upload_material/<int:subject_id>/', views.upload_material, name='upload_material'),
    path('horario/<int:subject_id>/', views.horario, name='horario'),
    path('search/', views.search_subjects, name='search_subjects'),
    path('parse-ics/<int:subject_id>/', views.parse_ics_to_json, name='parse-ics-to-json'),
    path('event/add/', views.add_event, name='add-event'),
    path('event/update/', views.update_event, name='update-event'),
    path('event/delete/<int:event_id>/', views.delete_event, name='delete-event'),
]