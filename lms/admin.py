from django.contrib import admin
from .models import *

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "address", "created_at", "updated_at")
    search_fields = ("user__username", "phone")
    list_filter = ("created_at",)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id","title", "instructor", "difficulty", "price", "created_at", "updated_at")
    search_fields = ("title", "instructor__username")
    list_filter = ("difficulty",)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id","student", "course", "progress", "status", "enrolled_at", "updated_at")
    search_fields = ("student__username", "course__title")
    list_filter = ("status", "enrolled_at")

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id","course", "title", "order", "created_at")
    search_fields = ("title", "course__title")
    list_filter = ("created_at",)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("id","course", "title", "total_marks", "deadline", "created_at")
    search_fields = ("title", "course__title")
    list_filter = ("deadline",)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id","assignment", "student", "submission_status", "evaluation_status", "submitted_at")
    search_fields = ("student__username", "assignment__title")
    list_filter = ("submission_status", "evaluation_status")

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ("id","user", "organization_name", "total_fund")
    search_fields = ("user__username", "organization_name")

@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ("id","sponsor", "student", "course", "amount", "status", "funded_at", "updated_at")
    search_fields = ("student__username", "course__title", "sponsor__organization_name")
    list_filter = ("status",)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id","user", "course", "amount", "payment_method", "status", "payment_date")
    search_fields = ("user__username", "transaction_id", "course__title")
    list_filter = ("status", "payment_method")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id","user", "type", "is_read", "created_at")
    search_fields = ("user__username", "message")
    list_filter = ("type", "is_read")

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("id","user", "subject", "status", "sent_at")
    search_fields = ("user__username", "subject")
    list_filter = ("status",)
