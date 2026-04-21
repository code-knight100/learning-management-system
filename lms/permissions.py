from rest_framework.permissions import *
from .models import Enrollment
from django.utils import timezone


# ---------------- ROLE HELPER ----------------

def has_role(user, role):
    if not user or not user.is_authenticated:
        return False

    role_map = {
        "Admin": "AD",
        "Instructor": "IN",
        "Student": "ST",
        "Sponsor": "SP",
    }

    expected_code = role_map.get(role)
    return user.groups.filter(name=role).exists() or getattr(user, "role", None) == expected_code


# ---------------- GLOBAL GENERIC PERMISSIONS ----------------


class IsAdminOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):

        user = request.user

        # 👑 Admin has full access
        if has_role(user, "Admin"):
            return True

        # 🔑 Owner-based access (generic fallback)
        if hasattr(obj, "user"):
            return obj.user == user

        if hasattr(obj, "student"):
            return obj.student == user

        if hasattr(obj, "instructor"):
            return obj.instructor == user

        return False
    


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return has_role(request.user, "Admin")


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return has_role(request.user, "Instructor")


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return has_role(request.user, "Student")


class IsSponsor(BasePermission):
    def has_permission(self, request, view):
        return has_role(request.user, "Sponsor")


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ["GET", "HEAD", "OPTIONS"]


# ---------------- COURSE ----------------

class CoursePermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # CREATE only Admin + Instructor
        if request.method == "POST":
            return has_role(user, "Instructor") or has_role(user, "Admin")

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if has_role(user, "Admin"):
            return True

        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj.instructor == user

        return True


# ---------------- ENROLLMENT ----------------

class EnrollmentPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if has_role(user, "Admin"):
            return True

        # Students can create their own enrollment.
        if request.method == "POST":
            return has_role(user, "Student")

        if request.method in SAFE_METHODS:
            return (
                has_role(user, "Student")
                or has_role(user, "Instructor")
                or has_role(user, "Sponsor")
            )

        if request.method in ["PUT", "PATCH"]:
            return has_role(user, "Instructor")

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if has_role(user, "Admin"):
            return True

        if request.method in SAFE_METHODS:
            if has_role(user, "Student"):
                return obj.student == user

            if has_role(user, "Instructor"):
                return obj.course.instructor == user

            if has_role(user, "Sponsor"):
                return True

        if request.method in ["PUT", "PATCH"] and has_role(user, "Instructor"):
            return obj.course.instructor == user

        return False


# ---------------- LESSON ----------------

class LessonPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return (
                has_role(user, "Student")
                or has_role(user, "Instructor")
                or has_role(user, "Sponsor")
                or has_role(user, "Admin")
            )

        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return has_role(user, "Instructor") or has_role(user, "Admin")

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if has_role(user, "Admin"):
            return True

        if request.method in SAFE_METHODS:
            if has_role(user, "Instructor"):
                return obj.course.instructor == user

            if has_role(user, "Student"):
                return obj.course.enrollments.filter(student=user).exists()

            if has_role(user, "Sponsor"):
                return True

        return obj.course.instructor == user


# ---------------- ASSIGNMENT ----------------

class AssignmentPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return (
                has_role(user, "Student")
                or has_role(user, "Instructor")
                or has_role(user, "Admin")
            )

        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return has_role(user, "Instructor") or has_role(user, "Admin")

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if has_role(user, "Admin"):
            return True

        if request.method in SAFE_METHODS:
            if has_role(user, "Student"):
                return Enrollment.objects.filter(student=user, course=obj.course).exists()

            if has_role(user, "Instructor"):
                return obj.course.instructor == user

            return False

        return obj.course.instructor == user


# ---------------- SUBMISSION ----------------

class SubmissionPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if has_role(user, "Admin"):
            return True

        if request.method in SAFE_METHODS:
            return has_role(user, "Student") or has_role(user, "Instructor")

        if request.method == "POST":
            return has_role(user, "Student")

        if request.method in ["PUT", "PATCH"]:
            return has_role(user, "Student") or has_role(user, "Instructor")

        if request.method == "DELETE":
            return False

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if has_role(user, "Admin"):
            return True

        if request.method in SAFE_METHODS:
            if has_role(user, "Student"):
                return obj.student == user

            if has_role(user, "Instructor"):
                return obj.assignment and obj.assignment.course.instructor == user

            return False

        if request.method in ["PUT", "PATCH"]:
            if has_role(user, "Student"):
                return (
                    obj.student == user
                    and obj.assignment
                    and obj.assignment.deadline >= timezone.now().date()
                )

            if has_role(user, "Instructor"):
                return obj.assignment and obj.assignment.course.instructor == user

        return False


# ---------------- SPONSORSHIP ----------------

class SponsorPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if has_role(user, "Admin"):
            return True

        if has_role(user, "Sponsor"):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if has_role(user, "Admin"):
            return True

        if has_role(user, "Sponsor"):
            return obj.user == user

        return False

class SponsorshipPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if has_role(user, "Admin"):
            return True

        if request.method in SAFE_METHODS:
            return (
                has_role(user, "Sponsor")
                or has_role(user, "Student")
                or has_role(user, "Instructor")
            )

        if request.method == "POST":
            return has_role(user, "Sponsor")

        if request.method in ["PUT", "PATCH", "DELETE"]:
            return has_role(user, "Sponsor")

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if has_role(user, "Admin"):
            return True

        if request.method in SAFE_METHODS:
            if has_role(user, "Sponsor"):
                return obj.sponsor.user == user

            if has_role(user, "Student"):
                return obj.student == user

            if has_role(user, "Instructor"):
                return obj.course.instructor == user

            return False

        if has_role(user, "Sponsor"):
            return obj.sponsor.user == user

        return False


# ---------------- PAYMENT ----------------

class PaymentPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if has_role(user, "Admin"):
            return request.method in SAFE_METHODS or request.method in ["POST", "PUT", "PATCH"]

        if request.method in SAFE_METHODS:
            return has_role(user, "Student") or has_role(user, "Sponsor")

        if request.method == "POST":
            return has_role(user, "Student") or has_role(user, "Sponsor")

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if has_role(user, "Admin"):
            return request.method in SAFE_METHODS or request.method in ["PUT", "PATCH"]

        if request.method in SAFE_METHODS:
            return obj.user == user

        return False
