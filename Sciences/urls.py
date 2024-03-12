from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('main', views.main, name='main'),
    path('signup/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('documents/', views.documents, name='documents'),
    path('remove-subject-from-schedule/<int:subject_id>/', views.delete_subject_from_schedule, name='remove-subject-from-schedule'),
    path('subjects/', include('subjects.urls')),
    path('community/', include('social.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
