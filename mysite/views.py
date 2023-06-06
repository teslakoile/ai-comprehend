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
from django.core.exceptions import ValidationError

import json
from random import choice
from scipy.special import expit
from sklearn.utils import shuffle
from random import sample, shuffle
from statistics import mean
import numpy as np
import pandas as pd
import pickle
from .models import UserProfile

DEFAULT_PARAMETERS = (-0.06760512, 0.1, -0.01688316, -0.21032119, 0.00128378, -0.02590103, -0.30148615, 0.03580852, -0.0356914)

with open('mysite/Compiler/aicomprehend_annotated_dataset_v7.json') as file:
    MASTER_DATA = json.load(file)

class StudentModel:
    def __init__(self, student_id, student_history, student_parameters=DEFAULT_PARAMETERS, remaining_question_ids=None, diagnostic_test_ids=None,
                mastered_components=None, inappropriate_components=None, model=None, in_diagnostic=False, in_review=False):

        self.student_id = student_id
        self.student_history = student_history
        self.recent_history = student_history[-30:]
        self.remaining_question_ids = remaining_question_ids
        self.diagnostic_test_ids = diagnostic_test_ids
        self.mastered_components = mastered_components
        self.inappropriate_components = inappropriate_components
        self.in_diagnostic = in_diagnostic
        self.in_review = in_review
        self.student_parameters = DEFAULT_PARAMETERS

        if self.student_id % 2 == 0:
            self.model = '1'
        else:
            self.model = '2'

        # # get knowledge component of last 30 questions using student_history and MASTER_DATA
        # self.recent_history = [MASTER_DATA[i['question_id']]['knowledge_component'] for i in self.recent_history]

        # get correct/incorrect of last 30 questions using student_history
        print("self.student_history: ", self.student_history)
        print("self.recent_history: ", self.recent_history)
        self.correct_responses = {
            'literal': [i['correct'] for i in self.recent_history if MASTER_DATA[i['question_id']]['knowledge_component'] == 'literal'].count(True),
            'inferential': [i['correct'] for i in self.recent_history if MASTER_DATA[i['question_id']]['knowledge_component'] == 'inferential'].count(True),
            'critical': [i['correct'] for i in self.recent_history if MASTER_DATA[i['question_id']]['knowledge_component'] == 'critical'].count(True)}

        self.incorrect_responses = {
            'literal': [i['correct'] for i in self.recent_history if MASTER_DATA[i['question_id']]['knowledge_component'] == 'literal'].count(False),
            'inferential': [i['correct'] for i in self.recent_history if MASTER_DATA[i['question_id']]['knowledge_component'] == 'inferential'].count(False),
            'critical': [i['correct'] for i in self.recent_history if MASTER_DATA[i['question_id']]['knowledge_component'] == 'critical'].count(False)}
        self.correct_responses['literal'] += self.correct_responses['inferential'] + self.correct_responses['critical']
        self.correct_responses['inferential'] += self.correct_responses['critical']
        self.incorrect_responses['literal'] += self.incorrect_responses['inferential'] + self.incorrect_responses['critical']
        self.incorrect_responses['inferential'] += self.incorrect_responses['critical']
        self.student_parameters = student_parameters

        print("diag test ids: ", diagnostic_test_ids)

        if len(diagnostic_test_ids) == 0:
            # add 3 unique questions from each knowledge component
            self.diagnostic_ids = []
            try:
                self.diagnostic_ids.extend(sample([i['id'] for i in MASTER_DATA if i['knowledge_component'] == 'literal'], 3))
            except ValueError:
                print("Not enough 'literal' items in MASTER_DATA")
            try:
                self.diagnostic_ids.extend(sample([i['id'] for i in MASTER_DATA if i['knowledge_component'] == 'inferential'], 3))
            except ValueError:
                print("Not enough 'inferential' items in MASTER_DATA")
            try:
                self.diagnostic_ids.extend(sample([i['id'] for i in MASTER_DATA if i['knowledge_component'] == 'critical'], 3))
            except ValueError:
                print("Not enough 'critical' items in MASTER_DATA")

            self.remaining_question_ids = [i['id'] for i in MASTER_DATA if i['id'] not in self.diagnostic_ids]
        else:
            self.diagnostic_ids = diagnostic_test_ids

        if mastered_components is None:
            self.mastered_components = []
        else:
            self.mastered_components = mastered_components
        if inappropriate_components is None:
            self.inappropriate_components = []
        else:
            self.inappropriate_components = inappropriate_components

        # if model is None:
        #     self.model = self.model_chooser()
        # else:
        #     self.model = model

        self.in_review = in_review
        self.in_diagnostic = in_diagnostic

    def model_chooser(self):
        # if student_id is odd, use model 1, if even, use model 2
        if self.student_id % 2 == 0:
            return '1'
        else:
            return '2'

    def pfa_model(self):

        self.student_parameters = DEFAULT_PARAMETERS

        beta_literal, gamma_literal, rho_literal, beta_inferential, gamma_inferential, rho_inferential, beta_critical, \
            gamma_critical, rho_critical = self.student_parameters

        m_literal = beta_literal + gamma_literal * self.correct_responses['literal'] + rho_literal * \
                    self.incorrect_responses['literal']
        m_inferential = beta_inferential + gamma_inferential * self.correct_responses['inferential'] + rho_inferential * \
                        self.incorrect_responses['inferential']
        m_critical = beta_critical + gamma_critical * self.correct_responses['critical'] + rho_critical * \
                     self.incorrect_responses['critical']

        p_literal = expit(m_literal)
        p_inferential = expit(m_inferential + m_literal)
        p_critical = expit(m_critical + m_inferential + m_literal)

        prediction = {'literal': np.clip(p_literal, 0.01, 0.99), 'inferential': np.clip(p_inferential, 0.01, 0.99),
                      'critical': np.clip(p_critical, 0.01, 0.99)}

        self.mastered_components = [i for i in prediction if
                                    (prediction[i] > 0.8 and i not in self.mastered_components) or i in self.mastered_components]
        self.inappropriate_components = [i for i in prediction if
                                         (prediction[i] < 0.2 and i != 'literal' or i in self.inappropriate_components) and i not in self.mastered_components]

        return prediction

    def log_res_vanilla(self):
        with open('mysite/log_res.pkl', 'rb') as model_file:
            log_res = pickle.load(model_file)

        data = pd.DataFrame(columns=['kc_literal', 'kc_inferential', 'kc_critical',
                             'kc_literal_success', 'kc_inferential_success', 'kc_critical_success',
                             'kc_literal_failure', 'kc_inferential_failure', 'kc_critical_failure'])

        data.loc[0] = [0, 0, 0, self.correct_responses['literal'], self.correct_responses['inferential'],
                        self.correct_responses['critical'], self.incorrect_responses['literal'],
                        self.incorrect_responses['inferential'], self.incorrect_responses['critical']]

        literal_data = inferential_data = critical_data = data.copy()
        literal_data['kc_literal'] = 1
        literal_data['kc_inferential'] = literal_data['kc_critical'] = 0

        inferential_data['kc_literal'] = inferential_data['kc_inferential'] = 1
        inferential_data['kc_critical'] = 0

        critical_data['kc_literal'] = critical_data['kc_inferential'] = critical_data['kc_critical'] = 1

        prediction = {'literal': np.clip(log_res.predict_proba(literal_data)[0][1], 0.01, 0.99),
                      'inferential': np.clip(log_res.predict_proba(inferential_data)[0][1], 0.01, 0.99),
                      'critical': np.clip(log_res.predict_proba(critical_data)[0][1], 0.01, 0.99)}

        self.mastered_components = [i for i in prediction if
                                    (prediction[i] > 0.8 and i not in self.mastered_components) or i in self.mastered_components]
        self.inappropriate_components = [i for i in prediction if
                                         (prediction[i] < 0.2 and i != 'literal' or i in self.inappropriate_components) and i not in self.mastered_components]

        return prediction
    

    def model_response(self):

        if len(self.recent_history) == 0:
            self.in_diagnostic = True

        if self.model == '1':
            prediction = self.pfa_model()
        elif self.model == '2':
            prediction = self.log_res_vanilla()

        if len(self.mastered_components) == 3:
            self.in_diagnostic = True

        if self.in_diagnostic and len(self.recent_history) == 9:
            self.in_diagnostic = False
            next_question_id = self.diagnostic_ids[len(self.recent_history - 1)]
            shuffle(self.diagnostic_ids)
        elif self.in_diagnostic and len([i for i in self.student_history if i['question_id'] in self.diagnostic_ids]) == 18:
            self.in_diagnostic = False
            self.in_review = True
            self.remaining_question_ids = [i['id'] for i in MASTER_DATA]
            next_question_id = self.remaining_question_ids.pop(choice(self.remaining_question_ids))
        elif self.in_diagnostic and len(self.mastered_components) == 3:
            next_question_id = self.diagnostic_ids[[i for i in self.student_history[9:] if i['question_id'] in self.diagnostic_ids]]
        elif self.in_diagnostic:
            print("self.diagnostic_ids: ", self.diagnostic_ids)
            print("self.recent_history: ", self.recent_history)
            next_question_id = self.diagnostic_ids[len(self.recent_history)]
        elif self.in_review:
            next_question_id = self.remaining_question_ids.pop(choice(self.remaining_question_ids))
        else:
            expectation = {}
            for i in prediction:
                expectation[i] = prediction[i] * mean(prediction.values()) + (1 - prediction[i]) * (
                        1 - mean(prediction.values()))

            # remove mastered components and inappropriate components from expectation
            if len(set(self.inappropriate_components) - set(self.mastered_components)):
                expectation = {i: expectation[i] for i in expectation if i not in self.mastered_components and i not in self.inappropriate_components}
            else:
                expectation = {i: expectation[i] for i in expectation if i not in self.mastered_components}

            next_question_kc = max(expectation, key=expectation.get)

            # get a random question id from the remaining questions ids
            next_question_id = choice(
                [i for i in self.remaining_question_ids if MASTER_DATA[i]['knowledge_component'] == next_question_kc])
            self.remaining_question_ids.remove(next_question_id)

        print("Student ID: {}".format(self.student_id))
        print("Student History: {}".format(self.student_history))
        print("Recent History: {}".format(self.recent_history))
        print("Correct Responses: {}".format(self.correct_responses))
        print("Incorrect Responses: {}".format(self.incorrect_responses))
        print("Mastered Components: {}".format(self.mastered_components))
        print("Inappropriate Components: {}".format(self.inappropriate_components))
        print("In Review: {}".format(self.in_review))
        print("In Diagnostic: {}".format(self.in_diagnostic))
        print("Model: {}".format(self.model))

        return next_question_id, self.student_parameters, self.remaining_question_ids, self.diagnostic_ids, self.mastered_components,\
               self.inappropriate_components, self.model, self.in_diagnostic, self.in_review
    
