from rest_framework.routers import DefaultRouter
from .views import * 

router = DefaultRouter()


router.register('manage_user', ManageUserViewSet, basename = 'manage_user')
router.register('profiles', ProfileViewSet, basename='profile')
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