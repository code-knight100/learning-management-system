from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from rest_framework.response import Response

from rest_framework import serializers
from .models import *
from django.utils import timezone
import secrets
import string



User = get_user_model()

# user serializer 1: 
class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            ]

    # create user safely: 
   
    def create(self, validated_data):

        password = validated_data.pop('password', None)

        user = User(**validated_data)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user


    # update user safely: 
   
    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
    

# user serialzer 2: 
class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'role'
        ]
        



    
    
# Profile serializer 1: 
class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['user']

    # Vvalidate and assign user: 
    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        # prevent duplicate profile: 
        if Profile.objects.filter(user=user).exists():
            raise serializers.ValidationError({
                "detail": "Profile already exists"
            })

        # inject user: 
        data['user'] = user

        return data

    def create(self, validated_data):
        return Profile.objects.create(**validated_data)



        

# profile serializer 2:     
class ProfileAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

    # 🔥 Validate user field
    def validate_user(self, value):
        if Profile.objects.filter(user=value).exists():
            raise serializers.ValidationError(
                "This user already has a profile"
            )
        return value

    def create(self, validated_data):
        return Profile.objects.create(**validated_data)
    
    












# ---------------- COURSE ----------------

class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user

        # 👇 Hide instructor field for Instructor role
        if user.groups.filter(name="Instructor").exists():
            fields.pop("instructor", None)

        return fields

    def validate(self, data):
        user = self.context["request"].user

        is_admin = user.groups.filter(name="Admin").exists()
        is_instructor = user.groups.filter(name="Instructor").exists()

        if not (is_admin or is_instructor):
            raise serializers.ValidationError("Not allowed")

        # Instructor always self-owned
        if is_instructor:
            data["instructor"] = user

        # Admin must provide valid instructor
        if is_admin:
            instructor = data.get("instructor")

            if not instructor:
                raise serializers.ValidationError("Instructor required")

            if not instructor.groups.filter(name="Instructor").exists():
                raise serializers.ValidationError("Selected user is not an instructor")

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user

        # Instructor cannot change ownership
        if user.groups.filter(name="Instructor").exists():
            validated_data["instructor"] = user

        # Admin validation
        if user.groups.filter(name="Admin").exists():
            instructor = validated_data.get("instructor", instance.instructor)

            if not instructor.groups.filter(name="Instructor").exists():
                raise serializers.ValidationError("Selected user is not an instructor")

        return super().update(instance, validated_data)
    
    

    
# ---------------- ENROLLMENT ----------------

class EnrollmentSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    instructor = serializers.StringRelatedField(source="course.instructor", read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role="ST"))
    status = serializers.ChoiceField(choices=Enrollment.STATUS_CHOICES, required=False)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "instructor",
            "student",
            "status",
            "progress",
            "enrolled_at",
            "updated_at",
        ]
        read_only_fields = ["id", "enrolled_at", "updated_at"]

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user
        request = self.context.get("request")

        if user.role == "ST":
            fields["student"].read_only = True

        if request and request.method == "POST":
            fields["status"].read_only = True
            fields["progress"].read_only = True

        if request and request.method in ["PUT", "PATCH"] and user.role == "IN":
            for field_name in ["id", "course", "instructor", "student", "enrolled_at", "updated_at"]:
                fields.pop(field_name, None)

        return fields

    def validate(self, data):
        user = self.context["request"].user
        request = self.context.get("request")

        is_admin = user.role == "AD"
        is_student = user.role == "ST"
        is_instructor = user.role == "IN"

        # ❌ only Student or Admin can create
        if request and request.method == "POST" and not (is_admin or is_student):
            raise serializers.ValidationError("Not allowed")

        if request and request.method in ["PUT", "PATCH"] and is_instructor:
            return data

        course = data.get("course")
        student = data.get("student")

        if is_student:
            student = user

        # 🔴 duplicate enrollment check
        if student and course and Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("Already enrolled")

        # 👇 Student creates own enrollment
        if is_student:
            data["student"] = user

        # 👇 Admin must assign valid student
        if is_admin:
            student = data.get("student")

            if not student:
                raise serializers.ValidationError("Student required")

            if student.role != "ST":
                raise serializers.ValidationError("Selected user is not a student")

        return data

    def create(self, validated_data):
        validated_data["status"] = "AC"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user

        # ❌ No update allowed for student
        if user.role == "ST":
            raise serializers.ValidationError("Students cannot update enrollment")

        # Instructors can update only progress and status on their own course enrollments.
        if user.role == "IN":
            validated_data = {
                "progress": validated_data.get("progress", instance.progress),
                "status": validated_data.get("status", instance.status),
            }

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["course"] = str(instance.course)
        data["student"] = str(instance.student)
        data["status"] = instance.get_status_display()
        return data
    

