import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.optimize import minimize
from imblearn.over_sampling import RandomOverSampler

# Load the dataset
data = pd.read_csv('training_dataset.csv')

# Split the dataset into train, test and validation
train_data, test_data = np.split(data.sample(frac=1), [int(.8 * len(data))])

# Oversample the train data to balance the number of correct and incorrect responses
ros = RandomOverSampler()
train_data, train_labels = ros.fit_resample(train_data, train_data['Knowledge Component'])


def loglik(params, data):
    ll = 0
    beta, gamma, rho = params
    for index, datapoint in data.iterrows():
        if type(datapoint) == str:
            continue
        actual_response = datapoint['Status']
        s_literal = datapoint['literal_number_correct']
        f_literal = datapoint['literal_number_incorrect']
        s_inferential = datapoint['inferential_number_correct']
        f_inferential = datapoint['inferential_number_incorrect']
        s_critical = datapoint['critical_number_correct']
        f_critical = datapoint['critical_number_incorrect']
        if datapoint['Knowledge Component'] == 'literal':
            m = beta + gamma * s_literal + rho * f_literal
        elif datapoint['Knowledge Component'] == 'inferential':
            m = beta + gamma * s_inferential + rho * f_inferential
        elif datapoint['Knowledge Component'] == 'critical':
            m = beta + gamma * s_critical + rho * f_critical

        pred = expit(m)

        ll += np.log(pred) if actual_response == 1 else np.log(1 - pred)

    return -ll


# Optimize the beta gamma and rho parameters for each knowledge component using the train data
bounds = ((-10, 0), (0, 10), (-10, 10))
# Literal parameters
literal_data = train_data[train_data['Knowledge Component'] == 'literal']
literal_optimal_parameters = minimize(loglik, [0, 0, 0], args=(literal_data), method='L-BFGS-B', bounds=bounds)
beta_literal, gamma_literal, rho_literal = literal_optimal_parameters.x
print(literal_optimal_parameters.x)

# Inferential parameters
inferential_data = train_data[train_data['Knowledge Component'] == 'inferential']
inferential_optimal_parameters = minimize(loglik, [0, 0, 0], args=(inferential_data), method='L-BFGS-B', bounds=bounds)
beta_inferential, gamma_inferential, rho_inferential = inferential_optimal_parameters.x
print(inferential_optimal_parameters.x)

# Critical parameters
critical_data = train_data[train_data['Knowledge Component'] == 'critical']
critical_optimal_parameters = minimize(loglik, [0, 0, 0], args=(critical_data), method='L-BFGS-B', bounds=bounds)
beta_critical, gamma_critical, rho_critical = critical_optimal_parameters.x
print(critical_optimal_parameters.x)


# With the optimized parameters, calculate the precision of the model using the validation data
def precision1(params, data):
    correct = 0
    beta_literal, gamma_literal, rho_literal, beta_inferential, gamma_inferential, rho_inferential, beta_critical, gamma_critical, rho_critical = params
    for index, datapoint in data.iterrows():
        if type(datapoint) == str:
            continue
        actual_response = datapoint['Status']
        s_literal = datapoint['literal_number_correct']
        f_literal = datapoint['literal_number_incorrect']
        s_inferential = datapoint['inferential_number_correct']
        f_inferential = datapoint['inferential_number_incorrect']
        s_critical = datapoint['critical_number_correct']
        f_critical = datapoint['critical_number_incorrect']
        if datapoint['Knowledge Component'] == 'literal':
            m = beta_literal + gamma_literal * s_literal + rho_literal * f_literal
        elif datapoint['Knowledge Component'] == 'inferential':
            m = beta_inferential + gamma_inferential * s_inferential + rho_inferential * f_inferential
        elif datapoint['Knowledge Component'] == 'critical':
            m = beta_critical + gamma_critical * s_critical + rho_critical * f_critical

        pred = expit(m)

        if pred >= 0.50 and actual_response == 1:
            correct += 1
        elif pred < 0.50 and actual_response == 0:
            correct += 1

    return correct / len(data)


# Calculate the precision of the model using the test data
optimal_parameters = [-0.21511034, 0.48704398, -1.03234507, -0.62694264, 0.39838356, 0.01086545, -1.35502912, 0.014411, 0.13719109]
print(precision1(optimal_parameters, test_data))

# Save the parameters to a file
with open('parameters.txt', 'w') as f:
    f.write(str(optimal_parameters))

