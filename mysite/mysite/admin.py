from django.contrib import admin
from .models import Question
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import UserAnswer

admin.site.register(Question)

class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0

class UserAdmin(DefaultUserAdmin):
    inlines = [UserAnswerInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
