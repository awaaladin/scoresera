"""
Django REST Framework views for the Scoring System API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import datetime

from .models import Competition, Judge, Team, Score, SiteSettings
from .serializers import (
    CompetitionSerializer, JudgeSerializer, JudgeLoginSerializer,
    TeamSerializer, ScoreSerializer, ScoreSubmitSerializer,
    LeaderboardSerializer, DashboardStatsSerializer, SiteSettingsSerializer,
    AnalyticsSerializer, UserSerializer
)


class CompetitionViewSet(viewsets.ModelViewSet):
    """ViewSet for Competition CRUD operations."""
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def teams(self, request, pk=None):
        """Get all teams for a competition."""
        competition = self.get_object()
        teams = competition.teams.all()
        serializer = TeamSerializer(teams, many=True)
        return Response({'teams': serializer.data})
    
    @action(detail=True, methods=['get'])
    def judges(self, request, pk=None):
        """Get all judges for a competition."""
        competition = self.get_object()
        judges = competition.judges.all()
        serializer = JudgeSerializer(judges, many=True)
        return Response({'judges': serializer.data})
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get leaderboard for a competition."""
        competition = self.get_object()
        leaderboard = (
            Team.objects.filter(competition=competition)
            .annotate(avg_score=Avg('scores__total_score'), votes=Count('scores'))
            .filter(votes__gt=0)
            .order_by('-avg_score')
            .values('name', 'avg_score', 'votes')
        )
        return Response({'leaderboard': list(leaderboard)})


