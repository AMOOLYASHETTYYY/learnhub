from django.shortcuts import render, redirect
from .forms import StudentSignUpForm, TeacherSignUpForm
from django.contrib import messages
from .models import CustomUser


def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student account created successfully!')
            return redirect('login')  # We’ll create this login URL soon
    else:
        form = StudentSignUpForm()
    return render(request, 'users/signup.html', {'form': form, 'user_type': 'Student'})

def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher account created successfully!')
            return redirect('login')
    else:
        form = TeacherSignUpForm()
    return render(request, 'users/signup.html', {'form': form, 'user_type': 'Teacher'})

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from .models import OTP
from .forms import OTPForm
from django.contrib import messages

def login_with_otp(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            
            otp_obj, created = OTP.objects.get_or_create(user=user)
            otp_obj.generate_code()

           
            send_mail(
                subject='Your OTP for LearnHub Login',
                message=f'Your OTP is: {otp_obj.code}',
                from_email='noreply@learnhub.com',
                recipient_list=[user.email],
            )

            
            request.session['otp_user_id'] = user.id
            return redirect('verify_otp')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'users/login_otp.html')






def verify_otp(request):
    if request.method == 'POST':
        user_id = request.session.get('otp_user_id')

        # If session expired or missing, redirect to login
        if not user_id:
            messages.error(request, "Session expired. Please log in again.")
            return redirect('login')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')

        otp_input = request.POST.get('otp')

        # Check if OTP is valid for this user
        if OTP.objects.filter(user=user, code=otp_input).exists():
            login(request, user)
            request.session.pop('otp_user_id', None)  # ✅ safe delete
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'users/verify_otp.html')
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
