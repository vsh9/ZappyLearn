# worksheet_generator/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

class Worksheet(models.Model):
    SUBJECT_CHOICES = [
        ('math', 'Mathematics'),
        ('science', 'Science'),
        ('english', 'English'),
        ('history', 'History'),
        ('geography', 'Geography'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_mood = models.CharField(max_length=100)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    grade_level = models.CharField(max_length=10, default='5-10')
    motivation_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='worksheets/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} worksheet for {self.user_mood} mood"

class Question(models.Model):
    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE, related_name='questions')
    difficulty = models.CharField(max_length=10, choices=Worksheet.DIFFICULTY_CHOICES)
    question_text = models.TextField()
    answer = models.TextField(blank=True, null=True)
    hints = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'difficulty']
    
    def __str__(self):
        return f"{self.difficulty} - {self.question_text[:50]}..."

class UserSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    mood_analysis = models.JSONField(blank=True, null=True)
    preferences = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session {self.session_id}"