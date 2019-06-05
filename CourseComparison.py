from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
import sqlite3
import FileGen2


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
        # print("Synset type: ", type(wn.synsets(word, wn_tag)[0]))
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
    # print("sentence: ", sentence)
    return sentence


# initial compare_words function
# def compare_words2(sentence1, sentence2):
#     """
#     :param sentence1: String - First sentence to be compared
#     :param sentence2: String - Second sentence to be compared
#     :return: Average of similarity between words
#     """
#     final_scores = []
#     total_score = 0.0
#
#     for word1 in sentence1:
#         word_scores = []
#
#         for word2 in sentence2:
#             wup_score = word1.wup_similarity(word2)
#             if wup_score is not None:
#                 word_scores.append(wup_score)
#
#         if len(word_scores) > 0:
#             final_scores.append(max(word_scores))
#
#     if len(final_scores) > 0:
#         total_score = sum(final_scores) / len(final_scores)
#
#     return total_score


def compare_words(sentence1, sentence2):
    """
    :param sentence1: String - First sentence to be compared
    :param sentence2: String - Second sentence to be compared
    :return: Average of similarity between words
    """
    brown_ic = wordnet_ic.ic('ic-brown.dat')  # can't use adjectives or adverbs
    semcor_ic = wordnet_ic.ic('ic-semcor.dat')


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
                print("Match found: ")
                print(synset1, " and ", synset2)
                print("wup_sim: ", synset1[0].wup_similarity(synset2[0]))
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

        # if len(word_scores) > 0:
        #     final_scores.append(max(word_scores))
        # else:
        #     if zero_bad_matches:
        #         word_scores.append(0)

    if len(final_scores) > 0:
        total_score = sum(final_scores) / len(final_scores)

    return total_score


def compare_descriptions(class1, class2, zero_bad_matches):
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
    # print("sentence1: ", class1)
    # print("sentence2: ", class2)
    # print(score)
    return score


def fetch_course_descriptions(institution_list, db_name):
    """
    :param institution_list: List of empty dictionaries corresponding with the possible institutions to be compared
    :param db_name: Name of database file
    :return: institution_list filled with appropriate data
    """

    conn = sqlite3.connect(db_name)
    curs = conn.cursor()

    for course in curs.execute('select distinct CourseNumber from Outcome').fetchall():
        description_string = ''

        for desc in curs.execute('''select CourseDescription from Course where CourseNumber=?''', course):
            # print('len: ', len(''.join(desc)))
            description_string = ''.join(desc)
            # print('len: ', len(description_string), 'desc: ', description_string)

        if len(description_string) > 0:
            if (curs.execute('''select InstitutionID from Course where CourseNumber=?''', course).fetchone()) is not None:
                institution_check = 0
                for idCheck in curs.execute('''select InstitutionID from Course where CourseNumber=?''',
                                            course).fetchone():
                    # print("ID: ", idCheck) #debug text
                    # print("Course: ", course, " Institution ID: ", idCheck)
                    institution_check = idCheck
                    # print("course: ", course, " ", institution_check)

                course_string = ''.join(course)
                institution_list[institution_check - 1][course_string] = description_string

    return institution_list


def create_create_statement(table, columns):
    statement = 'create table ' + table + '('
    for i in range(0, len(columns)):
        statement += columns[i]
        if i == len(columns) - 1:
            statement += ')'
        else:
            statement += ','
    return statement


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
            course_similarity = compare_descriptions(desc1, desc2, False)
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
        name = name.replace('-', '_')
        col_names.append(name)

    print("col_names: ", col_names)

    drop_statement = "drop table if exists " + table_name
    create_statement = create_create_statement(table_name, col_names)
    print("create_statement: ", create_statement)
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


def comparison_list(db_name, comp_table, jst_course):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    curs = conn.cursor()
    formatted_name = jst_course.replace('-', '_')
    sql_statement = 'select ' + formatted_name + ', OC_Courses from ' + comp_table
    curs.execute(sql_statement)
    result = [dict(row) for row in curs.fetchall()]
    # print(result)
    sorted_result = sorted(result, key=lambda k: k[formatted_name], reverse=True)
    return sorted_result


def output_comparisons(jst_course, comp_dict_list, db_name, filepath):
    conn = sqlite3.connect(db_name)
    curs = conn.cursor()

    jst_course_name = curs.execute('select CourseName from Course where CourseNumber = ?', (jst_course,)).fetchone()
    jst_course_name = ''.join(jst_course_name)

    filename = jst_course + ' ' + jst_course_name
    headline = 'Comparing ' + jst_course_name + '(' + jst_course + ')' ' to OC Courses\n\n'
    formatted_jst = jst_course.replace('-', '_')

    tuple_list = curs.execute('select CourseEquivalenceNonOC from Course where CourseNumber = ?',
                              (jst_course,)).fetchall()
    equiv_list = [' '.join(item) for item in tuple_list]
    print(equiv_list)

    filepath = filepath + filename

    with open(filepath, 'w') as myfile:
        myfile.write(headline)
        myfile.write('Course Number\tScore\tEquiv.\tCourse Name\n\n')
        for dict_item in comp_dict_list:
            # sql_statement = 'select CourseName from Course where CourseNumber = ' + str(dict_item['OC_Courses'])
            # print(sql_statement)
            course = dict_item['OC_Courses']
            course_name = curs.execute('select CourseName from Course where CourseNumber = ?', (course,)).fetchone()

            myfile.write(dict_item['OC_Courses'])

            myfile.write('\t\t')
            myfile.write(str(dict_item[formatted_jst]))
            myfile.write('\t')
            for i in range(0, len(equiv_list)):
                if dict_item['OC_Courses'] == equiv_list[i]:
                    myfile.write('YES')

            myfile.write('\t')
            myfile.write(''.join(course_name))
            myfile.write('\n')


