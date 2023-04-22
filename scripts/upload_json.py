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
json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mysite', 'Compiler', 'aicomprehend_annotated_dataset_v7.json')

with open(json_file_path, 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data)} items from JSON file")

success_count = 0
error_count = 0

for item in data:
    try:
        mymodel_instance = Question()
        mymodel_instance.passage = item['passage']
        mymodel_instance.question_text = item['question']
        mymodel_instance.choices = item['choices']
        mymodel_instance.answer = item['answer']
        mymodel_instance.knowledge_component = item['knowledge_component']
        mymodel_instance.id = item['id']
        mymodel_instance.relevant_sentences = item['relevant_sentences']
        mymodel_instance.choices_in_complete_thought = item['choices_in_complete_thought']
        mymodel_instance.dc_score = item['dc_score']
        mymodel_instance.difficulty_score = item['difficulty_score']
        mymodel_instance.save()
        success_count += 1

    except KeyError as e:
        error_count += 1
        print(f"KeyError: {e} in item with id: {item['id']}")

print(f"Successfully added {success_count} items, encountered errors in {error_count} items")