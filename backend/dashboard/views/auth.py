# dashboard/views/auth.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import RegistrationForm, CustomLoginForm

def redirect_role_based_dashboard(user):
    if user.role == 'student':
        return redirect('student_dashboard')
    elif user.role == 'teacher':
        return redirect('teacher_dashboard')
    return redirect('admin_dashboard')
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to SmartResa")
            return redirect_role_based_dashboard(user)
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect_role_based_dashboard(user)
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'title': 'Register Account'
    })

def custom_login(request):
    if request.user.is_authenticated:
        return redirect_role_based_dashboard(request.user)
        
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            try:
                user = form.get_user()
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect_role_based_dashboard(user)
            except Exception as e:
                messages.error(request, f'Login failed: {str(e)}')
        else:
            messages.error(request, 'Invalid email or password')
    else:
        form = CustomLoginForm()
    
    return render(request, 'registration/login.html', {
        'form': form,
        'title': 'Login to SmartResa'
    })

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('login')