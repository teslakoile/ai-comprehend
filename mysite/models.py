from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    id = models.IntegerField(primary_key=True)
    passage = models.TextField()
    question_text = models.TextField()
    choices = models.JSONField()
    answer = models.CharField(max_length=2)
    knowledge_component = models.CharField(max_length=255)
    relevant_sentences = models.JSONField(default=list)
    choices_in_complete_thought = models.JSONField(default=list)
    dc_score = models.FloatField(default=0.0)
    difficulty_score = models.FloatField(default=0.0)

    def __str__(self):
        return self.question_text
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    history = models.TextField(blank=True, default='')

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1)
    correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'question')