def grab_form_data(dbname, jst_num, oc_num):
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()

    select1 = 'select ReviewerID from Course where CourseNumber="' + oc_num + '"'
    if curs.execute(select1).fetchone() is not None:
        rev_id = ''.join(map(str, curs.execute(select1).fetchone()))
    else:
        print("No ReviewerID found")
        return

    # select2 = 'select ReviewerName from Reviewer where ReviewerID=' + rev_id
    # rev_name = ''.join(curs.execute(select2).fetchone())
    #
    # select3 = 'select ReviewerDepartment from Reviewer where ReviewerID=' + rev_id
    # rev_dept = ''.join(curs.execute(select3).fetchone())

    rev_name = ''.join(curs.execute('select ReviewerName from Reviewer where ReviewerID=?', (rev_id,)).fetchone())
    rev_dept = ''.join(curs.execute('select ReviewerDepartment from Reviewer where ReviewerID=?', (rev_id,)).fetchone())
    oc_name = ''.join(curs.execute('select CourseName from Course where CourseNumber=?', (oc_num,)).fetchone())
    jst_name = ''.join(curs.execute('select CourseName from Course where CourseNumber=?', (jst_num,)).fetchone())
    oc_desc = ''.join(curs.execute('select CourseDescription from Course where CourseNumber=?', (oc_num,)).fetchone())
    jst_desc = ''.join(curs.execute('select CourseDescription from Course where CourseNumber=?', (jst_num,)).fetchone())

    data_list = [rev_name, rev_dept, jst_num, oc_num, oc_name, jst_name, oc_desc, jst_desc]
    return data_list


def copy_table(db1, db2, tb):
    conn = sqlite3.connect(db1)
    conn.row_factory = sqlite3.Row
    curs = conn.cursor()
    drop_statement = 'drop table if exists ' + tb
    curs.execute(drop_statement)
    attach_statement = 'attach database "' + db2 + '" as db2'
    curs.execute(attach_statement)
    row_statement = 'select * from db2.' + tb
    row = curs.execute(row_statement).fetchone()
    columns = row.keys()
    print(columns)
    create_statement = create_create_statement(tb, columns)
    print(create_statement)
    curs.execute(create_statement)
    insert_statement = 'insert into ' + tb + ' select * from db2.' + tb
    curs.execute(insert_statement)
    conn.commit()


def compare_courses(course1, course2, db):
    conn = sqlite3.connect(db)
    curs = conn.cursor()
    c1sql = 'select OutcomeDescription from Outcome where CourseNumber="' + course1 + '"'
    c2sql = 'select OutcomeDescription from Outcome where CourseNumber="' + course2 + '"'
    c1otc = list(map(lambda x: x[0], curs.execute(c1sql).fetchall()))
    c2otc = list(map(lambda x: x[0], curs.execute(c2sql).fetchall()))

    comparison_dict = {}

    for outcome1 in c1otc:
        # print("Outcome1: ", outcome1)
        comp_list = []
        for outcome2 in c2otc:
            outcomes_and_score = []
            outcome_score = compare_descriptions(outcome1, outcome2, False)
            # outcomes_and_score.append(outcome1)
            outcomes_and_score.append(outcome2)
            outcomes_and_score.append(outcome_score)
            comp_list.append(outcomes_and_score)

        # print("Pre-sort: ", comp_list)
        comp_list.sort(key=lambda x: x[1], reverse=True)
        # print("Post-sort: ", comp_list)
        comparison_dict[outcome1] = comp_list
        # print("Dictionary: ", comparison_dict)

    form_data = grab_form_data(db, course2, course1)
    file_gen = FileGen2.FileGen(form_data[0], form_data[1], form_data[2], form_data[3], form_data[4], form_data[5],
                                form_data[6], form_data[7])

    for oc, jst in comparison_dict.items():
        file_gen.Like_Outcomes(oc, jst)

    file_name = './files/EvalForms/' + course1 + '_' + course2 + '_Eval_Form.docx'
    file_gen.Save_Doc(file_name)


'''
# Code used for building table and testing
course_and_desc_list = [{}, {}, {}]
table_name = 'DescriptionComparisons'
database_name = 'mce.sqlite3'
db2 = 'mce2.sqlite3'

course_and_desc_list = fetch_course_descriptions(course_and_desc_list, database_name)
# comparison_table = mass_compare_descriptions(course_and_desc_list[0], course_and_desc_list[2])
# build_comparison_table(comparison_table, database_name, table_name, course_and_desc_list)

jst_course1 = 'A-830-0030'
jst_course2 = 'AR-2201-0603'

for course, desc in course_and_desc_list[2].items():
    print("Course: ", course)
    comp_list = comparison_list(database_name, table_name, course)
    output_comparisons(course, comp_list, database_name, './ComparisonReports/wup_no_syns/')
'''


database = 'mce.sqlite3'
# oc_courses = ['PE 107']
# jst_courses = ['A-830-0030']

oc_courses = ['CJ 220', 'IRM 340', 'JMC 105', 'MTH 120', 'SCI 107', 'PE 107']
jst_courses = ['A-830-0030', 'NV-1710-0118', 'AR-2201-0603', 'NV-1710-0118', 'AR-1601-0277', 'A-830-0030']

# form_data = grab_form_data(database, jst_courses[0], oc_courses[0])
# print(form_data)

for i in range(0, len(oc_courses)):
    # print("OC Course: ", oc_courses[i])
    # print("JST Course: ", jst_courses[i])
    compare_courses(oc_courses[i], jst_courses[i], database)

