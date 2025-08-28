from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from booking_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='booking_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='booking_app/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('travel/', views.travel_list, name='travel_list'),
    path('booking/<int:travel_id>/', views.booking_create, name='booking_create'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('ai-response/', views.ai_response, name='ai_response'),
]