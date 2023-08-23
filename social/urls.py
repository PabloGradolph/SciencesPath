from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='community_home'),
    path('delete/<int:post_id>', views.delete, name='delete'),
]