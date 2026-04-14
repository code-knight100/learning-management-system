from django.shortcuts import render

# Create your views here.

from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import * 

class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrInstructor]


class EnrollmentViewSet(ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStudentRole]


class LessonViewSet(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsStudentOrInstructor]


class AssignmentViewSet(ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsInstructorRole]


class SubmissionViewSet(ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudentRole]


class SponsorViewSet(ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    permission_classes = [IsSponsorRole]


class SponsorshipViewSet(ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [IsSponsorRole]


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [CanMakePayment]


class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminOrInstructor]


class EmailLogViewSet(ModelViewSet):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAdminOrInstructor]
