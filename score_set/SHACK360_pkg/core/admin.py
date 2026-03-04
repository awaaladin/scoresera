"""
Django admin configuration for the Scoring System.
"""
from django.contrib import admin
from .models import (
    Competition, Judge, Team, Score, SiteSettings,
    QuizMaster, Question, Contestant, QuizSession, 
    QuizAnswer, QuizScore, ProctorAlert, NetworkLog
)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'status', 'teams_count', 'judges_count', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['name', 'description', 'location']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Judge)
class JudgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'pin', 'competition', 'is_active', 'scores_count']
    list_filter = ['is_active', 'competition']
    search_fields = ['name', 'email', 'phone', 'expertise']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'competition', 'school_name', 'average_score', 'scores_count']
    list_filter = ['competition', 'category']
    search_fields = ['name', 'school_name', 'company_name', 'contact_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['team', 'judge', 'innovation_score', 'impact_score', 'presentation_score', 'total_score', 'submitted_at']
    list_filter = ['team__competition', 'judge', 'submitted_at']
    search_fields = ['team__name', 'judge__name', 'comments']
    readonly_fields = ['total_score', 'submitted_at', 'updated_at']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'organization_email']
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================================
# SMART AI LIVE QUIZ & PROCTORING SYSTEM ADMIN
# ============================================================================

@admin.register(QuizMaster)
class QuizMasterAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'pin', 'is_active', 'sessions_count', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'phone', 'expertise']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_number', 'question_text_short', 'question_type', 'difficulty', 'points', 'time_limit', 'success_rate', 'is_active']
    list_filter = ['question_type', 'difficulty', 'category', 'is_active']
    search_fields = ['question_text', 'correct_answer', 'category']
    ordering = ['question_number']
    readonly_fields = ['times_asked', 'times_correct', 'created_at', 'updated_at']
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(Contestant)
class ContestantAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'school_name', 'access_code', 'total_quizzes', 'accuracy_rate', 'is_active', 'is_verified']
    list_filter = ['is_active', 'is_verified', 'school_name']
    search_fields = ['name', 'email', 'phone', 'school_name']
    readonly_fields = ['access_code', 'total_quizzes', 'total_correct', 'total_wrong', 'total_points', 'created_at', 'updated_at']


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'quiz_master', 'status', 'mode', 'total_questions', 'proctoring_enabled', 'started_at', 'ended_at']
    list_filter = ['status', 'mode', 'proctoring_enabled']
    search_fields = ['title', 'quiz_master__name']
    filter_horizontal = ['contestants', 'questions_used']
    readonly_fields = ['room_id', 'created_at', 'updated_at']


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'contestant', 'question', 'answer_given', 'is_correct', 'time_taken', 'total_points', 'submitted_at']
    list_filter = ['is_correct', 'is_timed_out', 'session']
    search_fields = ['contestant__name', 'answer_given']
    readonly_fields = ['base_points', 'speed_bonus', 'penalty_points', 'total_points', 'submitted_at']


@admin.register(QuizScore)
class QuizScoreAdmin(admin.ModelAdmin):
    list_display = ['session', 'contestant', 'correct_answers', 'wrong_answers', 'final_score', 'accuracy_percentage', 'rank', 'warnings_count', 'is_disqualified']
    list_filter = ['is_disqualified', 'session']
    search_fields = ['contestant__name', 'session__title']
    readonly_fields = ['total_questions', 'correct_answers', 'wrong_answers', 'timed_out', 
                      'total_base_points', 'total_speed_bonus', 'total_penalty', 'final_score',
                      'average_time', 'accuracy_percentage', 'created_at', 'updated_at']


@admin.register(ProctorAlert)
class ProctorAlertAdmin(admin.ModelAdmin):
    list_display = ['session', 'contestant', 'alert_type', 'severity', 'is_reviewed', 'is_false_positive', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_reviewed', 'is_false_positive']
    search_fields = ['contestant__name', 'description']
    readonly_fields = ['created_at']


@admin.register(NetworkLog)
class NetworkLogAdmin(admin.ModelAdmin):
    list_display = ['session', 'contestant', 'ping_ms', 'packet_loss', 'jitter_ms', 'status', 'recorded_at']
    list_filter = ['session', 'connection_type']
    search_fields = ['contestant__name']
    readonly_fields = ['recorded_at']
