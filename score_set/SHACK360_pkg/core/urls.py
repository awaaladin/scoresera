"""
URL configuration for the Scoring System API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompetitionViewSet, JudgeViewSet, TeamViewSet, ScoreViewSet,
    leaderboard, dashboard_stats, analytics, settings_view,
    # Quiz System
    QuizMasterViewSet, QuestionViewSet, ContestantViewSet, QuizSessionViewSet,
    QuizAnswerViewSet, ProctorAlertViewSet, NetworkLogViewSet, quiz_dashboard_stats
)

router = DefaultRouter()
router.register(r'competitions', CompetitionViewSet)
router.register(r'judges', JudgeViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'scores', ScoreViewSet)

# Quiz System Routes
router.register(r'quiz/masters', QuizMasterViewSet)
router.register(r'quiz/questions', QuestionViewSet)
router.register(r'quiz/contestants', ContestantViewSet)
router.register(r'quiz/sessions', QuizSessionViewSet)
router.register(r'quiz/answers', QuizAnswerViewSet)
router.register(r'quiz/alerts', ProctorAlertViewSet)
router.register(r'quiz/network', NetworkLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('analytics/', analytics, name='analytics'),
    path('settings/', settings_view, name='settings'),
    # Quiz System
    path('quiz/dashboard/stats/', quiz_dashboard_stats, name='quiz-dashboard-stats'),
]
