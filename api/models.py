from django.db import models


class User(models.Model):
    ROLE_CHOICES = [('student', 'Student'), ('alumni', 'Alumni'), ('admin', 'Admin')]
    STATUS_CHOICES = [('active', 'Active'), ('blocked', 'Blocked')]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='student_profile')
    branch = models.CharField(max_length=255, blank=True, default='')
    year = models.CharField(max_length=50, blank=True, default='')
    skills = models.TextField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    avatar = models.CharField(max_length=255, blank=True, default='')
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, default='')
    resume_name = models.CharField(max_length=255, blank=True, default='')
    resume_text = models.TextField(blank=True, default='')  # extracted text, used for skill matching
    resume_uploaded_at = models.DateTimeField(null=True, blank=True)


class AlumniProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='alumni_profile')
    company = models.CharField(max_length=255, blank=True, default='')
    position = models.CharField(max_length=255, blank=True, default='')
    graduation_year = models.CharField(max_length=50, blank=True, default='')
    branch = models.CharField(max_length=255, blank=True, default='')
    experience = models.CharField(max_length=255, blank=True, default='')
    skills = models.TextField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    avatar = models.CharField(max_length=255, blank=True, default='')


class Opportunity(models.Model):
    TYPE_CHOICES = [('job', 'Job'), ('internship', 'Internship')]

    alumni = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    apply_link = models.CharField(max_length=500, blank=True, default='')
    # ---- requirements used to filter applicants' resumes ----
    required_skills = models.TextField(blank=True, default='')      # comma separated
    required_branch = models.CharField(max_length=255, blank=True, default='')  # comma separated, empty = any
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'), ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'), ('selected', 'Selected'),
    ]

    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('opportunity', 'student')


class MentorshipRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('accepted', 'Accepted'),
        ('rejected', 'Rejected'), ('completed', 'Completed'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_mentorships')
    alumni = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_mentorships')
    field = models.CharField(max_length=255, blank=True, default='')
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Event(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    event_date = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
