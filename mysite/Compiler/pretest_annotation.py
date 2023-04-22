import json
from datasets import load_dataset
import difficulty_calculation as dc

# Phase 1
# # Load the dataset
# master_dataset = load_dataset('race', 'all')
#
# passages_id_list = ['high24149.txt', 'high10134.txt', 'middle2177.txt', 'high11886.txt',
#                     'high19643.txt', 'high20162.txt', 'middle5573.txt', 'high8556.txt']
#
# pretest_dataset = master_dataset.filter(lambda example: example['example_id'] in passages_id_list)
#
# # Create a dictionary with the pretest dataset
# pretest_list = []
# for item in pretest_dataset['test']:
#     pretest_list.append(
#         {
#             'passage': item['article'],
#             'question': item['question'],
#             'choices': item['options'],
#             'answer': item['answer'],
#             'id': len(pretest_list)
#         }
#     )
#
# # Save the dictionary to a json file
# with open('pretest_dataset.json', 'w+') as pretest_file:
#     json.dump(pretest_list, pretest_file, indent=4)


# Phase 2
# pretest_index_in_order = [0, 1, 2, 3, 4, 17, 16, 18, 6, 7, 5, 14, 15, 11, 12, 13, 22, 23, 9, 8]
#
# # Load the pretest dataset
# with open('pretest_dataset.json', 'r') as pretest_file:
#     pretest_dataset = json.load(pretest_file)
#
# # Create a dictionary with the pretest dataset in the order of the pretest
# pretest_list = []
# for index in pretest_index_in_order:
#     pretest_list.append(pretest_dataset[index])
#
# # Change the id of the items in the pretest dataset
# for index, item in enumerate(pretest_list):
#     item['id'] = index
#
# # Save the dictionary to a json file
# with open('pretest_dataset_v2.json', 'w+') as pretest_file:
#     json.dump(pretest_list, pretest_file, indent=4)

# Phase 3
# # Load domain dataset
# with open('aicomprehend_annotated_dataset_v7.json', 'r') as domain_file:
#     domain_dataset = json.load(domain_file)
#
# # Load pretest dataset
# with open('pretest_dataset_v2.json', 'r') as pretest_file:
#     pretest_dataset = json.load(pretest_file)
#
# new_pretest_dataset = []
# # Match the pretest dataset with the domain dataset
# for item in pretest_dataset:
#     for domain_item in domain_dataset:
#         if item['choices'][0] == domain_item['choices'][0]:
#             new_pretest_dataset.append(domain_item)
#             new_pretest_dataset[-1]['id'] = len(new_pretest_dataset) - 1
#
#     if item['choices'][1].__str__() not in new_pretest_dataset.__str__():
#         new_pretest_dataset.append(item)
#         new_pretest_dataset[-1]['id'] = item['id']
#
# # Save the dictionary to a json file
# with open('pretest_dataset_v3.json', 'w+') as pretest_file:
#     json.dump(new_pretest_dataset, pretest_file, indent=4)

# Phase 4 Manual annotation for non-annotated items
# Load pretest dataset
with open('pretest_dataset_v3.json', 'r') as pretest_file:
    pretest_dataset = json.load(pretest_file)

for item in pretest_dataset:
    if "knowledge_component" not in item.keys():
        print(item['passage'])
        print(item['question'])
        print(item['choices'])
        print(item['answer'])
        print(item['id'])
        knowledge_component = str(input("Knowledge component: "))
        item['knowledge_component'] = knowledge_component

    if "relevant_sentences" not in item.keys():
        print(item['passage'])
        print(item['question'])
        print(item['choices'])
        print(item['answer'])
        print(item['id'])
        relevant_sentences = []
        relevant_sentence = str(input("Relevant sentences: "))
        relevant_sentences.append(relevant_sentence)
        while relevant_sentence != "stop":
            relevant_sentence = str(input("Relevant sentences: "))
            relevant_sentences.append(relevant_sentence)
        choices_in_complete_thought = []
        for i in range(4):
            choice_in_complete_thought = str(input("Choice in complete thought: "))
            choices_in_complete_thought.append(choice_in_complete_thought)

        item['relevant_sentences'] = relevant_sentences
        item['choices_in_complete_thought'] = choices_in_complete_thought
        dc_score, difficulty_score = dc.calculate_question_complexity(passage=item['passage'],
                                                                      question=item['question'],
                                                                      choices=item['choices'],
                                                                      correct_answer=item['answer'],
                                                                      relevant_sentences=item['relevant_sentences'],
                                                                      choices_in_complete_thought=item['choices_in_complete_thought'],
                                                                      question_type=item['knowledge_component'])
        item['dc_score'] = dc_score
        item['difficulty_score'] = difficulty_score

# Save the dictionary to a json file
with open('pretest_dataset_v4.json', 'w+') as pretest_file:
    json.dump(pretest_dataset, pretest_file, indent=4)
