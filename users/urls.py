from django.urls import path
from . import views
from .views import login_with_otp, verify_otp

urlpatterns = [
    path('signup/student/', views.student_signup, name='student_signup'),
    path('signup/teacher/', views.teacher_signup, name='teacher_signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', login_with_otp, name='login'), 
    path('verify-otp/', verify_otp, name='verify_otp'),
]


