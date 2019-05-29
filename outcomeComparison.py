from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
import sqlite3
import FileGen


def penn_to_wn(tag):
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag"""
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
        # print("Synset: ", wn.synsets(word, wn_tag))
        # print("Our word: ", wn.synsets(word, wn_tag)[0])
        print("Synset type: ", type(wn.synsets(word, wn_tag)[0]))
        return wn.synsets(word, wn_tag)[0]
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
    # print("Sentence type: ", type(sentence))
    print("Sentence: ", sentence)
    return sentence


def tagged_to_synset_test(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None

    try:
        # print("Synset: ", wn.synsets(word, wn_tag))
        # print("Our word: ", wn.synsets(word, wn_tag)[0])
        # print("Synset type: ", type(wn.synsets(word, wn_tag)))
        return wn.synsets(word, wn_tag)
    except:
        return None


def tokenize_sentence_test(group1):
    """
    :param group1: String to be tokenized
    :return: tokenized string
    """
    sentence = pos_tag(word_tokenize(group1))
    sentence = [tagged_to_synset_test(*tagged_word) for tagged_word in sentence]
    # print("tokenized: ", sentence)
    sentence = [ss for ss in sentence if ss]
    # print("Sentence type: ", type(sentence))
    # print("Element type: ", type(sentence[0]))
    # print("Sentence: ", sentence)
    return sentence


def compare_words_testing(sentence1, sentence2, zero_bad_matches):
    """
    :param sentence1: String - First sentence to be compared
    :param sentence2: String - Second sentence to be compared
    :param zero_bad_matches: Bool - True appends 0 for bad matches, False ignores them
    :return: Average of similarity between words
    """
    final_scores = []
    total_score = 0.0

    # print("sentence1 type: ", type(sentence1))
    # print("element type: ", type(sentence1[0]))

    for word1 in sentence1:
        word_scores = []
        for word1_syn in word1:
            # print("word1_syn: ", word1_syn)

            for word2 in sentence2:
                syn_scores = []
                for word2_syn in word2:
                    # print("word2_syn: ", word2_syn)

                    wup_score = word1_syn.wup_similarity(word2_syn)
                    if wup_score is not None:
                        syn_scores.append(wup_score)

                    if len(syn_scores) > 0:
                        word_scores.append(max(syn_scores))
                    else:
                        if zero_bad_matches:
                            word_scores.append(0)

        if len(word_scores) > 0:
            average_word_score = sum(word_scores) / len(word_scores)
            final_scores.append(average_word_score)
    if len(final_scores) > 0:
        total_score = sum(final_scores) / len(final_scores)

    return total_score


def compare_words(sentence1, sentence2, zero_bad_matches):
    """
    :param sentence1: String - First sentence to be compared
    :param sentence2: String - Second sentence to be compared
    :param zero_bad_matches: Bool - True appends 0 for bad matches, False ignores them
    :return: Average of similarity between words
    """
    final_scores = []
    total_score = 0.0

    print("sentence1 type: ", type(sentence1))
    print("element type: ", type(sentence1[0]))

    for word1 in sentence1:
        word_scores = []
        print("word1 type: ", type(word1))

        for word2 in sentence2:
            print("word2 type: ", type(word2))
            wup_score = word1.wup_similarity(word2)
            #path_score = word1.path_similarity(word2)
            # print("wup_score: ", wup_score, " Type: ", type(wup_score))
            # print("path_score: ", path_score, " Type: ", type(path_score))

            if wup_score is not None: # and path_score is not None:
                word_score = wup_score #(wup_score + path_score) / 2
                word_scores.append(word_score)
            else:
                if zero_bad_matches:
                    word_scores.append(0)

        if len(word_scores) > 0:
            average_word_score = sum(word_scores) / len(word_scores)
            final_scores.append(average_word_score)
    if len(final_scores) > 0:
        total_score = sum(final_scores) / len(final_scores)

    return total_score


def compare_outcomes(outcomes1, outcomes2):
    """
    :param outcomes1: First set of outcomes to be compared
    :param outcomes2: Second set of outcomes to be compared
    :return: Average similarity score of outcomes

    Compute similarity between outcomes using Wordnet
    Outcomes are list of strings(sentences).
    In a loop, take a single OC outcome, tokenize it.
    In another loop, take each JST outcome, tokenize it, compare it to OC outcome, until all OC outcomes are done.
    Need to think of a way to do scores properly/better.
    """

    total_score = 0.0
    outcome_scores = []
    for oc1 in outcomes1:
        sentence1 = tokenize_sentence(oc1)

        for oc2 in outcomes2:
            sentence2 = tokenize_sentence(oc2)
            sentence_score = compare_words(sentence1, sentence2, False)
            outcome_scores.append(sentence_score)

    if len(outcome_scores) > 0:
        total_score = sum(outcome_scores) / len(outcome_scores)

    return total_score


def build_comparison_dict_test(outcomes1, outcomes2):
    """
    :param outcomes1: First set of outcomes to be compared
    :param outcomes2: Second set of outcomes to be compared
    :return: Average similarity score of outcomes

    Compute similarity between outcomes using Wordnet
    Outcomes are list of strings(sentences).
    In a loop, take a single OC outcome, tokenize it.
    In another loop, take each JST outcome, tokenize it, compare it to OC outcome, until all OC outcomes are done.
    Need to think of a way to do scores properly/better.
    """

    # total_score = 0.0

    comparison_dict = {}
    for oc1 in outcomes1:
        jst_dict = {}
        jst_outcome_list = []
        jst_score_list = []

        sentence1 = tokenize_sentence_test(oc1)

        for oc2 in outcomes2:
            jst_outcome_list.append(oc2)
            sentence2 = tokenize_sentence_test(oc2)

            # print("Sentence1: ", oc1, "Type: ", type(oc1))
            # print("Sentence2: ", oc2, "Type: ", type(oc2))
            sentence_score1 = compare_words_testing(sentence1, sentence2, False)
            sentence_score2 = compare_words_testing(sentence2, sentence1, False)
            print("Comparing outcomes: ", oc1, " ", oc2)
            sentence_score = (sentence_score1 + sentence_score2) / 2
            print("Score: ", sentence_score)
            # print("Sentence1: ", sentence1)
            # print("Sentence2: ", sentence2)
            # print("Scores: ", sentence_score1, " ", sentence_score2, " ", sentence_score)

            jst_score_list.append(sentence_score)

            # outcome_score.append(sentence_score)

        # outcome_scores.append(outcome_score)
        jst_dict["outcomes"] = jst_outcome_list
        jst_dict["scores"] = jst_score_list

        comparison_dict[oc1] = jst_dict

    return comparison_dict


def build_comparison_dict(outcomes1, outcomes2):
    """
    :param outcomes1: First set of outcomes to be compared
    :param outcomes2: Second set of outcomes to be compared
    :return: Average similarity score of outcomes

    Compute similarity between outcomes using Wordnet
    Outcomes are list of strings(sentences).
    In a loop, take a single OC outcome, tokenize it.
    In another loop, take each JST outcome, tokenize it, compare it to OC outcome, until all OC outcomes are done.
    Need to think of a way to do scores properly/better.
    """

    # total_score = 0.0
    comparison_dict = {}
    for oc1 in outcomes1:
        jst_dict = {}
        jst_outcome_list = []
        jst_score_list = []
        sentence1 = tokenize_sentence(oc1)

        for oc2 in outcomes2:
            jst_outcome_list.append(oc2)
            sentence2 = tokenize_sentence(oc2)
            sentence_score1 = compare_words(sentence1, sentence2, True)
            sentence_score2 = compare_words(sentence2, sentence1, True)
            sentence_score = (sentence_score1 + sentence_score2) / 2

            jst_score_list.append(sentence_score)

            # outcome_score.append(sentence_score)

        # outcome_scores.append(outcome_score)
        jst_dict["outcomes"] = jst_outcome_list
        jst_dict["scores"] = jst_score_list

        comparison_dict[oc1] = jst_dict

    return comparison_dict


# def symmetrical_filter(outcome1, outcome2, score_threshold):
#     """
#     :param outcome1: First set of outcomes to be compared
#     :param outcome2: Second set of outcomes to be compared
#     :param score_threshold: Minimum score to allow outcome match
#     :return: Average similarity score of outcomes
#     Symmetric sentence similarity - take the average of comparing 1 to 2 and 2 to 1"
#     """
#     sym_outcome_scores = []
#     pass1 = filter_outcomes(outcome1, outcome2, score_threshold)
#     pass2 = filter_outcomes(outcome2, outcome1, score_threshold)
#
#     for i in range(len(pass1)):
#         score = pass1[i] + pass2[i] / 2
#         sym_outcome_scores.append(score)
#
#     return sym_outcome_scores