# ---------------- LESSON ----------------

class LessonSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField(source="course.instructor", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "instructor",
            "title",
            "content",
            "order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "instructor"]

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user

        if user.role == "IN":
            fields["course"].queryset = Course.objects.filter(instructor=user)

        return fields

    def validate(self, data):
        user = self.context["request"].user
        course = data.get("course", getattr(self.instance, "course", None))

        if user.role == "AD":
            return data

        if not course:
            raise serializers.ValidationError("Course required")

        if course.instructor != user:
            raise serializers.ValidationError("Not your course")

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["course"] = str(instance.course)
        return data


# ---------------- ASSIGNMENT ----------------

class AssignmentSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField(source="course.instructor", read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "id",
            "course",
            "instructor",
            "title",
            "description",
            "total_marks",
            "deadline",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "instructor"]

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user

        if user.role == "IN":
            fields["course"].queryset = Course.objects.filter(instructor=user)

        return fields

    def validate_deadline(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past")
        return value

    def validate(self, data):
        user = self.context["request"].user
        course = data.get("course", getattr(self.instance, "course", None))

        if user.role == "AD":
            return data

        if not course:
            raise serializers.ValidationError("Course required")

        if course.instructor != user:
            raise serializers.ValidationError("Not your course")

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["course"] = str(instance.course)
        return data


# ---------------- SUBMISSION ----------------

class SubmissionSerializer(serializers.ModelSerializer):
    assignment_name = serializers.StringRelatedField(source="assignment", read_only=True)
    course = serializers.StringRelatedField(source="assignment.course", read_only=True)
    instructor = serializers.StringRelatedField(source="assignment.course.instructor", read_only=True)
    student_name = serializers.StringRelatedField(source="student", read_only=True)
    submission_status = serializers.CharField(source="get_submission_status_display", read_only=True)
    evaluation_status = serializers.ChoiceField(choices=Submission.EVALUATION_CHOICES, required=False)

    class Meta:
        model = Submission
        fields = [
            "id",
            "assignment",
            "assignment_name",
            "course",
            "instructor",
            "student",
            "student_name",
            "file",
            "answer_text",
            "marks_obtained",
            "submission_status",
            "evaluation_status",
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student",
            "student_name",
            "assignment_name",
            "course",
            "instructor",
            "submission_status",
            "submitted_at",
            "updated_at",
        ]

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user
        request = self.context.get("request")

        if request and request.method == "POST":
            for field_name in [
                "assignment_name",
                "course",
                "student",
                "student_name",
                "marks_obtained",
                "submission_status",
                "evaluation_status",
                "submitted_at",
                "updated_at",
            ]:
                fields.pop(field_name, None)

        if user.role == "ST" and request and request.method in ["PUT", "PATCH"]:
            for field_name in ["marks_obtained", "evaluation_status"]:
                fields.pop(field_name, None)

        if user.role == "IN" and request and request.method in ["PUT", "PATCH"]:
            for field_name in [
                "id",
                "assignment",
                "assignment_name",
                "course",
                "instructor",
                "student",
                "student_name",
                "file",
                "answer_text",
                "submission_status",
                "submitted_at",
                "updated_at",
            ]:
                fields.pop(field_name, None)

        return fields

    def validate(self, data):
        user = self.context["request"].user
        request = self.context.get("request")
        assignment = data.get("assignment", getattr(self.instance, "assignment", None))

        if user.role == "AD":
            return data

        if user.role == "ST":
            if not assignment:
                raise serializers.ValidationError("Assignment required")

            # enrolled check
            if not Enrollment.objects.filter(student=user, course=assignment.course).exists():
                raise serializers.ValidationError("Not enrolled")

            # duplicate submission on create
            if (
                request
                and request.method == "POST"
                and Submission.objects.filter(student=user, assignment=assignment).exists()
            ):
                raise serializers.ValidationError("Already submitted")

            # deadline
            if assignment.deadline < timezone.now().date():
                raise serializers.ValidationError("Deadline passed")

            data["student"] = user
            data["submission_status"] = "SB"
            return data

        if user.role == "IN":
            return data

        raise serializers.ValidationError("Not allowed")

        return data

    def update(self, instance, validated_data):
        user = self.context["request"].user

        if user.role == "ST":
            validated_data = {
                "file": validated_data.get("file", instance.file),
                "answer_text": validated_data.get("answer_text", instance.answer_text),
            }

        if user.role == "IN":
            allowed_fields = {
                "marks_obtained": validated_data.get("marks_obtained", instance.marks_obtained),
            }
            if "evaluation_status" in validated_data:
                allowed_fields["evaluation_status"] = validated_data["evaluation_status"]
            validated_data = allowed_fields

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["evaluation_status"] = instance.get_evaluation_status_display()
        return data


# ---------------- SPONSOR ----------------

class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = "__all__"

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user

        fields["user"].queryset = User.objects.filter(role="SP")

        if user.role != "AD":
            fields["user"].read_only = True

        return fields

    def validate(self, data):
        user = self.context["request"].user
        request_user = self.context["request"].user
        target_user = data.get("user", getattr(self.instance, "user", request_user))

        if user.role == "AD":
            return data

        if Sponsor.objects.filter(user=request_user).exclude(pk=getattr(self.instance, "pk", None)).exists():
            raise serializers.ValidationError("Already a sponsor")

        data["user"] = target_user
        return data


# ---------------- SPONSORSHIP ----------------

class SponsoredStudentField(serializers.PrimaryKeyRelatedField):
    def display_value(self, instance):
        student_label = f"{instance.username} ({instance.get_role_display()})"
        course_titles = list(
            instance.enrollments.select_related("course").values_list("course__title", flat=True)
        )
        if course_titles:
            return f"{student_label} | Enrolled in → {', '.join(course_titles)}"
        return student_label


class PaymentStudentField(serializers.PrimaryKeyRelatedField):
    def display_value(self, instance):
        student_label = str(instance)
        course_titles = list(
            instance.enrollments.select_related("course").values_list("course__title", flat=True)
        )
        if course_titles:
            return f"{student_label} | Enrolled in → {', '.join(course_titles)}"
        return student_label

class SponsorshipSerializer(serializers.ModelSerializer):
    sponsor = serializers.PrimaryKeyRelatedField(queryset=Sponsor.objects.filter(user__role="SP"), required=False)
    student = SponsoredStudentField(queryset=User.objects.filter(role="ST"), required=True, allow_null=False)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    instructor = serializers.StringRelatedField(source="course.instructor", read_only=True)
    status = serializers.ChoiceField(choices=Sponsorship.SPONSORSHIP_CHOICES, required=False)

    class Meta:
        model = Sponsorship
        fields = [
            "id",
            "sponsor",
            "student",
            "course",
            "instructor",
            "amount",
            "funded_at",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "instructor", "created_at", "updated_at"]

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user
        fields["course"].queryset = Course.objects.filter(enrollments__isnull=False).distinct()

        if user.role == "SP":
            fields["sponsor"].read_only = True

        return fields

    def validate(self, data):
        user = self.context["request"].user
        sponsor = data.get("sponsor")
        student = data.get("student")
        course = data.get("course")

        if user.role == "AD":
            if not sponsor:
                raise serializers.ValidationError("Sponsor required")

            if not student:
                raise serializers.ValidationError("Student required")

            if student and student.role != "ST":
                raise serializers.ValidationError("Selected user is not a student")

            if student and course and not Enrollment.objects.filter(student=student, course=course).exists():
                raise serializers.ValidationError("The selected student is not enrolled in this course")

            if sponsor.user.role != "SP":
                raise serializers.ValidationError("Selected user is not a sponsor")

            if (
                sponsor
                and student
                and course
                and Sponsorship.objects.filter(
                    sponsor=sponsor,
                    student=student,
                    course=course
                ).exclude(pk=getattr(self.instance, "pk", None)).exists()
            ):
                raise serializers.ValidationError("Duplicate sponsorship")

            return data

        sponsor = Sponsor.objects.get(user=user)

        if not student:
            raise serializers.ValidationError("Student required")

        if not course:
            raise serializers.ValidationError("Course required")

        if student and student.role != "ST":
            raise serializers.ValidationError("Selected user is not a student")

        if student and course and not Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("The selected student is not enrolled in this course")

        if Sponsorship.objects.filter(
            sponsor=sponsor,
            student=student,
            course=course
        ).exclude(pk=getattr(self.instance, "pk", None)).exists():
            raise serializers.ValidationError("Duplicate sponsorship")

        data["sponsor"] = sponsor
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["sponsor"] = str(instance.sponsor.user)
        student = getattr(instance, "student", None)
        data["student"] = str(student) if student else None
        data["course"] = str(instance.course)
        data["status"] = instance.get_status_display()
        return data


# ---------------- PAYMENT ----------------

class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES, required=False)

    student = PaymentStudentField(queryset=User.objects.filter(role="ST"), required=False, allow_null=True, write_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "course",
            "student",
            "amount",
            "payment_method",
            "other_payment_option",
            "status",
            "transaction_id",
            "sponsorship",
            "payment_date",
            "updated_at",
        ]
        read_only_fields = ["id", "payment_date", "updated_at"]

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user
        request = self.context.get("request")

        if request and request.method == "POST" and user.role == "ST":
            fields.pop("sponsorship", None)
            fields.pop("student", None)
            fields.pop("status", None)

        if request and request.method == "POST" and user.role == "SP":
            fields.pop("status", None)

        if user.role == "SP":
            sponsor_sponsorships = Sponsorship.objects.filter(sponsor__user=user)
            fields["sponsorship"].queryset = sponsor_sponsorships
            fields["course"].queryset = Course.objects.filter(
                sponsorships__sponsor__user=user
            ).distinct()
            fields["student"].queryset = User.objects.filter(
                role="ST",
                sponsorships__sponsor__user=user,
            ).distinct()

        if user.role == "AD" and request and request.method == "POST":
            fields["sponsorship"].queryset = Sponsorship.objects.filter(
                student__isnull=False
            ).select_related("sponsor__user", "student", "course")
            fields["student"].required = True

        if request and request.method == "POST":
            fields["transaction_id"].read_only = True

        if user.role == "AD" and request and request.method in ["PUT", "PATCH"]:
            for field_name in [
                "student",
                "course",
                "amount",
                "payment_method",
                "other_payment_option",
                "transaction_id",
                "sponsorship",
                "payment_date",
                "updated_at",
            ]:
                fields.pop(field_name, None)

        return fields

    def _generate_transaction_id(self):
        alphabet = string.ascii_uppercase + string.digits

        while True:
            candidate = "TXN-" + "".join(secrets.choice(alphabet) for _ in range(10))
            if not Payment.objects.filter(transaction_id=candidate).exists():
                return candidate

    def validate(self, data):
        user = self.context["request"].user
        request = self.context.get("request")
        course = data.get("course", getattr(self.instance, "course", None))
        sponsorship = data.get("sponsorship", getattr(self.instance, "sponsorship", None))
        student = data.pop("student", None)
        payment_method = data.get("payment_method", getattr(self.instance, "payment_method", None))
        other_payment_option = data.get("other_payment_option", getattr(self.instance, "other_payment_option", None))

        if user.role not in ["ST", "SP", "AD"]:
            raise serializers.ValidationError("Not allowed")

        if request and request.method != "POST":
            if user.role == "AD":
                return data
            raise serializers.ValidationError("Payments cannot be edited after creation")

        if data["amount"] <= 0:
            raise serializers.ValidationError("Amount must be positive")

        if payment_method == "OT" and not other_payment_option:
            raise serializers.ValidationError("Please mention the other payment option")

        if user.role == "ST":
            data["user"] = user
            if course and not Enrollment.objects.filter(student=user, course=course).exists():
                raise serializers.ValidationError("The user is not enrolled in the selected course")
            if sponsorship and sponsorship.student and sponsorship.student != user:
                raise serializers.ValidationError("This sponsorship does not belong to you")

        elif user.role == "SP":
            data["user"] = user
            sponsor_profile = Sponsor.objects.filter(user=user).first()

            if student and not sponsorship:
                sponsorship = Sponsorship.objects.filter(
                    sponsor=sponsor_profile,
                    student=student,
                    course=course,
                ).first()
                if not sponsorship:
                    raise serializers.ValidationError("No sponsorship found for the selected student and course")
                data["sponsorship"] = sponsorship

            if sponsorship and sponsorship.sponsor.user != user:
                raise serializers.ValidationError("This sponsorship does not belong to you")
            if sponsorship and sponsor_profile and sponsorship.sponsor != sponsor_profile:
                raise serializers.ValidationError("This sponsorship does not belong to you")
            if student and sponsorship and sponsorship.student != student:
                raise serializers.ValidationError("Selected student does not match the selected sponsorship")
            if student and course and not Enrollment.objects.filter(student=student, course=course).exists():
                raise serializers.ValidationError("The user is not enrolled in the selected course")

        elif user.role == "AD":
            if not student:
                raise serializers.ValidationError("Student required")
            if student.role != "ST":
                raise serializers.ValidationError("Admin can only make payment for students")
            data["user"] = student
            if course and not Enrollment.objects.filter(student=student, course=course).exists():
                raise serializers.ValidationError("The user is not enrolled in the selected course")
            if sponsorship and sponsorship.student and sponsorship.student != student:
                raise serializers.ValidationError("Selected student does not match the selected sponsorship")

        if sponsorship and course and sponsorship.course != course:
            raise serializers.ValidationError("Selected sponsorship does not match the selected course")

        return data

    def create(self, validated_data):
        validated_data["transaction_id"] = self._generate_transaction_id()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user

        if user.role == "AD":
            validated_data = {
                "status": validated_data.get("status", instance.status)
            }

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["course"] = str(instance.course)
        student = None
        if instance.sponsorship and instance.sponsorship.student:
            student = instance.sponsorship.student
        elif getattr(instance.user, "role", None) == "ST":
            student = instance.user
        data["student"] = str(student) if student else None
        data["payment_method"] = instance.get_payment_method_display()
        data["status"] = instance.get_status_display()
        return data


# ---------------- NOTIFICATION ----------------

class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, write_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "user",
            "message",
            "type",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "sender", "created_at", "updated_at"]

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user
        request = self.context.get("request")

        if user.role != "AD":
            fields["sender"].read_only = True

        if user.role == "IN":
            fields["user"].queryset = User.objects.filter(
                role="ST",
                enrollments__course__instructor=user,
            ).distinct()

        if user.role == "SP":
            fields["user"].queryset = User.objects.filter(
                role="ST",
                sponsorships__sponsor__user=user,
            ).distinct()

        if request and request.method == "POST":
            fields["is_read"].read_only = True

        if user.role == "IN" and request and request.method in ["PUT", "PATCH"]:
            for field_name in ["is_read"]:
                fields.pop(field_name, None)

        if user.role == "SP" and request and request.method in ["PUT", "PATCH"]:
            for field_name in ["is_read"]:
                fields.pop(field_name, None)

        if user.role == "AD" and request and request.method in ["PUT", "PATCH"]:
            fields.pop("is_read", None)

        if user.role == "ST" and request and request.method in ["PUT", "PATCH"]:
            for field_name in ["sender", "user", "message", "type", "created_at", "updated_at", "id"]:
                fields.pop(field_name, None)

        return fields

    def validate(self, data):
        user = self.context["request"].user
        request = self.context.get("request")
        sender = data.get("sender", getattr(self.instance, "sender", None))
        recipient = data.get("user", getattr(self.instance, "user", None))

        if not data.get("message", getattr(self.instance, "message", None)):
            raise serializers.ValidationError("Message required")

        if request and request.method == "POST":
            if "is_read" in data and data.get("is_read"):
                raise serializers.ValidationError("Cannot mark notification as read during creation")

            if user.role == "AD":
                if not sender:
                    data["sender"] = user
                if not recipient:
                    raise serializers.ValidationError("User required")
                return data

            if user.role == "IN":
                if not recipient:
                    raise serializers.ValidationError("User required")
                data["sender"] = user
                return data

            if user.role == "SP":
                if not recipient:
                    raise serializers.ValidationError("User required")
                data["sender"] = user
                return data

            raise serializers.ValidationError("Not allowed")

        if request and request.method in ["PUT", "PATCH"]:
            if user.role == "ST":
                return data

            if user.role in ["IN", "SP", "AD"]:
                return data

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["sender"] = str(instance.sender) if instance.sender else None
        data["user"] = str(instance.user) if instance.user else None
        return data

    def update(self, instance, validated_data):
        user = self.context["request"].user

        if user.role == "ST":
            validated_data = {
                "is_read": validated_data.get("is_read", instance.is_read)
            }

        return super().update(instance, validated_data)



# ---------------- EMAIL LOG ----------------

class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = '__all__'
        read_only_fields = ['id']
