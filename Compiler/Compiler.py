<<<<<<< HEAD:Compiler.py
import io
import sys
import re

from Google import Create_Service
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from datasets import load_dataset
import os
import json
from tkinter import *
from tkinter import messagebox

FONT = ('Arial', 12)

# Set up Google Drive API service
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

# Check for the latest version of the dataset in Google Drive
folder_id = '1_EDy64e8ONe-JDUI0ltjFC-vfSfGqRW-'
query = f"parents = '{folder_id}'"
response = service.files().list(q=query).execute()
files = response.get('files')
next_page_token = response.get('nextPageToken')

while next_page_token:
    response = service.files().list().execute()
    files.extend(response.get('files'))
    next_page_token = response.get('nextPageToken')

files_list = []

# Compile all file version names and ids in a list
for file in files:
    if 'aicomprehend_dataset' in file['name']:
        files_list.append(
            {
                file['name'].removesuffix('.json'): file['id']
            }
        )

file_name_list = []

for file in files_list:
    file_name_list.append(list(file.keys()))

# Download the latest version of the dataset if it exists
if not files_list:
    aicomprehend_dataset = []
    latest_version_file_name = 'aicomprehend_dataset_v0'
else:
    latest_version_file = files_list[0]
    latest_version_file_name = list(latest_version_file.keys())[0]
    file_id = latest_version_file[latest_version_file_name]

    # Download the latest file
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)
    done = False

    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)

    with open(os.path.join('', latest_version_file_name + '.json'), 'wb') as f:
        f.write(fh.read())
        f.close()

    # Load the latest version of the dataset
    with open(latest_version_file_name + '.json', 'r') as current_dataset:
        aicomprehend_dataset = json.loads(current_dataset.read())

if len(aicomprehend_dataset) < 150:
    print(len(aicomprehend_dataset))
    # Loading Source Dataset
    dataset = load_dataset("race", "middle")
else:
    dataset = load_dataset("race", "high")

# Set up the UI
root = Tk()
root.title('Data Compiler')
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))

# Passage Holder
passage_holder = Canvas(width=1000, height=400, bg='black')
passage_holder.grid(row=1, column=1, columnspan=2, pady=10, sticky='NSEW')

# Passage Text
passage_text = passage_holder.create_text(20, 20, font=('Arial', 10), fill='white', anchor='nw', width=1050)

# Question Holder
question_holder = Canvas(width=1000, height=50, bg='black')
question_holder.grid(row=2, column=1, columnspan=2, pady=10, sticky='NSEW')

# Question Text
question_text = question_holder.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=800)

# Choices Holders
choice_holder_1 = Canvas(width=390, height=100, bg='black', )
choice_holder_2 = Canvas(width=390, height=100, bg='black', )
choice_holder_3 = Canvas(width=390, height=100, bg='black', )
choice_holder_4 = Canvas(width=390, height=100, bg='black', )
choice_holder_1.grid(row=3, column=1, pady=10, sticky='NSEW')
choice_holder_2.grid(row=3, column=2, pady=10, sticky='NSEW')
choice_holder_3.grid(row=4, column=1, pady=10, sticky='NSEW')
choice_holder_4.grid(row=4, column=2, pady=10, sticky='NSEW')

# Choices Text
choice_text_1 = choice_holder_1.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=350)
choice_text_2 = choice_holder_2.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=350)
choice_text_3 = choice_holder_3.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=350)
choice_text_4 = choice_holder_4.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=350)

# Component Entry
component_entry = Entry(width=50)
component_entry.grid(row=5, column=1, columnspan=1, sticky='NSW')

# Labels
passage_label = Label(text='PASSAGE')
passage_label.grid(row=1, column=0, sticky='NSEW', pady=10, padx=10)

question_label = Label(text='QUESTION')
question_label.grid(row=2, column=0, sticky='NSEW', pady=10, padx=10)

choices_label = Label(text='CHOICES')
choices_label.grid(row=3, column=0, sticky='NSEW', pady=10, padx=10)

component_label = Label(text='COMPONENT')
component_label.grid(row=5, column=0, sticky='NSEW', pady=10, padx=10)

# Upload Dataset Button
upload_dataset_button = Button(text='Upload Dataset', bg='black', fg='white', font=('Arial', 15,), padx=10)
upload_dataset_button.grid(row=5, column=2)

# Center all elements
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(4, weight=1)

if len(aicomprehend_dataset) < 150:
    current_index = len(aicomprehend_dataset)
else:
    current_index = 1
current_item = dataset['test'][current_index]


# Dataloader function for the UI
def dataloader():
    global current_item
    current_item = dataset['test'][current_index]
    if current_item['question'] not in aicomprehend_dataset.__str__():
        formatted_passage_list = current_item['article'].split('\n')
        formatted_passage = '\n\n'.join(formatted_passage_list)
        passage_holder.itemconfig(passage_text, text=formatted_passage, )
        question_holder.itemconfig(question_text, text=current_item['question'])
        choice_holder_1.itemconfig(choice_text_1, text=current_item['options'][0])
        choice_holder_2.itemconfig(choice_text_2, text=current_item['options'][1])
        choice_holder_3.itemconfig(choice_text_3, text=current_item['options'][2])
        choice_holder_4.itemconfig(choice_text_4, text=current_item['options'][3])