def symmetrical_compare_outcomes(outcome1, outcome2):
    """
    :param outcome1: First set of outcomes to be compared
    :param outcome2: Second set of outcomes to be compared
    :return: Average similarity score of outcomes
    Symmetric sentence similarity - take the average of comparing 1 to 2 and 2 to 1"
    """
    return (compare_outcomes(outcome1, outcome2) + compare_outcomes(outcome2, outcome1)) / 2


def compare_descriptions(class1, class2):
    """
    :param class1: First description being compared
    :param class2: Second description being compared
    :return: Similarity score of the two descriptions

    Compute similarity between descriptions using Wordnet
    Outcomes are list of sentences.
    In a loop, take a single description, tokenize it.
    In another loop, take each description, tokenize it, compare it to first description, until all descriptions are done.
    Scoring could possibly use some tweaking long-term
    """

    sentence1 = tokenize_sentence(class1)
    sentence2 = tokenize_sentence(class2)

    return compare_words(sentence1, sentence2, True)


def symmetrical_compare_descriptions(outcome1, outcome2):
    """ Symmetric sentence similarity - take the average of comparing 1 to 2 and 2 to 1"""
    return (compare_descriptions(outcome1, outcome2) + compare_descriptions(outcome2, outcome1)) / 2


def fetch_course_outcomes(institution_list, db_name):
    """
    :param institution_list: List of empty dictionaries corresponding with the possible institutions to be compared
    :param db_name: Name of database file
    :return: institution_list filled with appropriate data
    """

    conn = sqlite3.connect(db_name)
    curs = conn.cursor()

    for course in curs.execute('select distinct CourseNumber from Outcome').fetchall():
        outcome_list = []
        for outcome in curs.execute('''select OutcomeDescription from Outcome where CourseNumber=?''', course):
            outcome_string = ''.join(outcome)
            outcome_list.append(outcome_string)

        if (curs.execute('''select InstitutionID from Course where CourseNumber=?''', course).fetchone()) is not None:
            institution_check = 0
            for idCheck in curs.execute('''select InstitutionID from Course where CourseNumber=?''',
                                        course).fetchone():
                # print("ID: ", idCheck) #debug text
                institution_check = idCheck
                # print("course: ", course, " ", institution_check)

            course_string = ''.join(course)
            institution_list[institution_check - 1][course_string] = outcome_list

    return institution_list


