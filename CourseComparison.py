from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
# from nltk.corpus import wordnet_ic
# import sqlite3
import FileGen2
from Course import Course
from Reviewer import Reviewer


def penn_to_wn(tag):
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag"""
    # if tag.startswith('N'):
    #     return wn.NOUN
    # if tag.startswith('V'):
    #     return wn.VERB
    # if tag.startswith('J'):
    #     return wn.ADJ
    # if tag.startswith('R'):
    #     return wn.ADV

    if tag.startswith('N'):
        return 'n'
    if tag.startswith('V'):
        return 'v'
    if tag.startswith('J'):
        return 'a'
    if tag.startswith('R'):
        return 'r'
    return None


def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None
    try:
        return wn.synsets(word, wn_tag)  # [0]
    except:
        return None


def tokenize_sentence(group1):
    """
    :param group1: String to be tokenized
    :return: tokenized string
    """
    sentence = pos_tag(word_tokenize(group1))
    sentence = [tagged_to_synset(*tagged_word) for tagged_word in sentence]
    sentence = [ss for ss in sentence if ss]
    return sentence


def compare_words(sentence1, sentence2):
    """
    :param sentence1: String - First sentence to be compared
    :param sentence2: String - Second sentence to be compared
    :return: Average of similarity between words
    """

    final_scores = []
    total_score = 0.0

    for synset1 in sentence1:
        word_scores = []
        set1 = set(synset1)

        for synset2 in sentence2:
            set2 = set(synset2)

            # wup_score = None
            # # wup_score = len(set1.intersection(set2)) / len(set1.union(set2))
            # lemma1, pos1, synset_index_str1 = str(synset1).lower().rsplit('.', 2)
            # lemma2, pos2, synset_index_str2 = str(synset2).lower().rsplit('.', 2)
            # # print("synset1: ", synset1)
            # # print("synset2: ", synset2)
            # # print("pos1: ", pos1)
            # # print("pos2: ", pos2)
            # if pos1 == pos2 and pos1 != 'a' and pos1 != 'r':
            #     # res_similarity seemed bad, doesn't seem to be a standardized score
            #     wup_score = synset1.jcn_similarity(synset2, semcor_ic)
            #     print("Score: ", wup_score)

            # Partial synonym check approach - attempt 3

            if len(set1.intersection(set2)) > 0:
                # print("Match found: ")
                # print(synset1, " and ", synset2)
                # print("wup_sim: ", synset1[0].wup_similarity(synset2[0]))
                wup_score = 1
            else:
                syn_scores = []
                for syn in synset2:
                    syn_score1 = synset1[0].wup_similarity(syn)
                    syn_score2 = syn.wup_similarity(synset1[0])
                    if syn_score1 is not None and syn_score2 is not None:
                        syn_score = (syn_score1 + syn_score2) / 2
                        syn_scores.append(syn_score)
                if len(syn_scores) > 0:
                    wup_score = max(syn_scores)
                else:
                    wup_score = None

            if wup_score is not None:
                word_scores.append(wup_score)

        if len(word_scores) > 0:
            final_scores.append(max(word_scores))

    if len(final_scores) > 0:
        total_score = sum(final_scores) / len(final_scores)

    return total_score


def compare_descriptions(class1, class2):
    """
    :param class1: First description being compared
    :param class2: Second description being compared
    :param zero_bad_matches: If true, will allow for bad matches to be 0'd out, resulting in lower
    but technically more accurate results
    :return: Similarity score of the two descriptions
    Compute similarity between descriptions using Wordnet
    """

    sentence1 = tokenize_sentence(class1)
    sentence2 = tokenize_sentence(class2)

    symmetrical_score = (compare_words(sentence1, sentence2) +
                         compare_words(sentence2, sentence1)) / 2

    score = float('{:.3f}'.format(symmetrical_score * 100))
    return score


def compare_courses(course1, course2, reviewer):
    # conn = sqlite3.connect(db)
    # curs = conn.cursor()
    # c1sql = 'select OutcomeDescription from Outcome where CourseNumber="' + course1 + '"'
    # c2sql = 'select OutcomeDescription from Outcome where CourseNumber="' + course2 + '"'
    # c1otc = list(map(lambda x: x[0], curs.execute(c1sql).fetchall()))
    # c2otc = list(map(lambda x: x[0], curs.execute(c2sql).fetchall()))

    comparison_dict = {}

    for outcome1 in course1.outcomes:
        comp_list = []
        for outcome2 in course2.outcomes:
            outcomes_and_score = []
            outcome_score = compare_descriptions(outcome1, outcome2)
            outcomes_and_score.append(outcome2)
            outcomes_and_score.append(outcome_score)
            comp_list.append(outcomes_and_score)

        comp_list.sort(key=lambda x: x[1], reverse=True)
        comparison_dict[outcome1] = comp_list

    file_gen = FileGen2.FileGen(course1, course2, reviewer)

    for oc, jst in comparison_dict.items():
        file_gen.Like_Outcomes(oc, jst)

    file_name = './files/EvalForms/' + course1.number + '_' + course2.number + '_Eval_Form.docx'
    file_gen.Save_Doc(file_name)


database = 'mce.sqlite3'

# course_pairs = [['CJ 220', 'A-830-0030'], ['IRM 340', 'NV-1710-0118'], ['JMC 105', 'AR-2201-0603'],
#                 ['MTH 120', 'NV-1710-0118'], ['SCI 107', 'AR-1601-0277'], ['PE 107', 'A-830-0030']]
course_pairs = [['PE 107', 'A-830-0030', 'Nick Juday']]

for pair in course_pairs:
    OC_Course = Course(database, pair[0])
    JST_Course = Course(database, pair[1])
    Reviewer = Reviewer(database, pair[2])
    compare_courses(OC_Course, JST_Course, Reviewer)