# Function for updating the dataset with the annotated data
def save_annotation():
    global current_index

    if component_entry.get().lower() in ['l', 'i', 'c']:

        formatted_passage_list = current_item['article'].split('\n')
        formatted_passage = '\n\n'.join(formatted_passage_list)

        if component_entry.get().lower() == 'l':
            knowledge_component = 'literal'
        elif component_entry.get().lower() == 'i':
            knowledge_component = 'inferential'
        else:
            knowledge_component = 'critical'

        data_dict = {
            'passage': formatted_passage,
            'question': current_item['question'],
            'choices': current_item['options'],
            'answer': current_item['answer'],
            'knowledge component': knowledge_component,
            'id': len(aicomprehend_dataset),
        }

        aicomprehend_dataset.append(data_dict)
        save_offline()
        current_index += 1
        dataloader()

    else:
        messagebox.showwarning('Invalid Input!', 'Please enter a valid input: L/I/C')


# Function for saving the dataset locally
def save_offline():
    version = re.findall(r'\d+', latest_version_file_name)
    version = ''.join(version)
    new_file_name = 'aicomprehend_dataset_v' + str(int(version) + 1) + '.json'
    with open(new_file_name, 'w+') as local_backup:
        try:
            aicomprehend_dataset_local_backup = [json.load(local_backup), aicomprehend_dataset]
        except json.JSONDecodeError:
            aicomprehend_dataset_local_backup = aicomprehend_dataset
        json.dump(aicomprehend_dataset_local_backup, local_backup, indent=4)


# Function for saving the dataset online to Google Drive
def save_online():
    save_offline()
    if latest_version_file_name:
        version = re.findall(r'\d+', latest_version_file_name)
        version = ''.join(version)
        new_file_name = 'aicomprehend_dataset_v' + str(int(version) + 1) + '.json'
    else:
        new_file_name = 'aicomprehend_dataset_v1.json'
    mimetypes = 'text/plain'
    file_metadata = {
        'name': new_file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(new_file_name, mimetype=mimetypes)
    service.files().create(body=file_metadata, media_body=media, fields='id', supportsAllDrives=True).execute()

    sys.exit()


# bind the save online function to the upload button
upload_dataset_button.config(command=save_online)

# main
dataloader()
root.bind('<Return>', lambda event: save_annotation())
root.mainloop()
=======
import io
from Google import Create_Service
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from datasets import load_dataset
import os
import json
from tkinter import *
from tkinter import messagebox

FONT = ('Arial', 12)

# Loading Source Dataset
dataset = load_dataset("race", "all")

# Set up Google Drive API service
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

# Check for the latest version of the dataset in Google Drive
folder_id = '1_EDy64e8ONe-JDUI0ltjFC-vfSfGqRW-'
query = f"parents = '{folder_id}'"
response = service.files().list(q=query).execute()
files = response.get('files')
next_page_token = response.get('nextPageToken')

while next_page_token:
    response = service.files().list().execute()
    files.extend(response.get('files'))
    next_page_token = response.get('nextPageToken')

files_list = []

# Compile all file version names and ids in a list
for file in files:
    if 'aicomprehend_dataset' in file['name']:
        files_list.append(
            {
                file['name'].removesuffix('.json'): file['id']
            }
        )

file_name_list = []

for file in files_list:
    file_name_list.append(list(file.keys()))

# Download the latest version of the dataset if it exists
if not files_list:
    aicomprehend_dataset = []
    latest_version_file_name = 'aicomprehend_dataset_v0'

else:
    latest_version_file = [x for x in files_list if list(x.keys())[0] == max(file_name_list)[0]]
    latest_version_file_name = max(file_name_list)[0]
    file_name = latest_version_file_name
    file_id = latest_version_file[0][file_name]

    # Download the latest file
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)
    done = False

    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)

    with open(os.path.join('', file_name + '.json'), 'wb') as f:
        f.write(fh.read())
        f.close()

    # Load the latest version of the dataset
    with open(file_name + '.json', 'r') as current_dataset:
        aicomprehend_dataset = json.loads(current_dataset.read())

# Set up the UI
root = Tk()
root.title('Data Compiler')
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))

# Passage Holder
passage_holder = Canvas(width=1000, height=400, bg='black')
passage_holder.grid(row=1, column=1, columnspan=2, pady=10, sticky='NSEW')

# Passage Text
passage_text = passage_holder.create_text(20, 20, font=('Arial', 10), fill='white', anchor='nw', width=1050)

# Question Holder
question_holder = Canvas(width=1000, height=50, bg='black')
question_holder.grid(row=2, column=1, columnspan=2, pady=10, sticky='NSEW')

