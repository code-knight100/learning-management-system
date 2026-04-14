from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register('profiles', ProfileViewSet)
router.register('courses', CourseViewSet)
router.register('enrollments', EnrollmentViewSet)
router.register('lessons', LessonViewSet)
router.register('assignments', AssignmentViewSet)
router.register('submissions', SubmissionViewSet)
router.register('sponsors', SponsorViewSet)
router.register('sponsorships', SponsorshipViewSet)
router.register('payments', PaymentViewSet)
router.register('notifications', NotificationViewSet)
router.register('email-logs', EmailLogViewSet)

urlpatterns = router.urls