def fetch_course_description(institution_list, db_name):
    """
    :param institution_list: List of empty dictionaries corresponding with the possible institutions to be compared
    :param db_name: Name of database file
    :return: institution_list filled with appropriate data
    """

    conn = sqlite3.connect(db_name)
    curs = conn.cursor()

    for course in curs.execute('select distinct CourseNumber from Outcome').fetchall():
        description_string = 0
        for outcome in curs.execute('''select CourseDescription from Course where CourseNumber=?''', course):
            description_string = ''.join(outcome)

        if (curs.execute('''select InstitutionID from Course where CourseNumber=?''', course).fetchone()) is not None:
            institution_check = 0
            for idCheck in curs.execute('''select InstitutionID from Course where CourseNumber=?''',
                                        course).fetchone():
                # print("ID: ", idCheck) #debug text
                institution_check = idCheck
                # print("course: ", course, " ", institution_check)

            institution_list[institution_check - 1][course] = description_string

    return institution_list


def mass_compare_outcomes(inst1, inst2):
    """
    :param inst1: List element containing a dictionary containing a course (key) and outcomes (value)
    :param inst2: List element containing a dictionary containing a course (key) and outcomes (value)
    :return: List of lists that serves as a matrix of outcome comparisons for all courses
    """
    table = []
    for course1, outcomes1 in inst1.items():
        sim_list = []
        for course2, outcomes2 in inst2.items():
            course_similarity = symmetrical_compare_outcomes(outcomes1, outcomes2)
            sim_list.append(course_similarity)
        table.append(sim_list)
    return table


