from collections.abc import Iterable
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.utils import timezone
from datetime import timedelta

class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, username, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, username, password, **other_fields)

    def create_user(self, email, username, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        
        other_fields.setdefault('is_active', True)
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        # password = make_password(password=password)
        user.set_password(password)
        user.save()
        return user
class NewUser(AbstractUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone_number = PhoneNumberField(default='1234567890')
    is_Email_Verified = models.BooleanField(default=False)
    is_Phone_Verified = models.BooleanField(default=False)
    # otp = models.CharField(max_length=6, null=True, blank=True)
    id = models.AutoField(primary_key=True)
    
    class Types(models.TextChoices):
        DOCTOR = "DOCTOR", "Doctor"
        PATIENT = "PATIENT", "Patient"
        ADMIN = "ADMIN", "Admin"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    
    type = models.CharField(_("Type"), max_length=50, choices=Types.choices, default=Types.ADMIN)

    objects = CustomAccountManager()

    # USERNAME_FIELD = 'username'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
    
class DoctorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs) -> QuerySet:
        return super().get_queryset(*args, **kwargs).filter(type=NewUser.Types.DOCTOR)

class PatientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs) -> QuerySet:
        return super().get_queryset(*args, **kwargs).filter(type=NewUser.Types.PATIENT)

class IntermediateManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs) -> QuerySet:
        return super().get_queryset(*args, **kwargs).filter(type=NewUser.Types.INTERMEDIATE)
    
class AppointmentManager(BaseUserManager):
    def upcoming_appointments(self):
        """
        Get a queryset for all upcoming appointments.
        """
        return self.filter(meeting_Date_Time__gt=timezone.now())

    def past_appointments(self):
        """
        Get a queryset for all past appointments.
        """
        return self.filter(meeting_Date_Time__lt=timezone.now())

    def chat_appointments(self):
        """
        Get a queryset for all appointments of type CHAT.
        """
        return self.filter(meeting_Type=Appointment.MeetingType.CHAT)

    def videocall_appointments(self):
        """
        Get a queryset for all appointments of type VIDEOCALL.
        """
        return self.filter(meeting_Type=Appointment.MeetingType.VIDEOCALL)

class Patient(NewUser):
    class SeverityType(models.TextChoices):
        MILD = "MILD", "Mild",
        SEVERE = "SEVERE", "Severe"
    blood_Group = models.CharField(_("Blood group"), max_length=4, default="Blood group not mentioned.")
    ailments = models.CharField(_("Ailments"), max_length=500, default="None")
    severity = models.CharField(_("Severity"), max_length=20, choices=SeverityType.choices, default=SeverityType.MILD, blank=True, null=True)
    disease = models.TextField(verbose_name="Information about disease", null=True, blank=True)
    objects = PatientManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = NewUser.Types.PATIENT
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
class Doctor(NewUser):
    about = models.CharField(max_length=200)
    speciality = models.CharField(max_length=100)
    objects = DoctorManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = NewUser.Types.DOCTOR
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
    
class Intermediate(NewUser):
    about = models.CharField(max_length=200)
    objects = IntermediateManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = NewUser.Types.INTERMEDIATE
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Intermediate person"
        verbose_name_plural = "Intermediate people"

class Appointment(models.Model):
    class MeetingType(models.TextChoices):
        CHAT = "CHAT", "Chat"
        VIDEOCALL = "VIDEOCALL", "Videocall"
    
    intermediate = models.ForeignKey(Intermediate, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    time_difference = timedelta(hours=5, minutes=30)  # Adjust this according to your time difference
    server_time = timezone.now() - time_difference
    meeting_Date_Time = models.DateTimeField(verbose_name="Meeting Date and Time", default=server_time)
    meeting_Type = models.CharField(_("Meeting type"), max_length=50, choices=MeetingType.choices, default=MeetingType.CHAT)
    disease = models.TextField(verbose_name="Information about disease", null=True)
    video_URL = models.URLField(verbose_name="Meet link", blank=True, null=True)
    objects = AppointmentManager()

    def save(self, *args, **kwargs):
        # if self.meeting_Type == Appointment.MeetingType.VIDEOCALL and not self.video_URL:
        #     # If it's a videocall appointment and no video_URL is provided, set it based on the frontend value
        #     # Assuming you have a field in the frontend named 'frontend_video_url', replace it with your actual field
        #     video_URL = getattr(self, 'video_URL', None)
            
        #     if frontend_video_url:
        #         self.video_URL = video_URL
        #     else:
        #         # Handle the case where no video_URL is provided from the frontend
        #         raise ValueError("Video URL is required for videocall appointments.")

        # # You can add more custom logic as needed
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"



    