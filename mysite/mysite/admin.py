from django.contrib import admin
from .models import Question, UserAnswer
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User


def delete_user_history(modeladmin, request, queryset):
    for user in queryset:
        UserAnswer.objects.filter(user=user).delete()
    delete_user_history.short_description = "Delete selected users' history"


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0


class UserAdmin(DefaultUserAdmin):
    actions = [delete_user_history]
    inlines = [UserAnswerInline]


admin.site.register(Question)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