def scrub(table_name):
    # These functions format the 'create' statement programmatically
    return ''.join(chr for chr in table_name if chr.isalnum())


def create_create_statement(table_name, columns):
    """
    :param table_name: name of table to be created
    :param columns: list of column names
    :return: string create statement
    """
    return f"create table {scrub(table_name)} ({columns[0]}" + (
            ",{} "*(len(columns)-1)).format(*map(scrub, columns[1:])) + ")"


def mass_compare_descriptions(inst1, inst2):
    """
    :param inst1: List element containing a dictionary containing a course (key) and outcomes (value)
    :param inst2: List element containing a dictionary containing a course (key) and outcomes (value)
    :return: List of lists that serves as a matrix of outcome comparisons for all courses
    """
    table = []
    for course1, desc1 in inst1.items():
        sim_list = []
        for course2, desc2 in inst2.items():
            # compare descriptions of each course in inst1 to each course in inst2, one at a time
            course_similarity = symmetrical_compare_descriptions(desc1, desc2)
            sim_list.append(course_similarity)
        table.append(sim_list)
    return table


def build_comparison_table(comp_table, db_name, table_name, course_and_desc_list):
    """
    :param comp_table: list of lists - comparison table of % similarity between outcomes or descriptions
    :param db_name: database name
    :param table_name: table name
    :param course_and_desc_list: dictionary of courses and their outcomes or descriptions
    :return:
    """
    col_names = ["OC_Courses"]

    comp_conn = sqlite3.connect(db_name)
    comp_curs = comp_conn.cursor()

    for name, description in course_and_desc_list[2].items():
        name_string = ''.join(name)
        col_names.append(name_string)

    drop_statement = "drop table if exists " + table_name
    create_statement = create_create_statement(table_name, col_names)
    comp_curs.execute(drop_statement)
    comp_curs.execute(create_statement)

    insert_statement = "insert into " + table_name + " values (?,"
    for i in range(len(comp_table[0])):
        insert_statement += "?"
        if i == len(comp_table[0]) - 1:
            insert_statement += ")"
        else:
            insert_statement += ","

    course_list = []
    for k, v in course_and_desc_list[0].items():
        course_list.append(''.join(k))

    for i in range(len(comp_table)):
        row = [course_list[i]]
        for j in range(len(comp_table[i])):
            row.append(comp_table[i][j])
        comp_curs.execute(insert_statement, row)
        comp_conn.commit()


# Need instructor name, department, military course, and oc course


oc_course_num = 'PE 107'
oc_course_title = 'First Aid'
oc_course = oc_course_num + ' ' + oc_course_title

jst_course_num = 'NV-2201-0128'
jst_course_title = 'Expiditionary Combat Skills'
jst_course = jst_course_num + ' ' + jst_course_title

instructor = 'Nick Juday'
department = 'HHP'

course_and_outcome_list = [{}, {}, {}]
database_name = 'mce.sqlite3'

course_and_outcome_list = fetch_course_outcomes(course_and_outcome_list, database_name)

# test_file = FileGen.FileGen(instructor, department, jst_course, oc_course)


'''
single_oc_outcome = ['Identify the major body systems to provide appropriate care']
single_jst_outcome = ['casualty care']

single_oc_outcome2 = ['Identify ways to prevent injury and / or illness']
single_jst_outcome2 = ['basic first aid']

two_oc_outcomes = ['Identify ways to prevent injury and / or illness.',
                   'Identify the major body systems to provide appropriate care.']
two_jst_outcomes = ['basic first aid', 'casualty care']

oc3 = ['Identify ways to prevent injury and / or illness.',
       'Identify the major body systems to provide appropriate care.',
       'Follow the emergency action steps in any emergency.'
       ]
jst3 = ['basic first aid', 'casualty care', 'military communication']
'''

oc_course_outcomes = course_and_outcome_list[0].get(oc_course_num)
jst_course_outcomes = course_and_outcome_list[2].get(jst_course_num)


