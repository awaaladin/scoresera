"""
Django models for the Junior Achievement Nigeria Scoring System.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import random
import string


class Competition(models.Model):
    """Competition event model."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    max_teams = models.PositiveIntegerField(default=50)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_competitions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.date})"
    
    @property
    def teams_count(self):
        return self.teams.count()
    
    @property
    def judges_count(self):
        return self.judges.count()
    
    @property
    def scores_count(self):
        return Score.objects.filter(team__competition=self).count()


class Judge(models.Model):
    """Judge model - can be linked to a User or standalone."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='judge_profile')
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    pin = models.CharField(max_length=10, unique=True)
    expertise = models.CharField(max_length=255, blank=True)
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True, related_name='judges')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.pin:
            self.pin = self.generate_pin()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_pin():
        """Generate a random 6-digit PIN."""
        return ''.join(random.choices(string.digits, k=6))
    
    @property
    def scores_count(self):
        return self.scores.count()


class Team(models.Model):
    """Team participating in a competition."""
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=255)
    school_name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    logo = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = [['competition', 'name']]
    
    def __str__(self):
        return f"{self.name} - {self.competition.name}"
    
    @property
    def average_score(self):
        scores = self.scores.all()
        if not scores:
            return 0
        return sum(s.total_score for s in scores) / len(scores)
    
    @property
    def scores_count(self):
        return self.scores.count()


class Score(models.Model):
    """Score entry from a judge for a team."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='scores')
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE, related_name='scores')
    
    # Scoring criteria (each out of 10)
    innovation_score = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    impact_score = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    presentation_score = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    
    # Weighted total (calculated)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = [['team', 'judge']]  # One score per judge per team
    
    def __str__(self):
        return f"{self.team.name} by {self.judge.name}: {self.total_score}"
    
    def save(self, *args, **kwargs):
        # Calculate weighted total score
        # Innovation: 30%, Impact: 40%, Presentation: 30%
        self.total_score = (
            float(self.innovation_score) * 0.30 +
            float(self.impact_score) * 0.40 +
            float(self.presentation_score) * 0.30
        ) * 10  # Scale to 100
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    """Global site settings (singleton model)."""
    organization_name = models.CharField(max_length=255, default="Junior Achievement Nigeria")
    organization_email = models.EmailField(default="admin@janigeria.org")
    organization_phone = models.CharField(max_length=20, default="+234 800 000 0000")
    organization_address = models.TextField(default="Lagos, Nigeria")
    
    # Scoring settings
    default_max_score = models.PositiveIntegerField(default=10)
    innovation_weight = models.PositiveIntegerField(default=30)
    impact_weight = models.PositiveIntegerField(default=40)
    presentation_weight = models.PositiveIntegerField(default=30)
    
    # Feature flags
    allow_offline_scoring = models.BooleanField(default=True)
    auto_calculate_results = models.BooleanField(default=True)
    require_judge_email = models.BooleanField(default=False)
    
    # System settings
    theme = models.CharField(max_length=20, default='light')
    timezone = models.CharField(max_length=50, default='UTC+1')
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


# ============================================================================
# SMART AI LIVE QUIZ & PROCTORING SYSTEM MODELS
# ============================================================================

