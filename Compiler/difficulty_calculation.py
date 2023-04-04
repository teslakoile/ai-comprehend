import spacy
import pandas as pd
import json

nlp = spacy.load("en_core_web_lg")
common_words = pd.read_csv('coca.csv')
common_words_list = (common_words['lemma'][:2999]).str.lower().to_list()
common_words_list = ' '.join(common_words_list)
common_words_list = [x.text for x in nlp(common_words_list)]


with open("aicomprehend_dataset_v26_cleaned.json", 'r') as f:
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


def normalize_score(score, max_score, min_score):
    return (score - min_score) / (max_score - min_score) * (10 - min_score) + min_score


def calculate_question_complexity(passage, question, question_type, choices, correct_answer, scaling=0.2):

    passage_doc = nlp(passage)
    question_doc = nlp(question)

    passage_entities = list(passage_doc.ents)
    question_entities = list(question_doc.ents)

    passage_noun_chunks = list(passage_doc.noun_chunks)
    question_noun_chunks = list(question_doc.noun_chunks)

    shared_entities = len(set(passage_entities).intersection(question_entities))
    shared_noun_chunks = len(set(passage_noun_chunks).intersection(question_noun_chunks))

    passage_similarity = question_doc.similarity(passage_doc)
    correct_answer_doc = nlp(correct_answer)
    correct_answer_similarity = correct_answer_doc.similarity(passage_doc)
    choices_similarity = 0
    for choice in choices:
        choice_doc = nlp(choice)
        choices_similarity += choice_doc.similarity(passage_doc)
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


annotated_dataset = []

for data in dataset_for_annotation:
    passage = data['passage']
    question = data['question']
    question_type = data['knowledge component']
    choices = data['choices']
    correct_answer = data['answer']
    dc_score, difficulty_score = calculate_question_complexity(passage, question, question_type, choices, correct_answer)
    annotated_dataset.append({'passage': passage, 'question': question, 'knowledge component': question_type, 'choices': choices,
                              'answer': correct_answer, 'dc_score': dc_score, 'difficulty_score': difficulty_score})

with open('annotated_dataset.json', 'w') as f:
    json.dump(annotated_dataset, f, indent=4)

