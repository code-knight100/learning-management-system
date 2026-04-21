from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# Create your models here.


# Profile table: 
class Profile(models.Model):
    user= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=50, blank = True , null = True)
    phone = models.CharField(max_length=15, blank = True, null = True )
    profile_image = models.ImageField(upload_to="profile_img/",  blank= True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return (f"{self.user.username}")
    
# Course table: 
class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ("BR","Beginner"),
        ("IN","Intermmediate"),
        ("AD","Advanced")
    ]
    title = models.CharField(max_length=30, unique = True )
    description = models.TextField()
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null = True, related_name="courses")
    difficulty = models.CharField(max_length=2, choices = DIFFICULTY_CHOICES, default = "BR")  # enum is used
    price = models.DecimalField(max_digits=7, decimal_places=2)  # used to store price, FloatField has roundoff error
    created_at = models.DateTimeField(auto_now_add=True)  # time is added automatically only once
    updated_at = models.DateTimeField(auto_now=True)  # time is changes when you update and save
    course_image = models.ImageField(upload_to='course_img/', null = True, blank = True)
    video = models.FileField(upload_to="course_vid/", null=True, blank=True)

    def __str__(self):
        return self.title
    
# Enrollment table: 
class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("AC", "Active"),
        ("CO", "Completed"),
        ("DR", "Dropped")
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="enrollments")  # don't let delete student if he has enrolled
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="enrollments") # don't delete course if students have enrolled in it
    progress = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(max_length = 2, choices = STATUS_CHOICES, default = "AC")
    enrolled_at = models.DateField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
# Lesson table: 
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=50)
    content = models.TextField()
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
# Assingment table: 
class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=50)
    description = models.TextField()
    total_marks = models.IntegerField()
    deadline = models.DateField()  # only DateField here to add deadline mannully 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
   
    
    
# Submission table: 
class Submission(models.Model):
    SUBMISSION_STATUS = [
        ("NS", "Not submitted yet"), 
        ("SB", "Submitted"), 
    ]
    EVALUATION_CHOICES = [
        ("PN", "Pending"), 
        ("RV" , "Reviewed"),
        ("AP" , "Approved"),
        ("RJ" , "Rejected")
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null = True, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null = True, related_name="submissions")
    file = models.FileField(upload_to="file/", blank = True, null = True)
    answer_text = models.TextField(null = True, blank = True)
    marks_obtained = models.IntegerField(blank = True, null = True )
    submitted_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)
    submission_status = models.CharField(max_length=2, choices = SUBMISSION_STATUS, default="NS")
    evaluation_status = models.CharField(max_length=2, choices = EVALUATION_CHOICES, default = "PN")
    
# Sponser table: 
class Sponsor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)  # one user(sponsor) can become only one sponsor
    organization_name = models.CharField(max_length=50)
    total_fund= models.DecimalField(max_digits=12, decimal_places = 2)

    def __str__(self):
        return self.user.username
    
    
# Sponsorship table: 
class Sponsorship(models.Model):
    SPONSORSHIP_CHOICES = [
        ("PN", "Pending"),
        ("AP", "Approved"),
        ("RJ", "Rejected"),
        ("AC", "Active"),
        ("FN", "Finished")
    ]
    sponsor= models.ForeignKey(Sponsor, on_delete=models.PROTECT, related_name="sponsorships")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sponsorships")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="sponsorships")
    amount = models.DecimalField(max_digits=10, decimal_places = 2)
    funded_at = models.DateTimeField(null = True, blank = True)  # set when funding actually happens
    status = models.CharField(max_length = 2, choices = SPONSORSHIP_CHOICES, default = "PN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # records time/date if anything like: amount correction is needed 

    def __str__(self):
        sponsor_name = self.sponsor.user.username if self.sponsor_id and self.sponsor.user_id else "Unknown sponsor"
        course_name = self.course.title if self.course_id else "Unknown course"
        return f"{sponsor_name} - {course_name}"
    
# Payment table: 
class Payment(models.Model):
    PAYMENT_CHOICES = [
        ("CH", "Cash"),
        ("ES", "E-Sewa"),
        ("KH", "Khalti"),
        ("IM", "IME-Pay"),
        ("OT", "Other")
    ]
    other_payment_option = models.CharField(max_length=50, null = True, blank = True)  # char field to enter other payment option 
    
    STATUS_CHOICES = [
        ("PN", "Pending"),
        ("PP", "Partially Paid"),
        ("FP", "Fully Paid"),
        ("RF", "Refunded")
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")  # who paid
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="payments")  # what they paid for
    sponsorship = models.ForeignKey(Sponsorship,on_delete=models.PROTECT,null=True,blank=True, related_name="payments")  # optional, only if sponsored
    amount = models.DecimalField(max_digits = 12, decimal_places = 2)
    payment_method = models.CharField(max_length=2, choices = PAYMENT_CHOICES, default = "CH")
    transaction_id = models.CharField(max_length=50, unique = True, db_index = True ) #  db_index = True makes search fast 
    payment_date= models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length=2, choices = STATUS_CHOICES, default = "PN")
    updated_at = models.DateTimeField(auto_now=True)   # record status changes like: pending, paid etc. 
    
# Notification table: 
class Notification(models.Model):
    TYPE_CHOICES = [
        ("IN", "Informative"), 
        ("WR", "Warning"), 
        ("AL", "Alert")
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_notifications", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    message = models.TextField()
    type = models.CharField(max_length= 2, choices = TYPE_CHOICES, default = "IN")
    is_read = models.BooleanField(default = False)
    created_at= models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True) 
    
# Emaillog table: 
class EmailLog(models.Model):
    STATUS_CHOICES = [
        ("PN", "Pending"), 
        ("SN", "Sent"), 
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_logs")
    subject = models.CharField(max_length=100)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add= True)
    status = models.CharField(max_length=2, choices = STATUS_CHOICES, default = "PN")
    
    
    
    
    
    
    