class QuizMaster(models.Model):
    """Quiz Master / Moderator - oversees live quiz sessions."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='quizmaster_profile')
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    pin = models.CharField(max_length=10, unique=True)
    expertise = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Quiz Master"
        verbose_name_plural = "Quiz Masters"
    
    def __str__(self):
        return f"QM: {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.pin:
            self.pin = ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)
    
    @property
    def sessions_count(self):
        return self.quiz_sessions.count()


class Question(models.Model):
    """Question pool for quiz sessions."""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    ]
    
    question_number = models.PositiveIntegerField(unique=True, validators=[MinValueValidator(1), MaxValueValidator(1000)])
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='mcq')
    
    # For MCQ questions
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_answer = models.CharField(max_length=500)
    
    # Question metadata
    category = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    points = models.PositiveIntegerField(default=10)
    time_limit = models.PositiveIntegerField(default=30, help_text="Time in seconds")
    
    # Tracking
    times_asked = models.PositiveIntegerField(default=0)
    times_correct = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['question_number']
    
    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}..."
    
    @property
    def success_rate(self):
        if self.times_asked == 0:
            return 0
        return round((self.times_correct / self.times_asked) * 100, 1)


class Contestant(models.Model):
    """Contestant participating in quiz sessions."""
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    school_name = models.CharField(max_length=255, blank=True)
    access_code = models.CharField(max_length=10, unique=True)
    photo_url = models.URLField(blank=True)
    
    # Biometric data (for face verification)
    face_encoding = models.TextField(blank=True, help_text="Stored face encoding for verification")
    
    # Stats
    total_quizzes = models.PositiveIntegerField(default=0)
    total_correct = models.PositiveIntegerField(default=0)
    total_wrong = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)
    
    @property
    def accuracy_rate(self):
        total = self.total_correct + self.total_wrong
        if total == 0:
            return 0
        return round((self.total_correct / total) * 100, 1)


class QuizSession(models.Model):
    """Live quiz session between quiz master and contestant(s)."""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('waiting', 'Waiting for Contestant'),
        ('live', 'Live'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    MODE_CHOICES = [
        ('single', 'Single Contestant'),
        ('multi', 'Multiple Contestants'),
        ('tournament', 'Tournament Mode'),
    ]
    
    title = models.CharField(max_length=255)
    quiz_master = models.ForeignKey(QuizMaster, on_delete=models.CASCADE, related_name='quiz_sessions')
    contestants = models.ManyToManyField(Contestant, related_name='quiz_sessions', blank=True)
    
    # Session settings
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='single')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    total_questions = models.PositiveIntegerField(default=10)
    default_time_per_question = models.PositiveIntegerField(default=30)
    
    # Question selection
    category_filter = models.CharField(max_length=100, blank=True)
    difficulty_filter = models.CharField(max_length=20, blank=True)
    questions_used = models.ManyToManyField(Question, related_name='sessions_used', blank=True)
    
    # Scoring settings
    correct_points = models.PositiveIntegerField(default=10)
    speed_bonus_enabled = models.BooleanField(default=True)
    negative_marking = models.BooleanField(default=False)
    wrong_answer_penalty = models.PositiveIntegerField(default=2)
    
    # Proctoring settings
    proctoring_enabled = models.BooleanField(default=True)
    movement_detection = models.BooleanField(default=True)
    voice_detection = models.BooleanField(default=True)
    fullscreen_required = models.BooleanField(default=True)
    tab_switch_detection = models.BooleanField(default=True)
    max_warnings = models.PositiveIntegerField(default=3)
    
    # WebRTC session
    room_id = models.CharField(max_length=50, unique=True, blank=True)
    recording_enabled = models.BooleanField(default=True)
    recording_url = models.URLField(blank=True)
    
    # Timing
    scheduled_time = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Quiz Session"
        verbose_name_plural = "Quiz Sessions"
    
    def __str__(self):
        return f"{self.title} - {self.quiz_master.name}"
    
    def save(self, *args, **kwargs):
        if not self.room_id:
            self.room_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        super().save(*args, **kwargs)
    
    @property
    def current_question_number(self):
        return self.questions_used.count()
    
    @property
    def duration_seconds(self):
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return 0


class QuizAnswer(models.Model):
    """Individual answer submitted by contestant during a quiz session."""
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='answers')
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='quiz_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='quiz_answers')
    
    # Answer data
    answer_given = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    time_taken = models.FloatField(default=0, help_text="Seconds taken to answer")
    
    # Scoring
    base_points = models.PositiveIntegerField(default=0)
    speed_bonus = models.PositiveIntegerField(default=0)
    penalty_points = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    
    # Status
    is_timed_out = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['submitted_at']
        unique_together = [['session', 'contestant', 'question']]
    
    def __str__(self):
        return f"{self.contestant.name} - Q{self.question.question_number}: {'✓' if self.is_correct else '✗'}"
    
    def save(self, *args, **kwargs):
        # Calculate points
        if self.is_correct:
            self.base_points = self.question.points
            # Speed bonus: faster answer = more bonus (max 50% of base points)
            if self.time_taken > 0 and self.time_taken < self.question.time_limit:
                remaining_time_ratio = 1 - (self.time_taken / self.question.time_limit)
                self.speed_bonus = int(self.base_points * 0.5 * remaining_time_ratio)
        else:
            self.base_points = 0
            self.speed_bonus = 0
            if self.session.negative_marking:
                self.penalty_points = self.session.wrong_answer_penalty
        
        self.total_points = self.base_points + self.speed_bonus - self.penalty_points
        super().save(*args, **kwargs)
        
        # Update question stats
        self.question.times_asked += 1
        if self.is_correct:
            self.question.times_correct += 1
        self.question.save()


class QuizScore(models.Model):
    """Overall score for a contestant in a quiz session."""
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='scores')
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='quiz_scores')
    
    # Scores
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    timed_out = models.PositiveIntegerField(default=0)
    
    # Points
    total_base_points = models.PositiveIntegerField(default=0)
    total_speed_bonus = models.PositiveIntegerField(default=0)
    total_penalty = models.PositiveIntegerField(default=0)
    final_score = models.IntegerField(default=0)
    
    # Performance metrics
    average_time = models.FloatField(default=0)
    accuracy_percentage = models.FloatField(default=0)
    
    # Ranking
    rank = models.PositiveIntegerField(null=True, blank=True)
    
    # Proctoring alerts
    warnings_count = models.PositiveIntegerField(default=0)
    is_disqualified = models.BooleanField(default=False)
    disqualification_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-final_score']
        unique_together = [['session', 'contestant']]
    
    def __str__(self):
        return f"{self.contestant.name} - {self.final_score} pts"
    
    def calculate_from_answers(self):
        """Recalculate score from all answers."""
        answers = QuizAnswer.objects.filter(session=self.session, contestant=self.contestant)
        
        self.total_questions = answers.count()
        self.correct_answers = answers.filter(is_correct=True).count()
        self.wrong_answers = answers.filter(is_correct=False, is_timed_out=False).count()
        self.timed_out = answers.filter(is_timed_out=True).count()
        
        self.total_base_points = sum(a.base_points for a in answers)
        self.total_speed_bonus = sum(a.speed_bonus for a in answers)
        self.total_penalty = sum(a.penalty_points for a in answers)
        self.final_score = self.total_base_points + self.total_speed_bonus - self.total_penalty
        
        if self.total_questions > 0:
            self.average_time = sum(a.time_taken for a in answers) / self.total_questions
            self.accuracy_percentage = (self.correct_answers / self.total_questions) * 100
        
        self.save()


class ProctorAlert(models.Model):
    """AI proctoring alerts for suspicious behavior."""
    ALERT_TYPE_CHOICES = [
        ('movement', 'Suspicious Movement'),
        ('look_away', 'Looking Away'),
        ('multiple_faces', 'Multiple Faces Detected'),
        ('no_face', 'No Face Detected'),
        ('voice', 'Voice Detected'),
        ('side_talk', 'Side Talk'),
        ('tab_switch', 'Tab Switch'),
        ('fullscreen_exit', 'Exited Fullscreen'),
        ('network', 'Network Issue'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='proctor_alerts')
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='proctor_alerts')
    
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    description = models.TextField()
    
    # Evidence
    screenshot_url = models.URLField(blank=True)
    audio_clip_url = models.URLField(blank=True)
    
    # Status
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    review_notes = models.TextField(blank=True)
    is_false_positive = models.BooleanField(default=False)
    
    # Network data (for network alerts)
    ping_ms = models.PositiveIntegerField(null=True, blank=True)
    packet_loss = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Proctor Alert"
        verbose_name_plural = "Proctor Alerts"
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.get_alert_type_display()} - {self.contestant.name}"


class NetworkLog(models.Model):
    """Network quality log for contestants during quiz."""
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='network_logs')
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='network_logs')
    
    ping_ms = models.PositiveIntegerField()
    packet_loss = models.FloatField(default=0)
    jitter_ms = models.PositiveIntegerField(default=0)
    connection_type = models.CharField(max_length=50, blank=True)  # wifi, 4g, etc.
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.contestant.name}: {self.ping_ms}ms"
    
    @property
    def status(self):
        if self.ping_ms <= 50:
            return 'good'
        elif self.ping_ms <= 120:
            return 'fair'
        else:
            return 'poor'

