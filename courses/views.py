from django.shortcuts import render, redirect, get_object_or_404
from .models import Course
from .forms import CourseForm
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from .models import Course, Enrollment
from django.core.mail import send_mail


import paypalrestsdk
from django.conf import settings

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})



# Decorator to check teacher
def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_teacher:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@teacher_required
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'courses/teacher_dashboard.html', {'courses': courses})

@login_required
@teacher_required
def create_course(request):
    form = CourseForm()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()

            # ✅ Email previous students
            students = Enrollment.objects.filter(course__teacher=request.user).select_related('student')
            notified = set()

            for enrollment in students:
                student = enrollment.student
                if student.email not in notified:
                    send_mail(
                        subject=f"🎓 New Course by {request.user.username}",
                        message=f"Hi {student.username},\n\n{request.user.username} just launched a new course: '{course.title}' on LearnHub!\n\nGo check it out!",
                        from_email='noreply@learnhub.com',
                        recipient_list=[student.email],
                        fail_silently=True
                    )
                    notified.add(student.email)

            return redirect('teacher_dashboard')
    return render(request, 'courses/course_form.html', {'form': form})

@login_required
@teacher_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    form = CourseForm(instance=course)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('teacher_dashboard')
    return render(request, 'courses/course_form.html', {'form': form})

@login_required
@teacher_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    course.delete()
    return redirect('teacher_dashboard')

@login_required
@teacher_required
def view_enrollments(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = Enrollment.objects.filter(course=course)
    return render(request, 'courses/enrollments.html', {
        'course': course,
        'enrollments': enrollments
    })
from django.db.models import Q

@login_required
def explore_courses(request):
    query = request.GET.get('q')
    if query:
        courses = Course.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    else:
        courses = Course.objects.all()
    return render(request, 'courses/explore.html', {'courses': courses})

@login_required
def subscribe_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.is_teacher:
        return redirect('explore_courses')

    already_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not already_enrolled:
        Enrollment.objects.create(student=request.user, course=course)

    return redirect('my_courses')

@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'courses/my_courses.html', {'enrollments': enrollments})

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from .models import Course, Enrollment

@login_required
def create_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.is_teacher:
        return redirect('explore_courses')

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('payment_success', args=[course.id])),
            "cancel_url": request.build_absolute_uri(reverse('explore_courses')),
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": course.title,
                    "sku": f"course_{course.id}",
                    "price": str(course.price),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(course.price),
                "currency": "USD"
            },
            "description": f"Purchase of course: {course.title}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    else:
        return JsonResponse({'error': 'Payment creation failed'}, status=500)

@login_required
def payment_success(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    messages.success(request, f"You’re now subscribed to '{course.title}'!")
    return redirect('my_courses')