# Question Text
question_text = question_holder.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=800)

# Choices Holders
choice_holder_1 = Canvas(width=390, height=100, bg='black', )
choice_holder_2 = Canvas(width=390, height=100, bg='black', )
choice_holder_3 = Canvas(width=390, height=100, bg='black', )
choice_holder_4 = Canvas(width=390, height=100, bg='black', )
choice_holder_1.grid(row=3, column=1, pady=10, sticky='NSEW')
choice_holder_2.grid(row=3, column=2, pady=10, sticky='NSEW')
choice_holder_3.grid(row=4, column=1, pady=10, sticky='NSEW')
choice_holder_4.grid(row=4, column=2, pady=10, sticky='NSEW')

# Choices Text
choice_text_1 = choice_holder_1.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=350)
choice_text_2 = choice_holder_2.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=350)
choice_text_3 = choice_holder_3.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=350)
choice_text_4 = choice_holder_4.create_text(20, 20, font=FONT, fill='white', anchor='nw', width=350)

# Component Entry
component_entry = Entry(width=50)
component_entry.grid(row=5, column=1, columnspan=1, sticky='NSW')

# Labels
passage_label = Label(text='PASSAGE')
passage_label.grid(row=1, column=0, sticky='NSEW', pady=10, padx=10)

question_label = Label(text='QUESTION')
question_label.grid(row=2, column=0, sticky='NSEW', pady=10, padx=10)

choices_label = Label(text='CHOICES')
choices_label.grid(row=3, column=0, sticky='NSEW', pady=10, padx=10)

component_label = Label(text='COMPONENT')
component_label.grid(row=5, column=0, sticky='NSEW', pady=10, padx=10)

# Upload Dataset Button
upload_dataset_button = Button(text='Upload Dataset', bg='black', fg='white', font=('Arial', 15,), padx=10)
upload_dataset_button.grid(row=5, column=2)

# Center all elements
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(4, weight=1)

current_index = len(aicomprehend_dataset)
current_item = dataset['train'][current_index]


# Dataloader function for the UI
def dataloader():
    global current_item
    current_item = dataset['train'][current_index]
    if current_item['question'] not in aicomprehend_dataset.__str__():
        formatted_passage_list = current_item['article'].split('\n')
        formatted_passage = '\n\n'.join(formatted_passage_list)
        passage_holder.itemconfig(passage_text, text=formatted_passage, )
        question_holder.itemconfig(question_text, text=current_item['question'])
        choice_holder_1.itemconfig(choice_text_1, text=current_item['options'][0])
        choice_holder_2.itemconfig(choice_text_2, text=current_item['options'][1])
        choice_holder_3.itemconfig(choice_text_3, text=current_item['options'][2])
        choice_holder_4.itemconfig(choice_text_4, text=current_item['options'][3])


# Function for updating the dataset with the annotated data
def save_annotation():
    global current_index

    if component_entry.get().lower() in ['l', 'i', 'c']:

        formatted_passage_list = current_item['article'].split('\n')
        formatted_passage = '\n\n'.join(formatted_passage_list)

        if component_entry.get().lower() == 'l':
            knowledge_component = 'literal'
        elif component_entry.get().lower() == 'i':
            knowledge_component = 'inferential'
        else:
            knowledge_component = 'critical'

        data_dict = {
            'passage': formatted_passage,
            'question': current_item['question'],
            'choices': current_item['options'],
            'answer': current_item['answer'],
            'knowledge component': knowledge_component,
            'id': len(aicomprehend_dataset),
        }

        aicomprehend_dataset.append(data_dict)
        save_offline()
        current_index += 1
        dataloader()

    else:
        messagebox.showwarning('Invalid Input!', 'Please enter a valid input: L/I/C')


# Function for saving the dataset locally
def save_offline():
    with open('aicomprehend_dataset_v' + str(int(latest_version_file_name[-1]) + 1) + '.json', 'w+') as local_backup:
        try:
            aicomprehend_dataset_local_backup = [json.load(local_backup), aicomprehend_dataset]
        except json.JSONDecodeError:
            aicomprehend_dataset_local_backup = aicomprehend_dataset
        json.dump(aicomprehend_dataset_local_backup, local_backup, indent=4)


# Function for saving the dataset online to Google Drive
def save_online():
    save_offline()
    if latest_version_file_name:
        new_file_name = 'aicomprehend_dataset_v' + str(int(latest_version_file_name[-1]) + 1) + '.json'
    else:
        new_file_name = 'aicomprehend_dataset_v1.json'
    mimetypes = 'text/plain'
    file_metadata = {
        'name': new_file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(new_file_name, mimetype=mimetypes)
    service.files().create(body=file_metadata, media_body=media, fields='id', supportsAllDrives=True).execute()


# bind the save online function to the upload button
upload_dataset_button.config(command=save_online)

# main
dataloader()
root.bind('<Return>', lambda event: save_annotation())
root.mainloop()
>>>>>>> origin/main:Compiler/Compiler.py
