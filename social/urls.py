from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='community_home'),
    path('delete/<int:post_id>', views.delete, name='delete'),
    path('edit/', views.edit, name='edit'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('like/', views.post_like, name='post_like'),
    path('add_comment/<int:post_id>/', views.add_comment_to_post, name='add_comment_to_post'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]