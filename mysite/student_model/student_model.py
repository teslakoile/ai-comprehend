import json
from scipy.special import expit
from random import choice

with open('EEE-196/train/parameters.txt') as file:
    DEFAULT_PARAMETERS = file.read().replace('[', '').replace(']', '').replace('\n', ', ').replace(' ', '').split(',')
    DEFAULT_PARAMETERS = [float(i) for i in DEFAULT_PARAMETERS]

with open('EEE-196/Compiler/aicomprehend_annotated_dataset_v7.json') as file:
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
