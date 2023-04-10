from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required

from django.db.models import Count
from django.db.models.functions import Random
from .models import Question
import random
from .models import UserAnswer
from django.http import JsonResponse

from django.core import serializers
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

@login_required
def home(request):
    return render(request, 'home.html', {'user': request.user})

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email address already exists.')
            return redirect('register')
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()
            messages.success(request, 'Account created successfully!')
            return redirect('home')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')

@login_required
def test(request):
    user = request.user
    answered_questions = UserAnswer.objects.filter(user=user).values_list('question_id', flat=True)
    unanswered_questions = Question.objects.exclude(id__in=answered_questions)
    questions_count = Question.objects.count()
    answered_questions_count = answered_questions.count()

    if unanswered_questions:
        question = random.choice(unanswered_questions)

        if request.method == 'POST':
            selected_choice = request.POST['selected_choice']
            user_answer = UserAnswer(user=request.user, question=question, answer=selected_choice)
            user_answer.save()

        return render(request, 'test.html', {'question': question, 'questions_count': questions_count, 'answered_questions_count': answered_questions_count})
    else:
        return render(request, 'done.html')

    

def success(request):
    return render(request, 'success.html')


def update_user_answer(request):
    print("Request method: ", request.method)
    print("X-Requested-With header: ", request.headers.get('X-Requested-With'))
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_id = request.user.id
        question_id = request.POST.get('question_id')
        selected_answer = request.POST.get('selected_answer')

        print("User ID: ", user_id)
        print("Question ID: ", question_id)
        print("Selected Answer: ", selected_answer)

            # Get the correct answer for the question
        question = Question.objects.get(id=question_id)
        correct_answer = question.answer

        # Get the index of the selected answer (A, B, C, D)
        answer_choices = question.choices
        selected_answer_index = answer_choices.index(selected_answer)

        # Map the index to a corresponding letter
        index_to_letter = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        selected_answer_letter = index_to_letter[selected_answer_index]

        # Compare the user's selected answer letter to the correct answer
        is_correct = selected_answer_letter == correct_answer

        # Update or create the UserAnswer
        user_answer, created = UserAnswer.objects.update_or_create(
            user_id=user_id, question_id=question_id,
            defaults={'answer': selected_answer_letter, 'correct': is_correct} # Update the 'correct' field here
        )
        user_answer.save()

        return JsonResponse({'message': 'UserAnswer updated'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@user_passes_test(lambda u: u.is_staff)  # Ensure that the user is an admin
def get_user_history(request, username):
    if username:
        target_user = User.objects.get(username=username)
        user_answers = UserAnswer.objects.filter(user=target_user)
        formatted_answers = []

        for answer in user_answers:
            formatted_answers.append({
                'question_id': answer.question.id,
                'correct': int(answer.correct)
            })

        return JsonResponse({'user_history': formatted_answers})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@user_passes_test(lambda u: u.is_staff)  # Ensure that the user is an admin
def get_all_users_history(request):
    all_users = User.objects.all()
    all_users_history = []

    for user in all_users:
        user_answers = UserAnswer.objects.filter(user=user)
        formatted_answers = []

        for answer in user_answers:
            formatted_answers.append({
                'question_id': answer.question.id,
                'correct': int(answer.correct)
            })

        user_history = {
            'username': user.username,
            'history': formatted_answers
        }
        all_users_history.append(user_history)

    return JsonResponse({'all_users_history': all_users_history})
    


@staff_member_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')