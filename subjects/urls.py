from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('detail/<int:subject_id>', views.detail, name='detail'),
    path('delete_review/<int:review_id>/<int:subject_id>', views.delete_review, name='delete_review'),
]