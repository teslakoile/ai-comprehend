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
from django.utils import timezone

import json
from random import choice
from scipy.special import expit

# Load the necessary data and define the StudentModel class
with open('mysite/train/parameters.txt') as file:
    DEFAULT_PARAMETERS = file.read().replace('[', '').replace(']', '').replace('\n', ', ').replace(' ', '').split(',')
    DEFAULT_PARAMETERS = [float(i) for i in DEFAULT_PARAMETERS]

with open('mysite/Compiler/aicomprehend_annotated_dataset_v7.json') as file:
    MASTER_DATA = json.load(file)

class StudentModel:

    def __init__(self, student_id, student_history, student_parameters=DEFAULT_PARAMETERS):
        self.student_id = student_id
        self.student_history = student_history
        self.student_parameters = student_parameters
        self.correct_responses = {'literal': 0, 'inferential': 0, 'critical': 0}
        self.incorrect_responses = {'literal': 0, 'inferential': 0, 'critical': 0}
        self.pred_literal = 0
        self.pred_inferential = 0
        self.pred_critical = 0

        # Initialize the student's number of correct and incorrect responses for each knowledge component
        for response in self.student_history:
            question_id = response['question_id']
            knowledge_component = MASTER_DATA[question_id]['knowledge_component']
            if response['correct']:
                self.correct_responses[knowledge_component] += 1
            else:
                self.incorrect_responses[knowledge_component] += 1

    def pfa_model(self):
        beta_literal, gamma_literal, rho_literal, beta_inferential, gamma_inferential, rho_inferential, beta_critical, gamma_critical, rho_critical = self.student_parameters

        # Calculate the student's probability of answering each knowledge component correctly
        m_literal = beta_literal + gamma_literal * self.correct_responses['literal'] + rho_literal * self.incorrect_responses['literal']
        m_inferential = beta_inferential + gamma_inferential * self.correct_responses['inferential'] + rho_inferential * self.incorrect_responses['inferential']
        m_critical = beta_critical + gamma_critical * self.correct_responses['critical'] + rho_critical * self.incorrect_responses['critical']

        # Return the student's probability of answering each knowledge component correctly
        self.pred_literal = expit(m_literal)
        self.pred_inferential = expit(m_inferential)
        self.pred_critical = expit(m_critical)

        return {'literal': self.pred_literal, 'inferential': self.pred_inferential, 'critical': self.pred_critical}

    def question_choice(self):
        # Get the student's probability of answering each knowledge component correctly
        predictions = self.pfa_model()

        # Load all probabilities of correctness
        correct_pred_literal = predictions['literal']
        correct_pred_inferential = predictions['inferential']
        correct_pred_critical = predictions['critical']

        incorrect_pred_literal = 1 - correct_pred_literal
        incorrect_pred_inferential = 1 - correct_pred_inferential
        incorrect_pred_critical = 1 - correct_pred_critical

        correct_pred_average = (correct_pred_literal + correct_pred_inferential + correct_pred_critical) / 3
        incorrect_pred_average = (incorrect_pred_literal + incorrect_pred_inferential + incorrect_pred_critical) / 3

        # print(correct_pred_literal, correct_pred_inferential, correct_pred_critical)
        # print(incorrect_pred_literal, incorrect_pred_inferential, incorrect_pred_critical)
        # print(correct_pred_average, incorrect_pred_average)

        # calculate the expected value of each knowledge component
        expected_value_literal = correct_pred_literal * correct_pred_average + incorrect_pred_literal * incorrect_pred_average
        expected_value_inferential = correct_pred_inferential * correct_pred_average + incorrect_pred_inferential * incorrect_pred_average
        expected_value_critical = correct_pred_critical * correct_pred_average + incorrect_pred_critical * incorrect_pred_average

        # print(expected_value_literal, expected_value_inferential, expected_value_critical)

        if max(expected_value_literal, expected_value_inferential, expected_value_critical) == expected_value_literal:
            next_knowledge_component = 'literal'
        elif max(expected_value_literal, expected_value_inferential,
                 expected_value_critical) == expected_value_inferential:
            next_knowledge_component = 'inferential'
        else:
            next_knowledge_component = 'critical'

        # Return a question from the knowledge component with the highest expected value
        next_question_id = choice([MASTER_DATA[i] for i in range(1, len(MASTER_DATA)) if
                                   MASTER_DATA[i]["knowledge_component"] == next_knowledge_component])

        return next_question_id['id']

    
@login_required
def next_question(request):
    user = request.user
    user_answers = UserAnswer.objects.filter(user=user)
    user_history = []

    for answer in user_answers:
        user_history.append({
            'question_id': answer.question.id,
            'correct': int(answer.correct)
        })

    student_model = StudentModel(student_id=user.id, student_history=user_history)
    next_question_id = student_model.question_choice()

    return JsonResponse({'next_question_id': next_question_id})


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
    questions_count = Question.objects.count()
    answered_questions_count = answered_questions.count()

    print(f"Total questions in the database: {questions_count}")
    print(f"Answered questions by the user: {answered_questions_count}")

    # Get the next question based on the student model
    next_question_id = json.loads(next_question(request).content)['next_question_id']
    question = Question.objects.get(id=next_question_id)

    if request.method == 'POST':
        selected_choice = request.POST['selected_choice']
        user_answer = UserAnswer(user=request.user, question=question, answer=selected_choice)
        user_answer.save()

    return render(request, 'test.html', {'question': question, 'questions_count': questions_count, 'answered_questions_count': answered_questions_count})
    

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
            defaults={'answer': selected_answer_letter, 'correct': is_correct, 'submission_time': timezone.now()} # Add 'submission_time' field here
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

def user_is_authenticated(user):
    return user.is_authenticated

@user_passes_test(user_is_authenticated, login_url='/login/')
def index(request):
    return redirect('/home/')
