import json
import os
import sys

# Add your Django project to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

import django
django.setup()

from mysite.models import Question

# Replace this with the path to your JSON file
json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Compiler', 'aicomprehend_dataset_v9.json')

with open(json_file_path, 'r') as f:
    data = json.load(f)

for item in data:
    mymodel_instance = Question(
        passage=item['passage'],
        question_text=item['question'],
        choices=item['choices'],
        answer=item['answer'],
        knowledge_component=item['knowledge component'],
        id=item['id']
    )
    mymodel_instance.save()
