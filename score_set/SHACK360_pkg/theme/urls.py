"""
URL configuration for the Scoring System frontend pages.
"""
from django.urls import path
from .views import (
    index, login_view, logout_view, signup_view,
    judge_login_view, judge_dashboard_view,
    results_view, admin_dashboard_view,
    # Quiz System
    quiz_master_login_view, quiz_master_dashboard_view,
    contestant_login_view, contestant_quiz_view,
    question_pool_view, quiz_results_view
)

urlpatterns = [
    # Public pages
    path('', index, name='index'),
    path('results/', results_view, name='results'),
    
    # Auth pages
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    
    # Judge pages
    path('judge/', judge_login_view, name='judge_login'),
    path('judge/dashboard/', judge_dashboard_view, name='judge_dashboard'),
    
    # Admin pages
    path('admin-panel/', admin_dashboard_view, name='admin_dashboard'),
    
    # Quiz System pages
    path('quiz/', quiz_master_login_view, name='quiz_master_login'),
    path('quiz/dashboard/', quiz_master_dashboard_view, name='quiz_master_dashboard'),
    path('quiz/contestant/', contestant_login_view, name='contestant_login'),
    path('quiz/play/', contestant_quiz_view, name='contestant_quiz'),
    path('quiz/questions/', question_pool_view, name='question_pool'),
    path('quiz/results/', quiz_results_view, name='quiz_results'),
]
