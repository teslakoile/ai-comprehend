from tkinter import *
import json
from pprint import pprint
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import io
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
folder_id = '1_EDy64e8ONe-JDUI0ltjFC-vfSfGqRW-'

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

root = Tk()
root.title("Q/A Compiler")
# Center the window

root.config(width=900, height=600, background="#263D42")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (900 / 2)
y = (screen_height / 2) - (600 / 2)
root.geometry('%dx%d+%d+%d' % (900, 600, x, y))

# Create a title label
title = Label(text="Q/A Compiler", font="Courier 40 bold", fg="#e8e4c9", bg="#263D42")
title.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="NEW")

# Create a passage/question/choices/answer label
passage_label = Label(text="Passage/Question/Choices/Answer", font="Courier 20 bold", fg="#e8e4c9", bg="#263D42")
passage_label.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="NEW")

# Create a passage/question/choices/answer text box
passage_text = Text(root, width=50, height=10, font="Courier 20 bold", bg="#e8e4c9", fg="#263D42")
passage_text.grid(row=2, column=0, columnspan=4, padx=10, pady=(5, 30), sticky="NEW")


def submit():
    text = passage_text.get("1.0", "end-1c")
    passage = text.split("\n")[0]
    question = text.split("\n")[2].replace("Question: ", "")
    choices = text.split("\n")[4:8]
    for choice in choices:
        index = choices.index(choice)
        choice = choice[3:]
        choices[index] = choice
    answer = text.split("\n")[9]
    answer = answer[11:]

    if os.path.exists('DATA.json'):
        with open("DATA.json") as f:
            big_data = json.load(f)

    else:
        file_name = 'DATA.json'
        response = service.files().list(q=f"'{folder_id}' in parents").execute()
        data_files = response.get('files', [])
        request = service.files().get_media(fileId=data_files[0]['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

        fh.seek(0)
        with open(file_name, 'wb') as f:
            f.write(fh.read())
            f.close()
        with open("DATA.json") as f:
            big_data = json.load(f)
    if passage not in big_data.__str__():
        data = {
            "passage": {
                "text": passage,
                "questions": [
                    {
                        "question": question,
                        "choices": choices,
                        "answer": answer
                    }
                ]
            },
            "id": len(big_data)
        }
        with open("DATA.json", "w") as f:
            big_data.append(data)
            json.dump(big_data, f, indent=4, separators=(',', ': '))
            pprint(big_data)
    else:
        passage_index_in_string: object = big_data.__str__().index(passage)
        id_index = big_data.__str__()[passage_index_in_string:].find("id")
        passage_index = int(
            big_data.__str__()[passage_index_in_string + id_index + 5:passage_index_in_string + id_index + 6])
        big_data[passage_index]["passage"]["questions"].append({
            "question": question,
            "choices": choices,
            "answer": answer
        })
        with open("DATA.json", "w") as f:
            json.dump(big_data, f, indent=4, separators=(',', ': '))

# Create an add QA button
add_qa_button = Button(root, text="Add QA", font="Courier 20 bold", fg="#e8e4c9", bg="#263D42", command=submit)
add_qa_button.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="NEW")


def upload():
    file_name = 'DATA.json'
    mimetypes = 'text/plain'
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    response = service.files().list(q=f"'{folder_id}' in parents").execute()
    files = response.get('files', [])
    for file in files:
        try:
            service.files().delete(fileId=file['id']).execute()
        except HttpError:
            pass
    media = MediaFileUpload(file_name, mimetype=mimetypes)
    service.files().create(body=file_metadata, media_body=media, fields='id', supportsAllDrives=True).execute()


# Create an Upload data button
upload_data_button = Button(root, text="Upload Data", font="Courier 20 bold", fg="#e8e4c9", bg="#263D42",
                            command=upload)
upload_data_button.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky="NEW")

# Center all the grid elements
for i in range(4):
    root.grid_columnconfigure(i, weight=1)
for i in range(5):
    root.grid_rowconfigure(i, weight=1)

root.mainloop()
