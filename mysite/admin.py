from django.contrib import admin
from .models import Question, UserAnswer
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'model', 'mastered_components', 'inappropriate_components', 
                    'diagnostic_test_ids', 'remaining_question_ids')

class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'correct')


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
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserAnswer, UserAnswerAdmin)
