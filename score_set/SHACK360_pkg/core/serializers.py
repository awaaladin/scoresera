"""
Django REST Framework serializers for the Scoring System.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Competition, Judge, Team, Score, SiteSettings


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['id']


class CompetitionSerializer(serializers.ModelSerializer):
    """Serializer for Competition model."""
    teams_count = serializers.ReadOnlyField()
    judges_count = serializers.ReadOnlyField()
    scores_count = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Competition
        fields = [
            'id', 'name', 'description', 'date', 'location', 'status',
            'max_teams', 'created_by', 'created_by_name', 'teams_count',
            'judges_count', 'scores_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JudgeSerializer(serializers.ModelSerializer):
    """Serializer for Judge model."""
    scores_count = serializers.ReadOnlyField()
    competition_name = serializers.CharField(source='competition.name', read_only=True)
    
    class Meta:
        model = Judge
        fields = [
            'id', 'user', 'name', 'email', 'phone', 'pin', 'expertise',
            'competition', 'competition_name', 'is_active', 'scores_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'pin': {'required': False}  # Auto-generated if not provided
        }


class JudgeLoginSerializer(serializers.Serializer):
    """Serializer for judge login."""
    pin = serializers.CharField(max_length=10)


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model."""
    average_score = serializers.ReadOnlyField()
    scores_count = serializers.ReadOnlyField()
    competition_name = serializers.CharField(source='competition.name', read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'competition', 'competition_name', 'name', 'school_name',
            'company_name', 'category', 'contact_name', 'contact_email',
            'contact_phone', 'logo', 'description', 'average_score',
            'scores_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScoreSerializer(serializers.ModelSerializer):
    """Serializer for Score model."""
    team_name = serializers.CharField(source='team.name', read_only=True)
    judge_name = serializers.CharField(source='judge.name', read_only=True)
    competition_id = serializers.IntegerField(source='team.competition.id', read_only=True)
    
    class Meta:
        model = Score
        fields = [
            'id', 'team', 'team_name', 'judge', 'judge_name', 'competition_id',
            'innovation_score', 'impact_score', 'presentation_score',
            'total_score', 'comments', 'submitted_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_score', 'submitted_at', 'updated_at']


class ScoreSubmitSerializer(serializers.Serializer):
    """Serializer for submitting a score."""
    competition_id = serializers.IntegerField()
    judge_id = serializers.IntegerField()
    team_name = serializers.CharField(max_length=255)
    innovation = serializers.DecimalField(max_digits=4, decimal_places=2)
    impact = serializers.DecimalField(max_digits=4, decimal_places=2)
    presentation = serializers.DecimalField(max_digits=4, decimal_places=2)
    comments = serializers.CharField(required=False, allow_blank=True)


class LeaderboardSerializer(serializers.Serializer):
    """Serializer for leaderboard entries."""
    team_name = serializers.CharField()
    avg_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    votes = serializers.IntegerField()


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    competitions_count = serializers.IntegerField()
    judges_count = serializers.IntegerField()
    teams_scored_count = serializers.IntegerField()


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SiteSettings model."""
    class Meta:
        model = SiteSettings
        fields = '__all__'
        read_only_fields = ['id']


class AnalyticsSerializer(serializers.Serializer):
    """Serializer for analytics data."""
    total_competitions = serializers.IntegerField()
    active_judges = serializers.IntegerField()
    total_teams = serializers.IntegerField()
    total_scores = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    past_competitions = CompetitionSerializer(many=True)
    current_competitions = CompetitionSerializer(many=True)
    future_competitions = CompetitionSerializer(many=True)
    top_teams = serializers.ListField()


# ============================================================================
# SMART AI LIVE QUIZ & PROCTORING SYSTEM SERIALIZERS
# ============================================================================

from .models import (
    QuizMaster, Question, Contestant, QuizSession, 
    QuizAnswer, QuizScore, ProctorAlert, NetworkLog
)


class QuizMasterSerializer(serializers.ModelSerializer):
    """Serializer for QuizMaster model."""
    sessions_count = serializers.ReadOnlyField()
    
    class Meta:
        model = QuizMaster
        fields = [
            'id', 'user', 'name', 'email', 'phone', 'pin', 'expertise',
            'is_active', 'sessions_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'pin': {'required': False}
        }


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""
    success_rate = serializers.ReadOnlyField()
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    type_display = serializers.CharField(source='get_question_type_display', read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_number', 'question_text', 'question_type', 'type_display',
            'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer',
            'category', 'difficulty', 'difficulty_display', 'points', 'time_limit',
            'times_asked', 'times_correct', 'success_rate', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'times_asked', 'times_correct', 'created_at', 'updated_at']


class ContestantSerializer(serializers.ModelSerializer):
    """Serializer for Contestant model."""
    accuracy_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Contestant
        fields = [
            'id', 'name', 'email', 'phone', 'school_name', 'access_code',
            'photo_url', 'total_quizzes', 'total_correct', 'total_wrong',
            'total_points', 'accuracy_rate', 'is_active', 'is_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'access_code', 'created_at', 'updated_at']


class QuizSessionSerializer(serializers.ModelSerializer):
    """Serializer for QuizSession model."""
    quiz_master_name = serializers.CharField(source='quiz_master.name', read_only=True)
    contestants_list = ContestantSerializer(source='contestants', many=True, read_only=True)
    current_question_number = serializers.ReadOnlyField()
    duration_seconds = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    mode_display = serializers.CharField(source='get_mode_display', read_only=True)
    
    class Meta:
        model = QuizSession
        fields = [
            'id', 'title', 'quiz_master', 'quiz_master_name', 'contestants',
            'contestants_list', 'mode', 'mode_display', 'status', 'status_display',
            'total_questions', 'default_time_per_question', 'category_filter',
            'difficulty_filter', 'correct_points', 'speed_bonus_enabled',
            'negative_marking', 'wrong_answer_penalty', 'proctoring_enabled',
            'movement_detection', 'voice_detection', 'fullscreen_required',
            'tab_switch_detection', 'max_warnings', 'room_id', 'recording_enabled',
            'recording_url', 'scheduled_time', 'started_at', 'ended_at',
            'current_question_number', 'duration_seconds', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'room_id', 'created_at', 'updated_at']


class QuizAnswerSerializer(serializers.ModelSerializer):
    """Serializer for QuizAnswer model."""
    contestant_name = serializers.CharField(source='contestant.name', read_only=True)
    question_number = serializers.IntegerField(source='question.question_number', read_only=True)
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = QuizAnswer
        fields = [
            'id', 'session', 'contestant', 'contestant_name', 'question',
            'question_number', 'question_text', 'answer_given', 'is_correct',
            'time_taken', 'base_points', 'speed_bonus', 'penalty_points',
            'total_points', 'is_timed_out', 'submitted_at'
        ]
        read_only_fields = ['id', 'is_correct', 'base_points', 'speed_bonus', 
                          'penalty_points', 'total_points', 'submitted_at']


class QuizScoreSerializer(serializers.ModelSerializer):
    """Serializer for QuizScore model."""
    contestant_name = serializers.CharField(source='contestant.name', read_only=True)
    session_title = serializers.CharField(source='session.title', read_only=True)
    
    class Meta:
        model = QuizScore
        fields = [
            'id', 'session', 'session_title', 'contestant', 'contestant_name',
            'total_questions', 'correct_answers', 'wrong_answers', 'timed_out',
            'total_base_points', 'total_speed_bonus', 'total_penalty',
            'final_score', 'average_time', 'accuracy_percentage', 'rank',
            'warnings_count', 'is_disqualified', 'disqualification_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProctorAlertSerializer(serializers.ModelSerializer):
    """Serializer for ProctorAlert model."""
    contestant_name = serializers.CharField(source='contestant.name', read_only=True)
    session_title = serializers.CharField(source='session.title', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = ProctorAlert
        fields = [
            'id', 'session', 'session_title', 'contestant', 'contestant_name',
            'alert_type', 'alert_type_display', 'severity', 'severity_display',
            'description', 'screenshot_url', 'audio_clip_url', 'is_reviewed',
            'reviewed_by', 'reviewed_by_name', 'review_notes', 'is_false_positive',
            'ping_ms', 'packet_loss', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NetworkLogSerializer(serializers.ModelSerializer):
    """Serializer for NetworkLog model."""
    contestant_name = serializers.CharField(source='contestant.name', read_only=True)
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = NetworkLog
        fields = [
            'id', 'session', 'contestant', 'contestant_name', 'ping_ms',
            'packet_loss', 'jitter_ms', 'connection_type', 'status', 'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_at']