class JudgeViewSet(viewsets.ModelViewSet):
    """ViewSet for Judge CRUD operations."""
    queryset = Judge.objects.all()
    serializer_class = JudgeSerializer
    
    def get_permissions(self):
        if self.action in ['login', 'list']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Judge login with PIN."""
        serializer = JudgeLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pin = serializer.validated_data['pin']
        
        try:
            judge = Judge.objects.get(pin=pin)
        except Judge.DoesNotExist:
            # Create new judge with this PIN
            name = f"Judge-{pin}"
            judge = Judge.objects.create(name=name, pin=pin)
        
        return Response({
            'success': True,
            'judge': JudgeSerializer(judge).data
        })


class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team CRUD operations."""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class ScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for Score CRUD operations."""
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [AllowAny()]  # Judges submit without auth (PIN-based)
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit a score from judge panel."""
        serializer = ScoreSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            judge = Judge.objects.get(id=data['judge_id'])
        except Judge.DoesNotExist:
            return Response({'error': 'Judge not found'}, status=404)
        
        try:
            competition = Competition.objects.get(id=data['competition_id'])
        except Competition.DoesNotExist:
            return Response({'error': 'Competition not found'}, status=404)
        
        # Find or create team
        team, created = Team.objects.get_or_create(
            competition=competition,
            name=data['team_name'],
            defaults={'school_name': ''}
        )
        
        # Check if judge already scored this team
        existing_score = Score.objects.filter(team=team, judge=judge).first()
        if existing_score:
            # Update existing score
            existing_score.innovation_score = data['innovation']
            existing_score.impact_score = data['impact']
            existing_score.presentation_score = data['presentation']
            existing_score.comments = data.get('comments', '')
            existing_score.save()
            score = existing_score
        else:
            # Create new score
            score = Score.objects.create(
                team=team,
                judge=judge,
                innovation_score=data['innovation'],
                impact_score=data['impact'],
                presentation_score=data['presentation'],
                comments=data.get('comments', '')
            )
        
        return Response({
            'success': True,
            'total_score': float(score.total_score)
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    """Global leaderboard across all competitions."""
    leaderboard_data = (
        Team.objects.annotate(
            avg_score=Avg('scores__total_score'),
            votes=Count('scores')
        )
        .filter(votes__gt=0)
        .order_by('-avg_score')[:20]
        .values('name', 'avg_score', 'votes')
    )
    return Response({'leaderboard': list(leaderboard_data)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Dashboard statistics for admin panel."""
    today = timezone.now().date()
    
    # Basic counts
    competitions_count = Competition.objects.count()
    judges_count = Judge.objects.count()
    teams_scored_count = Team.objects.annotate(score_count=Count('scores')).filter(score_count__gt=0).count()
    
    # Recent activity
    recent_competitions = (
        Competition.objects
        .order_by('-created_at')[:5]
        .values('name', 'created_at')
    )
    recent_scores = (
        Score.objects
        .order_by('-submitted_at')[:5]
        .values('team__name', 'total_score', 'submitted_at')
    )
    
    activity = []
    for comp in recent_competitions:
        activity.append({
            'action': 'Competition Created',
            'details': comp['name'],
            'time': comp['created_at'].isoformat(),
            'type': 'create'
        })
    for score in recent_scores:
        activity.append({
            'action': 'Score Submitted',
            'details': f"{score['team__name']} ({round(float(score['total_score']), 1)})",
            'time': score['submitted_at'].isoformat(),
            'type': 'score'
        })
    
    # Sort by time
    activity.sort(key=lambda x: x['time'], reverse=True)
    activity = activity[:5]
    
    return Response({
        'stats': {
            'competitions_count': competitions_count,
            'judges_count': judges_count,
            'teams_scored_count': teams_scored_count
        },
        'recent_activity': activity
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics(request):
    """Advanced analytics for admin panel."""
    today = timezone.now().date()
    
    # Total metrics
    total_competitions = Competition.objects.count()
    active_judges = Judge.objects.filter(is_active=True).count()
    total_teams = Team.objects.count()
    total_scores = Score.objects.count()
    
    avg_score = Score.objects.aggregate(avg=Avg('total_score'))['avg'] or 0
    
    # Competition by status
    past_competitions = Competition.objects.filter(date__lt=today).order_by('-date')[:5]
    current_competitions = Competition.objects.filter(date=today).order_by('-date')[:5]
    future_competitions = Competition.objects.filter(date__gt=today).order_by('date')[:5]
    
    # Top teams
    top_teams = (
        Team.objects.annotate(
            total_score=Avg('scores__total_score'),
            evaluations=Count('scores')
        )
        .filter(evaluations__gt=0)
        .order_by('-total_score')[:10]
        .values('name', 'total_score', 'evaluations')
    )
    
    return Response({
        'analytics': {
            'total_competitions': total_competitions,
            'active_judges': active_judges,
            'total_teams': total_teams,
            'total_scores': total_scores,
            'average_score': float(avg_score),
            'past_competitions': CompetitionSerializer(past_competitions, many=True).data,
            'current_competitions': CompetitionSerializer(current_competitions, many=True).data,
            'future_competitions': CompetitionSerializer(future_competitions, many=True).data,
            'top_teams': list(top_teams)
        }
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def settings_view(request):
    """Get or update site settings."""
    settings = SiteSettings.get_settings()
    
    if request.method == 'GET':
        serializer = SiteSettingsSerializer(settings)
        return Response({'settings': serializer.data})
    
    elif request.method == 'POST':
        serializer = SiteSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Settings saved'})
        return Response(serializer.errors, status=400)


# ============================================================================
# SMART AI LIVE QUIZ & PROCTORING SYSTEM VIEWS
# ============================================================================

from .models import (
    QuizMaster, Question, Contestant, QuizSession, 
    QuizAnswer, QuizScore, ProctorAlert, NetworkLog
)
from .serializers import (
    QuizMasterSerializer, QuestionSerializer, ContestantSerializer,
    QuizSessionSerializer, QuizAnswerSerializer, QuizScoreSerializer,
    ProctorAlertSerializer, NetworkLogSerializer
)
import random


class QuizMasterViewSet(viewsets.ModelViewSet):
    """ViewSet for Quiz Master CRUD operations."""
    queryset = QuizMaster.objects.all()
    serializer_class = QuizMasterSerializer
    
    def get_permissions(self):
        if self.action in ['login']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Quiz Master login with PIN."""
        pin = request.data.get('pin')
        if not pin:
            return Response({'error': 'PIN required'}, status=400)
        
        try:
            qm = QuizMaster.objects.get(pin=pin, is_active=True)
            return Response({
                'success': True,
                'quiz_master': QuizMasterSerializer(qm).data
            })
        except QuizMaster.DoesNotExist:
            return Response({'error': 'Invalid PIN'}, status=401)


class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for Question CRUD operations."""
    queryset = Question.objects.filter(is_active=True)
    serializer_class = QuestionSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'random']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get a random question, optionally filtered."""
        queryset = Question.objects.filter(is_active=True)
        
        # Apply filters
        category = request.query_params.get('category')
        difficulty = request.query_params.get('difficulty')
        exclude_ids = request.query_params.get('exclude', '').split(',')
        exclude_ids = [int(x) for x in exclude_ids if x.isdigit()]
        
        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if exclude_ids:
            queryset = queryset.exclude(id__in=exclude_ids)
        
        if not queryset.exists():
            return Response({'error': 'No questions available'}, status=404)
        
        question = random.choice(list(queryset))
        return Response({'question': QuestionSerializer(question).data})
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all unique categories."""
        categories = Question.objects.values_list('category', flat=True).distinct()
        return Response({'categories': list(filter(None, categories))})
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create questions from list."""
        questions_data = request.data.get('questions', [])
        created = []
        for q_data in questions_data:
            serializer = QuestionSerializer(data=q_data)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
        return Response({'created': len(created), 'questions': created})


class ContestantViewSet(viewsets.ModelViewSet):
    """ViewSet for Contestant CRUD operations."""
    queryset = Contestant.objects.all()
    serializer_class = ContestantSerializer
    
    def get_permissions(self):
        if self.action in ['login', 'verify']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Contestant login with access code."""
        access_code = request.data.get('access_code')
        if not access_code:
            return Response({'error': 'Access code required'}, status=400)
        
        try:
            contestant = Contestant.objects.get(access_code=access_code, is_active=True)
            return Response({
                'success': True,
                'contestant': ContestantSerializer(contestant).data
            })
        except Contestant.DoesNotExist:
            return Response({'error': 'Invalid access code'}, status=401)
    
    @action(detail=True, methods=['post'])
    def verify_face(self, request, pk=None):
        """Verify contestant face (placeholder for AI verification)."""
        contestant = self.get_object()
        # TODO: Implement actual face verification
        contestant.is_verified = True
        contestant.save()
        return Response({'success': True, 'verified': True})


class QuizSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for Quiz Session CRUD operations."""
    queryset = QuizSession.objects.all()
    serializer_class = QuizSessionSerializer
    
    def get_permissions(self):
        if self.action in ['join', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a quiz session."""
        session = self.get_object()
        if session.status not in ['scheduled', 'waiting']:
            return Response({'error': 'Session cannot be started'}, status=400)
        
        session.status = 'live'
        session.started_at = timezone.now()
        session.save()
        return Response({'success': True, 'session': QuizSessionSerializer(session).data})
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a live session."""
        session = self.get_object()
        if session.status != 'live':
            return Response({'error': 'Session is not live'}, status=400)
        
        session.status = 'paused'
        session.save()
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume a paused session."""
        session = self.get_object()
        if session.status != 'paused':
            return Response({'error': 'Session is not paused'}, status=400)
        
        session.status = 'live'
        session.save()
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a quiz session."""
        session = self.get_object()
        session.status = 'completed'
        session.ended_at = timezone.now()
        session.save()
        
        # Calculate final scores for all contestants
        for contestant in session.contestants.all():
            score, created = QuizScore.objects.get_or_create(
                session=session, contestant=contestant
            )
            score.calculate_from_answers()
        
        return Response({'success': True, 'session': QuizSessionSerializer(session).data})
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Contestant joins a session."""
        session = self.get_object()
        contestant_id = request.data.get('contestant_id')
        
        try:
            contestant = Contestant.objects.get(id=contestant_id)
        except Contestant.DoesNotExist:
            return Response({'error': 'Contestant not found'}, status=404)
        
        session.contestants.add(contestant)
        
        # Create initial score record
        QuizScore.objects.get_or_create(session=session, contestant=contestant)
        
        if session.status == 'scheduled':
            session.status = 'waiting'
            session.save()
        
        return Response({'success': True, 'room_id': session.room_id})
    
    @action(detail=True, methods=['get'])
    def next_question(self, request, pk=None):
        """Get next random question for the session."""
        session = self.get_object()
        
        # Get IDs of already used questions
        used_ids = list(session.questions_used.values_list('id', flat=True))
        
        # Build query
        queryset = Question.objects.filter(is_active=True).exclude(id__in=used_ids)
        
        if session.category_filter:
            queryset = queryset.filter(category=session.category_filter)
        if session.difficulty_filter:
            queryset = queryset.filter(difficulty=session.difficulty_filter)
        
        if not queryset.exists():
            return Response({'error': 'No more questions available', 'completed': True})
        
        question = random.choice(list(queryset))
        session.questions_used.add(question)
        
        return Response({
            'question': QuestionSerializer(question).data,
            'question_number': session.questions_used.count(),
            'total_questions': session.total_questions
        })
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get session leaderboard."""
        session = self.get_object()
        scores = QuizScore.objects.filter(session=session).order_by('-final_score')
        
        leaderboard = []
        for i, score in enumerate(scores, 1):
            score.rank = i
            score.save()
            leaderboard.append({
                'rank': i,
                'contestant_name': score.contestant.name,
                'correct_answers': score.correct_answers,
                'total_questions': score.total_questions,
                'final_score': score.final_score,
                'accuracy': score.accuracy_percentage,
                'warnings': score.warnings_count,
                'is_disqualified': score.is_disqualified
            })
        
        return Response({'leaderboard': leaderboard})
    
    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Get all proctor alerts for this session."""
        session = self.get_object()
        alerts = ProctorAlert.objects.filter(session=session)
        return Response({'alerts': ProctorAlertSerializer(alerts, many=True).data})


class QuizAnswerViewSet(viewsets.ModelViewSet):
    """ViewSet for Quiz Answer operations."""
    queryset = QuizAnswer.objects.all()
    serializer_class = QuizAnswerSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit an answer during quiz."""
        session_id = request.data.get('session_id')
        contestant_id = request.data.get('contestant_id')
        question_id = request.data.get('question_id')
        answer = request.data.get('answer')
        time_taken = request.data.get('time_taken', 0)
        
        try:
            session = QuizSession.objects.get(id=session_id)
            contestant = Contestant.objects.get(id=contestant_id)
            question = Question.objects.get(id=question_id)
        except Exception as e:
            return Response({'error': str(e)}, status=404)
        
        # Check if answer is correct
        is_correct = answer.lower().strip() == question.correct_answer.lower().strip()
        
        # Create answer record
        quiz_answer = QuizAnswer.objects.create(
            session=session,
            contestant=contestant,
            question=question,
            answer_given=answer,
            is_correct=is_correct,
            time_taken=time_taken
        )
        
        # Update score
        score, _ = QuizScore.objects.get_or_create(session=session, contestant=contestant)
        score.calculate_from_answers()
        
        # Update contestant stats
        contestant.total_correct += 1 if is_correct else 0
        contestant.total_wrong += 0 if is_correct else 1
        contestant.total_points = score.final_score
        contestant.save()
        
        return Response({
            'success': True,
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'points_earned': quiz_answer.total_points,
            'total_score': score.final_score
        })


class ProctorAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for Proctor Alert operations."""
    queryset = ProctorAlert.objects.all()
    serializer_class = ProctorAlertSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def report(self, request):
        """Report a proctor alert from contestant client."""
        session_id = request.data.get('session_id')
        contestant_id = request.data.get('contestant_id')
        alert_type = request.data.get('alert_type')
        description = request.data.get('description', '')
        severity = request.data.get('severity', 'medium')
        ping_ms = request.data.get('ping_ms')
        
        try:
            session = QuizSession.objects.get(id=session_id)
            contestant = Contestant.objects.get(id=contestant_id)
        except Exception as e:
            return Response({'error': str(e)}, status=404)
        
        alert = ProctorAlert.objects.create(
            session=session,
            contestant=contestant,
            alert_type=alert_type,
            description=description,
            severity=severity,
            ping_ms=ping_ms
        )
        
        # Update warning count
        score, _ = QuizScore.objects.get_or_create(session=session, contestant=contestant)
        score.warnings_count += 1
        
        # Auto disqualify if max warnings exceeded
        if score.warnings_count >= session.max_warnings:
            score.is_disqualified = True
            score.disqualification_reason = f"Exceeded maximum warnings ({session.max_warnings})"
        
        score.save()
        
        return Response({
            'success': True,
            'alert_id': alert.id,
            'warnings_count': score.warnings_count,
            'is_disqualified': score.is_disqualified
        })
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Mark alert as reviewed."""
        alert = self.get_object()
        alert.is_reviewed = True
        alert.reviewed_by = request.user
        alert.review_notes = request.data.get('notes', '')
        alert.is_false_positive = request.data.get('false_positive', False)
        alert.save()
        
        # If false positive, reduce warning count
        if alert.is_false_positive:
            score = QuizScore.objects.filter(
                session=alert.session, contestant=alert.contestant
            ).first()
            if score and score.warnings_count > 0:
                score.warnings_count -= 1
                score.is_disqualified = False
                score.disqualification_reason = ''
                score.save()
        
        return Response({'success': True})


class NetworkLogViewSet(viewsets.ModelViewSet):
    """ViewSet for Network Log operations."""
    queryset = NetworkLog.objects.all()
    serializer_class = NetworkLogSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def log(self, request):
        """Log network status from contestant client."""
        session_id = request.data.get('session_id')
        contestant_id = request.data.get('contestant_id')
        ping_ms = request.data.get('ping_ms', 0)
        packet_loss = request.data.get('packet_loss', 0)
        jitter_ms = request.data.get('jitter_ms', 0)
        connection_type = request.data.get('connection_type', '')
        
        try:
            session = QuizSession.objects.get(id=session_id)
            contestant = Contestant.objects.get(id=contestant_id)
        except Exception as e:
            return Response({'error': str(e)}, status=404)
        
        log = NetworkLog.objects.create(
            session=session,
            contestant=contestant,
            ping_ms=ping_ms,
            packet_loss=packet_loss,
            jitter_ms=jitter_ms,
            connection_type=connection_type
        )
        
        # Create alert if network is poor
        if ping_ms > 120 or packet_loss > 5:
            ProctorAlert.objects.create(
                session=session,
                contestant=contestant,
                alert_type='network',
                severity='medium' if ping_ms <= 200 else 'high',
                description=f'Poor network: {ping_ms}ms ping, {packet_loss}% loss',
                ping_ms=ping_ms,
                packet_loss=packet_loss
            )
        
        return Response({
            'success': True,
            'status': log.status
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_dashboard_stats(request):
    """Dashboard statistics for quiz system."""
    stats = {
        'quiz_masters': QuizMaster.objects.filter(is_active=True).count(),
        'contestants': Contestant.objects.filter(is_active=True).count(),
        'questions': Question.objects.filter(is_active=True).count(),
        'sessions': QuizSession.objects.count(),
        'live_sessions': QuizSession.objects.filter(status='live').count(),
        'completed_sessions': QuizSession.objects.filter(status='completed').count(),
        'total_answers': QuizAnswer.objects.count(),
        'alerts_pending': ProctorAlert.objects.filter(is_reviewed=False).count(),
    }
    
    # Recent sessions
    recent_sessions = QuizSession.objects.order_by('-created_at')[:5]
    
    # Active alerts
    active_alerts = ProctorAlert.objects.filter(is_reviewed=False).order_by('-created_at')[:10]
    
    return Response({
        'stats': stats,
        'recent_sessions': QuizSessionSerializer(recent_sessions, many=True).data,
        'active_alerts': ProctorAlertSerializer(active_alerts, many=True).data
    })
