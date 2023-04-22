import spacy
import pandas as pd
import json

# Load NLP model (spacy)
nlp = spacy.load("en_core_web_lg")

# Load COCA dataset
common_words = pd.read_csv('coca.csv')
common_words_list = (common_words['lemma'][:2999]).str.lower().to_list()
common_words_list = ' '.join(common_words_list)
common_words_list = [x.text for x in nlp(common_words_list)]

# Load labelled dataset
with open("aicomprehend_annotated_dataset_v6.json", 'r') as f:
    dataset_for_annotation = json.loads(f.read())


# Break the text into sentences
def break_sentences(text):
    doc = nlp(text)
    return list(doc.sents)


# Counts for the Number of Words in the text
def word_count(text):
    sentences = break_sentences(text)
    words = 0
    for sentence in sentences:
        words += len([token for token in sentence if token.is_alpha])
    return words


# Counts the number of sentences in the text
def sentence_count(text):
    sentences = break_sentences(text)
    return len(sentences)


# Computes the word/sentence ratio
def avg_sentence_length(text):
    words = word_count(text)
    sentences = sentence_count(text)
    average_sentence_length = float(words / sentences)
    return average_sentence_length


# Counts the number of uncommon words in the text
def difficult_words(text):
    words = []
    sentences = break_sentences(text)
    for sentence in sentences:
        words += [token.lower_ for token in sentence if token.is_alpha]
    # difficult words are those with syllables >= 2
    # easy_word_set is provide by Textstat as
    # a list of common words
    diff_words_set = []

    for word in words:
        if word not in common_words_list:
            diff_words_set.append(word)

    return len(diff_words_set)


# Computes for the modified Dale Chall Readability Score
def dale_chall_readability_score(text):

    words = word_count(text)

    raw_score = (0.1579 * difficult_words(text)/words * 100) + \
                (0.0496 * avg_sentence_length(text))

    # If Percentage of Difficult Words is greater than 5 %, then;
    # Adjusted Score = Raw Score + 3.6365,
    # otherwise Adjusted Score = Raw Score

    if difficult_words(text)/words > 0.05:
        raw_score += 3.6365

    return raw_score


# Normalize score
def normalize_score(score, max_score, min_score):
    return (score - min_score) / (max_score - min_score) * (10 - min_score) + min_score


# Calculate question complexity
def calculate_question_complexity(passage, question, question_type, choices, correct_answer, relevant_sentences, choices_in_complete_thought, scaling=0.2):

    passage_doc = nlp(passage)
    question_doc = nlp(question)

    passage_entities = list(passage_doc.ents)
    question_entities = list(question_doc.ents)

    passage_noun_chunks = list(passage_doc.noun_chunks)
    question_noun_chunks = list(question_doc.noun_chunks)

    shared_entities = len(set(passage_entities).intersection(question_entities))
    shared_noun_chunks = len(set(passage_noun_chunks).intersection(question_noun_chunks))

    relevant_sentences_str = " ".join(relevant_sentences)
    relevant_sentences_doc = nlp(relevant_sentences_str)
    choices_in_complete_thought = [nlp(sentence) for sentence in choices_in_complete_thought]

    passage_similarity = question_doc.similarity(relevant_sentences_doc)

    if correct_answer == 'A':
        correct_answer = choices_in_complete_thought[0]
    elif correct_answer == 'B':
        correct_answer = choices_in_complete_thought[1]
    elif correct_answer == 'C':
        correct_answer = choices_in_complete_thought[2]
    elif correct_answer == 'D':
        correct_answer = choices_in_complete_thought[3]

    correct_answer_doc = correct_answer
    correct_answer_similarity = correct_answer_doc.similarity(relevant_sentences_doc)
    choices_similarity = 0
    for choice in choices_in_complete_thought:
        choices_similarity += choice.similarity(passage_doc)
    choices_similarity /= len(choices)

    dc_score = dale_chall_readability_score(passage)

    max_theoretical_similarity = 1
    min_theoretical_choices_similarity = 0

    max_ids = (max_theoretical_similarity + max_theoretical_similarity - min_theoretical_choices_similarity) * 10
    raw_complexity = (passage_similarity + correct_answer_similarity - choices_similarity) * 10
    normalized_complexity = normalize_score(raw_complexity, max_ids, 0)

    if question_type == 'inferential':
        ids = (shared_entities + shared_noun_chunks) * 10 / len(list(passage_doc.sents))
        inferential_difficulty_score = dc_score + ids + normalized_complexity * scaling
        if inferential_difficulty_score < dc_score:
            inferential_difficulty_score = dc_score
        return dc_score, inferential_difficulty_score
    elif question_type == 'critical':
        cds = (shared_entities + shared_noun_chunks) * 2
        critical_difficulty_score = dc_score + cds + normalized_complexity * scaling
        if critical_difficulty_score < dc_score + normalized_complexity * scaling:
            critical_difficulty_score = dc_score + normalized_complexity * scaling
        return dc_score, critical_difficulty_score
    else:
        return dc_score, dc_score


# Create an empty list to store the annotated dataset
annotated_dataset = []

# Annotate the dataset
for data in dataset_for_annotation:
    id = data['id']
    passage = data['passage']
    question = data['question']
    question_type = data['knowledge component']
    choices = data['choices']
    correct_answer = data['answer']
    relevant_sentences = data['relevant_sentences']
    choices_in_complete_thought = data['choices_in_complete_thought']

    dc_score, difficulty_score = calculate_question_complexity(passage, question, question_type, choices, correct_answer, relevant_sentences, choices_in_complete_thought)
    annotated_dataset.append({'id': id, 'passage': passage, 'question': question, 'knowledge_component': question_type, 'choices': choices, 'answer': correct_answer, 'relevant_sentences': relevant_sentences, 'choices_in_complete_thought': choices_in_complete_thought, 'dc_score': dc_score, 'difficulty_score': difficulty_score})

# Dump the dataset to a json file
with open('aicomprehend_annotated_dataset_v7.json', 'w') as f:
    json.dump(annotated_dataset, f, indent=4)

