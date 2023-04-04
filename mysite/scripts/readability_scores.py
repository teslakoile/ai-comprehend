import spacy
import re
import textstat

def normalize_score(score, max_score, min_score):
    return (score - min_score) / (max_score - min_score) * (10 - min_score) + min_score

def calculate_question_complexity(passage, question, question_type, choices, correct_answer, scaling=0.2):
    nlp = spacy.load("en_core_web_md")
    
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
    
    dc_score = textstat.dale_chall_readability_score(passage)
    
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


# Example usage
passage = """Little Tommy was doing very badly in math. His parents had tried everything--tutors, cards, special learning centers--
in short, everything they could think of. Finally they took Tommy to a catholic school. After the first day, little Tommy came home
with a very serious look on his face. He didn't kiss his mother hello. Instead, he went straight to his room and started studying.
Books and papers were spread out all over the room and little Tommy was hard at work. His mother was surprised. She called him down
to dinner and as soon as he finished eating, he went back to his room, without a word. In no time he was back hitting the books
as hard as before. This went on for some time, day after day while the mother tried to understand what was happening. Finally,
little Tommy brought home his report card. He quietly put it on the table and went up to his room and hit the books. His mom
looked at it and to her surprise, little Tommy got an A in math. She could no longer hold her curiosity. She went to his
room and asked, "Son, what was it? Was it the nuns ? " Little Tommy looked at her and shook his head, "No. " "Well then,"
she asked again. "WHAT was it? " Little Tommy looked at her and said, "Well, on the first day of school, when I saw that
man nailed to the plus sign , I knew they weren't joking. 
"""
question = "The last sentence in the passage shows that _ ."
question_type = "inferential"
choices = ["Tommy felt sorry for the man",
            "Tommy was afraid of being nailed",
            "Tommy didn't like the plus sign",
            "Tommy liked playing jokes on others"]
correct_answer = "Tommy was afraid of being nailed"

literal_difficulty_score, inferential_difficulty_score = calculate_question_complexity(passage, question, question_type, choices, correct_answer)
print("Literal Difficulty Score:", literal_difficulty_score)
print("Inferential Difficulty Score:", inferential_difficulty_score)

question = "From the passage, we can deduce that _ ."
question_type = "critical"
choices = ["teachers should be strict with their students",
            "mistakes might do good sometimes",
            "a catholic school is much better than other ones",
            "nuns are good at helping children with their math"]
correct_answer = "mistakes might do good sometimes"

literal_difficulty_score, critical_difficulty_score = calculate_question_complexity(passage, question, question_type, choices, correct_answer)
print("Literal Difficulty Score:", literal_difficulty_score)
print("Critical Difficulty Score:", critical_difficulty_score)


# Example usage
passage = """Many people hate wet, sticky August, but to some, it's an especially bitter time. A new working paper finds that,
 March and August are the months in which divorce filings peak. For the paper, the University of Washington's Brian Serafini and
Julie Brines analyzed the most recent years of divorce filings in Washington and drew their conclusion: divorce rises sharply in 
March and August. The result is supported by some nation-wide, anecdotal evidence. Online searches for "divorce" and "child custody"
dramatically grow early in the year, peaking in March, they point out. The authors guess that unhappily married couples schedule 
their divorce filings around both the winter holidays and Valentine's Day, as well as summer vacations. (More Americans vacation
m July than any other month.) There are a few explanations why people might time their marital dissolutions this way, It might 
just be too difficult to announce a divorce around family-oriented Christmas time, especially if there are kids involved, so many
couples weigh the decision to divorce around the new year and progress from there. February is a period in which couples tend
to look around for representation on legal sites. And by March, they're prepared to file for divorce. But the authors think
the more likely reason is that people decide their differences are irreconcilable right after a big trip. It could be that
people don't want to ruin a family getaway, or that vacations are so stressful that they drive the already-dissatisfied
to divorce. ("I told you to pack your suitcase last night; now we've missed the train!") Then there's the "broken promise"
theory. "6People are discontent with their marriages, they look at vacation as an opportunity to give it one last shot,
and what they were hoping would happen didn't occur," explained Brines, an associate professor of sociology. It's not
you; in other words, it's your failure to print the boarding passes.
"""
question = "According to Brian and Julie, why does divorce rise in March and August?"
question_type = "inferential"
choices = ["People need time to decide and prepare before they divorce",
            "Many couples want to have a new beginning in a new year",
            "Kids are less involved in winter and summer vacations",
            "Couples see more marital problems in their vacation trips"]
correct_answer = "Couples see more marital problems in their vacation trips"

literal_difficulty_score, inferential_difficulty_score = calculate_question_complexity(passage, question, question_type, choices, correct_answer)
print("Literal Difficulty Score:", literal_difficulty_score)
print("Inferential Difficulty Score:", inferential_difficulty_score)

question = "Which of the following can support Brian and Julie's conclusion?"
question_type = "critical"
choices = ["The divorce rate rises sharply in March and August",
            "They carried out online surveys and analyzed the results",
            "More people search for key words about divorce early in the year",
            "Conflicts in marriage tend to get more serious during Christmas"]
correct_answer = "mistakes might do good sometimes"

literal_difficulty_score, critical_difficulty_score = calculate_question_complexity(passage, question, question_type, choices, correct_answer)
print("Literal Difficulty Score:", literal_difficulty_score)
print("Critical Difficulty Score:", critical_difficulty_score)