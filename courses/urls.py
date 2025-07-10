from django.urls import path
from . import views

urlpatterns = [
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/course/create/', views.create_course, name='create_course'),
    path('teacher/course/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('teacher/course/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('teacher/course/<int:course_id>/students/', views.view_enrollments, name='view_enrollments'),
    path('explore/', views.explore_courses, name='explore_courses'),
    path('subscribe/<int:course_id>/', views.subscribe_course, name='subscribe_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('pay/<int:course_id>/', views.create_payment, name='create_payment'),
    path('payment-success/<int:course_id>/', views.payment_success, name='payment_success'),

]