'''
oc_outcome_list = [
    'Follow the emergency action steps in any emergency.',
    'Identify the major body systems to provide appropriate care.',
    'Identify ways to prevent injury and / or illness.',
    'Provide basic care for an injury and / or sudden illness until the victim can receive professional medical help, including CPR skills for the adult, child and infant.',
    'Recognize when an emergency has occurred and activate the EMS system.'
]

jst_outcome_list = [
    'Basic first aid',
    'land navigation',
    'military navigation',
    'military communication',
    'firearm safety',
    'Demonstrate knowledge of combat mind set',
    'Chemical, biological, radiological and nuclear training.',
    'Exercising judgment-based engagement training',
    'Identify and safely handle counter improvised explosive devices',
    'Perform basic movements while engaging targets',
    'accomplish high risk security operations',
    'casualty care',
    'pulse check and blood sweep',
    'control bleeding',
    'airway management',
    'nasopharyngeal breathing',
    'bandaging and splints',
    'head and spine treatment',
    'burns, environmental injuries',
    'vehicle emergency egress drills',
    'disease prevention',
    'field sanitation',
    'fractures',
    'infection control',
    'nuclear, biological, and chemical agents',
    'tactical combat casualty care.'
]


# print(build_comparison_dict_test(single_oc_outcome2, single_jst_outcome2))
# This yields ~45%
print("oc3 type: ", type(oc3), " oc_course_outcomes type: ", type(oc_course_outcomes))
print("-------------------------------------------------------------------------------------------")
print("oc3: ", oc3)
print("oc_course_outcomes: ", oc_course_outcomes)
print("-------------------------------------------------------------------------------------------")
print(build_comparison_dict_test(two_oc_outcomes, two_jst_outcomes))
print("-------------------------------------------------------------------------------------------")
print(build_comparison_dict_test(single_oc_outcome, single_jst_outcome))
print("-------------------------------------------------------------------------------------------")
print(build_comparison_dict_test(oc3, jst3))
print("-------------------------------------------------------------------------------------------")
print(build_comparison_dict_test(oc_course_outcomes, jst_course_outcomes))
print("-------------------------------------------------------------------------------------------")
print(build_comparison_dict_test(oc_outcome_list, jst_outcome_list))
print("-------------------------------------------------------------------------------------------")

# for item1 in oc_course_outcomes:
#     for item2 in jst_course_outcomes:
#         print(item1)
#         print(item2)
#         print(build_comparison_dict_test(item1, item2))

# print(build_comparison_dict_test(oc_course_outcomes, jst_course_outcomes))
# This yields ~31% for the same outcome

# print(build_comparison_dict_test(single_oc_outcome2[0], single_jst_outcome2[0]))
# 0.4174227136614015

# print(build_comparison_dict_test(single_oc_outcome2, single_jst_outcome2))

# print(build_comparison_dict_test(oc_course_outcomes, jst_course_outcomes))







# single_oc_outcome = 'Identify ways to prevent injury and / or illness'
# single_jst_outcome = 'basic first aid'
#
# single_oc_outcome = tokenize_sentence(single_oc_outcome)
# single_jst_outcome = tokenize_sentence(single_jst_outcome)
#
# print("OC type: ", type(single_oc_outcome))
# print("OC: ", single_oc_outcome)
# print("OC[0] type: ", type(single_oc_outcome[0]))
# print("OC[0] :", single_oc_outcome[0])
# print("------------------------------------------------------------")

# print(single_oc_outcome)
# print(single_jst_outcome)
# print(compare_words(single_oc_outcome, single_jst_outcome, False))
# 0.3232142857142857

'''




# test_file = FileGen.FileGen(instructor, department, jst_course, oc_course)
#
#
# with open("test5.txt", 'w') as myfile:
#     myfile.write("wup with synonyms\nNot zeroing bad matches")
#     for oc, jst in oc_vs_jst.items():
#         # test_file.Like_Outcomes(oc, jst["outcomes"])
#         myfile.write("---------------------------------------------------------------------\n")
#         myfile.write("OC Outcome: ")
#         myfile.write(oc)
#         myfile.write("\n")
#         for i in range(len(jst["outcomes"])):
#             myfile.write("JST Outcome: ")
#             myfile.write(jst["outcomes"][i])
#             myfile.write("\n")
#             myfile.write("Score: ")
#             myfile.write(str(jst["scores"][i]))
#             myfile.write("\n")
#
# test_file.Save_Doc()


# for item in oc_course_outcomes:
#     print(item)
#
# print("---------")
#
# for item in jst_course_outcomes:
#     print(item)

# print(course_and_outcome_list[0])
# print(course_and_outcome_list[2])

