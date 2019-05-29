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


def syns_tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None

    try:
        # print("Synset type: ", type(wn.synsets(word, wn_tag)[0]))
        return wn.synsets(word, wn_tag)
    except:
        return None


def syns_tokenize_sentence(group1):
    """
    :param group1: String to be tokenized
    :return: tokenized string
    """
    sentence = pos_tag(word_tokenize(group1))
    sentence = [syns_tagged_to_synset(*tagged_word) for tagged_word in sentence]
    sentence = [ss for ss in sentence if ss]
    # print("Sentence: ", sentence)
    print(sentence)
    return sentence


def syns_compare_words(sentence1, sentence2, zero_bad_matches):
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
            final_scores.append(max(word_scores))
            # average_word_score = sum(word_scores) / len(word_scores)
            # final_scores.append(average_word_score)
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

    sentence1 = syns_tokenize_sentence(class1)
    sentence2 = syns_tokenize_sentence(class2)

    symmetrical_score = (syns_compare_words(sentence1, sentence2, zero_bad_matches) +
                         syns_compare_words(sentence2, sentence1, zero_bad_matches)) / 2

    score = '{:.3f}'.format(symmetrical_score * 100)
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

        # if (
        # curs.execute('''select CourseDescription from Course where CourseNumber=?''', course).fetchone()) is not None:
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


course_and_desc_list = [{}, {}, {}]
table_name = 'DescriptionComparisons'
database_name = 'mce.sqlite3'
db2 = 'mce2.sqlite3'


course_and_desc_list = fetch_course_descriptions(course_and_desc_list, db2)
comparison_table = mass_compare_descriptions(course_and_desc_list[0], course_and_desc_list[2])
build_comparison_table(comparison_table, db2, table_name, course_and_desc_list)


for course, desc in course_and_desc_list[2].items():
    print("Course: ", course)
    comp_list = comparison_list(db2, table_name, course)
    output_comparisons(course, comp_list, db2, './ComparisonReports/wup_syns/')