"""
Django views for the Scoring System frontend pages.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods


def index(request):
    """Landing page - public access."""
    return render(request, 'index.html')


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def login_view(request):
    """Admin login page."""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def signup_view(request):
    """Admin signup page."""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'signup.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'signup.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'signup.html')
    
    return render(request, 'signup.html')


def logout_view(request):
    """Logout user."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')


@ensure_csrf_cookie
def judge_login_view(request):
    """Judge PIN login page."""
    return render(request, 'judge_login.html')


@ensure_csrf_cookie
def judge_dashboard_view(request):
    """Judge scoring dashboard."""
    return render(request, 'judge_dashboard.html')


def results_view(request):
    """Public live results page."""
    return render(request, 'results.html')


@login_required(login_url='login')
def admin_dashboard_view(request):
    """Admin dashboard - requires authentication."""
    return render(request, 'admin_dashboard.html')


# ============================================================================
# SMART AI LIVE QUIZ & PROCTORING SYSTEM VIEWS
# ============================================================================

@ensure_csrf_cookie
def quiz_master_login_view(request):
    """Quiz Master PIN login page."""
    return render(request, 'quiz_master_login.html')


@ensure_csrf_cookie
def quiz_master_dashboard_view(request):
    """Quiz Master control dashboard."""
    return render(request, 'quiz_master_dashboard.html')


@ensure_csrf_cookie
def contestant_login_view(request):
    """Contestant access code login page."""
    return render(request, 'contestant_login.html')


@ensure_csrf_cookie
def contestant_quiz_view(request):
    """Contestant quiz interface."""
    return render(request, 'contestant_quiz.html')


@login_required(login_url='login')
def question_pool_view(request):
    """Admin question pool management."""
    return render(request, 'question_pool.html')


def quiz_results_view(request):
    """Public quiz results/leaderboard page."""
    return render(request, 'quiz_results.html')
