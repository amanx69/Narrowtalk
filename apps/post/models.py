from django.db import models
from django.contrib.auth import get_user_model

User=get_user_model()

from django.db import models
from django.conf import settings
from apps.Profile.models import Skill  


class Project(models.Model):
    class Stage(models.TextChoices):
        IDEA = "idea", "Idea"
        MVP = "mvp", "MVP"
        FUNDED = "funded", "Funded"
        SCALING = "scaling", "Scaling"

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.IDEA)
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    links = models.JSONField(default=dict, blank=True)  # e.g. {"website": "...", "pitch_deck": "..."}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class RoleNeeded(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="roles")
    title = models.CharField(max_length=100)  
    description = models.TextField(blank=True)
    required_skills = models.ManyToManyField(Skill, related_name="roles_requiring", blank=True)
    slots_available = models.PositiveIntegerField(default=1)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.project.title}"


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )
    role = models.ForeignKey(RoleNeeded, on_delete=models.CASCADE, related_name="applications")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "role") 
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.role} ({self.status})"


class Membership(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="memberships"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    role_title = models.CharField(max_length=100, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user} in {self.project} as {self.role_title}"