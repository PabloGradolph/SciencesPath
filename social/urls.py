from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='community_home'),
    path('delete/<int:post_id>', views.delete, name='delete'),
    path('edit/', views.edit, name='edit'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
]