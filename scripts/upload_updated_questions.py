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
json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mysite', 'Compiler', 'aicomprehend_annotated_dataset_v9.json')

with open(json_file_path, 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data)} items from JSON file")

success_count = 0
error_count = 0

for index, item in enumerate(data):
    try:
        mymodel_instance, created = Question.objects.update_or_create(
            id=item['id'],
            defaults={
                'passage': item['passage'],
                'question_text': item['question'],
                'choices': item['choices'],
                'answer': item['answer'],
                'knowledge_component': item['knowledge_component'],
                'relevant_sentences': item['relevant_sentences'],
                'choices_in_complete_thought': item['choices_in_complete_thought'],
                'dc_score': item['dc_score'],
                'difficulty_score': item['difficulty_score'],
                'explanation': item['explanation'],
            }
        )
        success_count += 1
        print(f"Updated item {index + 1}/{len(data)}")

    except KeyError as e:
        error_count += 1
        print(f"KeyError: {e} in item with id: {item['id']}")

print(f"Successfully added/updated {success_count} items, encountered errors in {error_count} items")