@login_required
def next_question(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    if not user_profile.history:  # if history is empty, generate it from UserAnswer
        user_answers = UserAnswer.objects.filter(user=user)
        # user_history = []
        # for answer in user_answers:
        #     user_history.append({
        #         'correct': int(answer.correct),
        #         'question_id': answer.question.id
        #     })
        user_profile.history = user_history
        print("user_profile.history: ", user_profile.history)
        print("saving history")
        try:
            user_profile.save()
            print("user_profile saved in next question")
        except ValidationError as e:
            print("user_profile not saved in next question")
            
    else:  # if history exists, load it from UserProfile
        user_history = user_profile.history

    if len(user_history):
        student_model = StudentModel(student_id=user.id, student_history=user_history)
    else:
        student_model = StudentModel(student_id=user.id, student_history=user_history,
                                     remaining_question_ids=user_profile.remaining_questions_ids,
                                     diagnostic_test_ids=user_profile.diagnostic_test_ids,
                                     mastered_components=user_profile.mastered_components,
                                     inappropriate_components=user_profile.inappropriate_components,
                                     model=user_profile.model,
                                     in_diagnostic=user_profile.in_diagnostic, in_review=user_profile.in_review)
        
    next_question_id = student_model.model_response()[0]
    print("next question id")
    print(next_question_id)

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
            user_profile = UserProfile(user=user)
            user_profile.save()
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

    # Get user profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Instantiate StudentModel with data from user_profile and answered_questions
    student_model = StudentModel(
        user.id, 
        user_profile.history, 
        user_profile.remaining_question_ids,
        user_profile.diagnostic_test_ids,
        user_profile.mastered_components,
        user_profile.inappropriate_components,
        user_profile.model,
        user_profile.in_diagnostic,
        user_profile.in_review
    )

    # Get the next question based on the student model
    model_response = student_model.model_response()
    next_question_id = model_response[0]
    remaining_question_ids = model_response[2]
    diagnostic_ids = model_response[3]
    mastered_components = model_response[4]
    inappropriate_components = model_response[5]
    model = model_response[6]
    in_diagnostic = model_response[7]
    in_review = model_response[8]
    
    question = Question.objects.get(id=next_question_id)

    choices = json.dumps(question.choices)
    relevant_sentences = json.dumps(question.relevant_sentences)

    if request.method == 'POST':
        selected_choice = request.POST['selected_choice']
        user_answer = UserAnswer(user=request.user, question=question, answer=selected_choice)
        user_answer.save()

    # Update fields
    user_profile.in_diagnostic = in_diagnostic
    user_profile.in_review = in_review
    user_profile.model = model
    user_profile.mastered_components = mastered_components
    user_profile.inappropriate_components = inappropriate_components
    user_profile.diagnostic_test_ids = diagnostic_ids
    user_profile.remaining_question_ids = remaining_question_ids

    history = user_profile.history

    print("printing user_profile")
    try:
        user_profile.save()
        print("user_profile saved")
    except ValidationError as e:
        print("user_profile not saved")

    return render(request, 'test.html', {
        'question': question, 
        'choices': choices,
        'relevant_sentences': relevant_sentences,
        'questions_count': questions_count, 
        'answered_questions_count': answered_questions_count,
        'history': history
    })
    

def success(request):
    return render(request, 'success.html')


def update_user_answer(request):
    print("Request method: ", request.method)
    print("X-Requested-With header: ", request.headers.get('X-Requested-With'))
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_id = request.user.id
        question_id = request.POST.get('question_id')
        selected_answer = request.POST.get('selected_answer')

        # Validate POST data
        if not question_id or not selected_answer:
            print("Missing required data")
            return JsonResponse({'error': 'Missing required data'}, status=400)

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
        print(user_id, question_id, selected_answer_letter, is_correct, timezone.now())
        user_answer, created = UserAnswer.objects.update_or_create(
            user_id=user_id, question_id=question_id,
            defaults={'answer': selected_answer_letter, 'correct': is_correct, 'submission_time': timezone.now()} # Add 'submission_time' field here
        )
        #print number of questions the user has answered
        print(UserAnswer.objects.filter(user=request.user).count())
        user_answer.save()
        
        # Check if created or updated
        if created:
            print("UserAnswer created")
        else:
            print("UserAnswer updated")

        user_profile = UserProfile.objects.get(user=request.user)

        # Update fields
        if not any(item['question_id'] == int(question_id) for item in user_profile.history):
            # Update fields
            user_profile.history.append({
                'question_id': int(question_id),
                'correct': int(is_correct)
            })
            user_profile.save()
        

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