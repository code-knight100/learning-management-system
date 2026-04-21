from django.shortcuts import render
from django.db.models.deletion import ProtectedError

from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import * 
from rest_framework.exceptions import ValidationError

from rest_framework import viewsets
from .serializers import *

from rest_framework import status
from rest_framework.response import Response
from users.serializers import RegisterSerializer


from .permissions import *
from django.db.models import Q

from rest_framework.exceptions import PermissionDenied



User = get_user_model()



# user views: 
class ManageUserViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAdminOrOwner]

  
    # queryset control: 
 
    def get_queryset(self):
        user = self.request.user

        if user.role == "AD":
            return User.objects.all()

        return User.objects.filter(id=user.id)

  
    # serializer control: 
   
    def get_serializer_class(self):

        if self.action == "create":
            return RegisterSerializer

        return UserSerializer


    # delete protection: 

    def destroy(self, request, *args, **kwargs):

        user = self.get_object()

        # permission check (your existing logic)
        if request.user.role != "AD" and request.user != user:
            return Response({"detail": "Not allowed"}, status=403)

        try:
            user.delete()

        except ProtectedError:
            return Response(
                {
                    "detail": "Cannot delete user. This user is linked to protected records (enrollments, payments, sponsorships, etc)."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "User deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
    
        
    def get_serializer_class(self):
        user = self.request.user

        # create: 
        if self.action == "create":
            return AdminUserSerializer

        # admin get/update/patch: 
        if user.role == "AD":
            return AdminUserSerializer

        # normal user: 
        if self.action in ["update", "partial_update"]:
            return UserSerializer

        return UserSerializer



# profile views: 
class ProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user

        if user.groups.filter(name="Admin").exists():
            return ProfileAdminSerializer

        return ProfileUserSerializer

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name="Admin").exists():
            return Profile.objects.all()

        return Profile.objects.filter(user=user)






# ---------------- COURSE ----------------

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [CoursePermission]

    def get_queryset(self):
        user = self.request.user

        # Instructor → view all courses
        if has_role(user, "Instructor"):
            return Course.objects.all()

        # Student → view all courses
        if has_role(user, "Student"):
            return Course.objects.all()

        # Sponsor → view all courses
        if has_role(user, "Sponsor"):
            return Course.objects.all()

        # Admin → full access
        return Course.objects.all()


# ---------------- ENROLLMENT ----------------

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [EnrollmentPermission]


    def get_queryset(self):
        user = self.request.user

        if has_role(user, "Student"):
            return Enrollment.objects.filter(student=user)

        if has_role(user, "Instructor"):
            return Enrollment.objects.filter(course__instructor=user)

        if has_role(user, "Sponsor"):
            return Enrollment.objects.all()
        
        if has_role(user, "Admin"):
            return Enrollment.objects.all()

        return Enrollment.objects.none()



    
    
    

# ---------------- LESSON ----------------

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [LessonPermission]

    def get_queryset(self):
        user = self.request.user

        if has_role(user, "Student"):
            return Lesson.objects.filter(course__enrollments__student=user).distinct()

        if has_role(user, "Instructor"):
            return Lesson.objects.filter(course__instructor=user)

        if has_role(user, "Sponsor"):
            return Lesson.objects.all()

        if has_role(user, "Admin"):
            return Lesson.objects.all()

        return Lesson.objects.none()


# ---------------- ASSIGNMENT ----------------

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [AssignmentPermission]

    def get_queryset(self):
        user = self.request.user

        if has_role(user, "Student"):
            enrolled_course_ids = Enrollment.objects.filter(student=user).values_list("course_id", flat=True)
            return Assignment.objects.filter(course_id__in=enrolled_course_ids)

        if has_role(user, "Instructor"):
            return Assignment.objects.filter(course__instructor=user)

        if has_role(user, "Admin"):
            return Assignment.objects.all()

        return Assignment.objects.none()


# ---------------- SUBMISSION ----------------

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [SubmissionPermission]

    def get_queryset(self):
        user = self.request.user

        if has_role(user, "Student"):
            return Submission.objects.filter(student=user)

        if has_role(user, "Instructor"):
            return Submission.objects.filter(assignment__course__instructor=user)

        if has_role(user, "Admin"):
            return Submission.objects.all()

        return Submission.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        full_data = self.get_serializer(serializer.instance).data
        response_data = {"id": full_data["id"]}

        for field_name in request.data.keys():
            if field_name in full_data:
                response_data[field_name] = full_data[field_name]

        headers = self.get_success_headers(full_data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


# ---------------- SPONSOR ----------------

class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    permission_classes = [SponsorPermission]

    def get_queryset(self):
        user = self.request.user

        if has_role(user, "Admin"):
            return Sponsor.objects.all()

        if has_role(user, "Sponsor"):
            return Sponsor.objects.filter(user=user)

        return Sponsor.objects.none()

    def destroy(self, request, *args, **kwargs):
        sponsor = self.get_object()

        try:
            sponsor.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": "Cannot delete sponsor profile. It is linked to protected sponsorship records."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------- SPONSORSHIP ----------------

class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [SponsorshipPermission]

    def get_queryset(self):
        user = self.request.user

        if has_role(user, "Sponsor"):
            return Sponsorship.objects.filter(sponsor__user=user)

        if has_role(user, "Student"):
            return Sponsorship.objects.filter(student=user)

        if has_role(user, "Instructor"):
            return Sponsorship.objects.filter(course__instructor=user)

        if has_role(user, "Admin"):
            return Sponsorship.objects.all()

        return Sponsorship.objects.none()


# ---------------- PAYMENT ----------------

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [PaymentPermission]

    def get_queryset(self):
        user = self.request.user

        if has_role(user, "Admin"):
            return Payment.objects.all()

        if has_role(user, "Student") or has_role(user, "Sponsor"):
            return Payment.objects.filter(user=user)

        return Payment.objects.none()


# ---------------- NOTIFICATION ----------------

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)


# ---------------- EMAIL LOG ----------------

class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer

    def get_queryset(self):
        user = self.request.user

        if has_role(user, "Admin"):
            return EmailLog.objects.all()

        return EmailLog.objects.none()
