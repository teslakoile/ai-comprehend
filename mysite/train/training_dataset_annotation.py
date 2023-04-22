import numpy as np
import pandas as pd
import os
import json

csv_file = "combined_data.csv"
# Phase 1 Compilation
# Set the path to the directory containing the Excel files
excel_dir = "Encoded"

# Create an empty list to hold the dataframes
df_list = []
filenames_list = []

# Load pretest json file
with open('pretest_dataset_v4.json') as f:
    pretest_dataset = json.load(f)

# Compile individual data into a single dataframe and annotate with necessary labels
for filename in os.listdir(excel_dir):
    if filename.endswith(".xlsx"):
        df = pd.read_excel(os.path.join(excel_dir, filename))
        df.rename(columns={df.columns[0]: 'Question ID', 'Unnamed: 1': 'Response'}, inplace=True)

        # shift question id and response down by 1
        df['Question ID'] = df['Question ID'].shift(-1)
        df['Response'] = df['Response'].shift(-1)

        # delete last row
        df.drop(df.tail(1).index, inplace=True)

        # convert question id to int
        df['Question ID'] = df['Question ID'].astype(int) - 1

        # Add knowledge component, difficulty score, and answer labels
        df['Knowledge Component'] = df['Question ID'].apply(lambda x: pretest_dataset[x]['knowledge_component'])
        df['Difficulty'] = df['Question ID'].apply(lambda x: pretest_dataset[x]['difficulty_score'])
        df['Answer'] = df['Question ID'].apply(lambda x: pretest_dataset[x]['answer'])

        # Add student id and answer status labels
        df['Student ID'] = len(df_list)
        df['Status'] = (df['Response'] == df['Answer']) * 1

        # Create a new column named 'Knowledge Components' and initialize it with a list of zeros
        df['Knowledge Components'] = [0] * len(df)
        # Replace the zeros with the appropriate knowledge component
        df['Knowledge Components'] = df['Knowledge Components'].apply(lambda x: [0, 0, 0]).astype('object')
        df['Knowledge Components'] = np.where(df['Knowledge Component'] == 'literal', df['Knowledge Components'].apply(lambda x: [1, 0, 0]), df['Knowledge Components'])
        df['Knowledge Components'] = np.where(df['Knowledge Component'] == 'inferential', df['Knowledge Components'].apply(lambda x: [0, 1, 0]), df['Knowledge Components'])
        df['Knowledge Components'] = np.where(df['Knowledge Component'] == 'critical', df['Knowledge Components'].apply(lambda x: [0, 0, 1]), df['Knowledge Components'])
        # initialize number correct and incorrect columns
        df['literal_number_correct'] = 0
        df['literal_number_incorrect'] = 0
        df['inferential_number_correct'] = 0
        df['inferential_number_incorrect'] = 0
        df['critical_number_correct'] = 0
        df['critical_number_incorrect'] = 0
        # fill in number correct and incorrect columns
        for i in range(1, len(df)):
            previous_response = df.iloc[i - 1]
            if previous_response['Knowledge Components'][0] == 1:
                if previous_response['Status'] == 1:
                    df.at[i, 'literal_number_correct'] = previous_response['literal_number_correct'] + 1
                    df.at[i, 'literal_number_incorrect'] = previous_response['literal_number_incorrect']
                else:
                    df.at[i, 'literal_number_correct'] = previous_response['literal_number_correct']
                    df.at[i, 'literal_number_incorrect'] = previous_response['literal_number_incorrect'] + 1
            if previous_response['Knowledge Components'][1] == 1:
                if previous_response['Status'] == 1:
                    df.at[i, 'inferential_number_correct'] = previous_response['inferential_number_correct'] + 1
                    df.at[i, 'inferential_number_incorrect'] = previous_response['inferential_number_incorrect']
                else:
                    df.at[i, 'inferential_number_correct'] = previous_response['inferential_number_correct']
                    df.at[i, 'inferential_number_incorrect'] = previous_response['inferential_number_incorrect'] + 1
            if previous_response['Knowledge Components'][2] == 1:
                if previous_response['Status'] == 1:
                    df.at[i, 'critical_number_correct'] = previous_response['critical_number_correct'] + 1
                    df.at[i, 'critical_number_incorrect'] = previous_response['critical_number_incorrect']
                else:
                    df.at[i, 'critical_number_correct'] = previous_response['critical_number_correct']
                    df.at[i, 'critical_number_incorrect'] = previous_response['critical_number_incorrect'] + 1

        # Add the dataframe to the list
        df_list.append(df)

# Concatenate all the dataframes into one
df = pd.concat(df_list)

# Rearrange columns
df = df[['Student ID', 'Question ID', 'Knowledge Component', 'Knowledge Components', 'Difficulty', 'Response',
         'Answer', 'Status', 'literal_number_correct', 'literal_number_incorrect', 'inferential_number_correct',
         'inferential_number_incorrect', 'critical_number_correct', 'critical_number_incorrect']]

# Write the combined dataframe to a CSV file
df.to_csv('training_dataset.csv', index=False)
