from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import JSONField


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
    explanation = models.TextField(default='')

    def __str__(self):
        return self.question_text
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    history = JSONField(default=list, blank=True)
    remaining_question_ids = ArrayField(models.IntegerField(), default=list)
    diagnostic_test_ids = ArrayField(models.IntegerField(), default=list)
    mastered_components = ArrayField(models.CharField(max_length=255), default=list)
    inappropriate_components = ArrayField(models.CharField(max_length=255), default=list)
    model = models.CharField(max_length=50, default='')
    in_diagnostic = models.BooleanField(default=False)
    in_review = models.BooleanField(default=False)

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1)
    correct = models.BooleanField(default=False)
    submission_time = models.DateTimeField(default=timezone.now)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)  # Call the "real" save() method.
    #     user_profile = UserProfile.objects.get(user=self.user)
    #     history_entry = {"question_id": self.question.id, "correct": int(self.correct)}
    #     user_profile.history.append(history_entry)
    #     user_profile.save()

    class Meta:
        unique_together = ('user', 'question')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()