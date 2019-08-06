from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
import FileGen3 as FileGen2
from Course import Course
from Reviewer import Reviewer
import multiprocessing as mp


class CourseComparison:

    def __init__(self, c1, c2, rev, db):
        self.course1 = Course(db, c1)
        self.course2 = Course(db, c2)
        self.reviewer = Reviewer(db, rev)
        self.comp1 = None
        self.outcomes_and_score = []
        pass

    def penn_to_wn(self, tag):
        # Convert between a Penn Treebank tag to a simplified Wordnet tag
        if tag.startswith('N'):
            return 'n'
        if tag.startswith('V'):
            return 'v'
        if tag.startswith('J'):
            return 'a'
        if tag.startswith('R'):
            return 'r'
        return None

    def tagged_to_synset(self, word, tag):
        # return synset (set of synonyms) based on the Wordnet tag of each word
        wn_tag = self.penn_to_wn(tag)
        if wn_tag is None:
            return None
        try:
            return wn.synsets(word, wn_tag)
        except:
            return None

    def tokenize_sentence(self, group1):
        """
        :param group1: String to be tokenized
        :return: tokenized string
        """
        sentence = pos_tag(word_tokenize(group1))
        sentence = [self.tagged_to_synset(*tagged_word) for tagged_word in sentence]
        sentence = [ss for ss in sentence if ss]
        return sentence

    def compare_words(self, sentence1, sentence2):
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

                if len(set1.intersection(set2)) > 0:
                    # if a word from one set is found to have a synonym in the other set,
                    # then set the score to 1, or 100%
                    wup_score = 1
                else:
                    # if an exact match is not found, take the score of the word against
                    # all other words, then take the best match
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

    def compare_string(self, string1, string2):
        """
        :param class1: First description being compared
        :param class2: Second description being compared
        :return: Similarity score of the two descriptions
        Compute similarity between descriptions using Wordnet
        """

        sentence1 = self.tokenize_sentence(string1)
        sentence2 = self.tokenize_sentence(string2)

        symmetrical_score = (self.compare_words(sentence1, sentence2) +
                             self.compare_words(sentence2, sentence1)) / 2

        score = float('{:.3f}'.format(symmetrical_score * 100))
        return score

    # old course comparison function, replaced by multiprocessing functions
    # def compare_courses(self):
    #     comparison_dict = {}
    #
    #     for outcome1 in self.course1.outcomes:
    #         comp_list = []
    #         for outcome2 in self.course2.outcomes:
    #             outcomes_and_score = []
    #             outcome_score = self.compare_string(outcome1, outcome2)
    #             outcomes_and_score.append(outcome2)
    #             outcomes_and_score.append(outcome_score)
    #             comp_list.append(outcomes_and_score)
    #
    #         comp_list.sort(key=lambda x: x[1], reverse=True)
    #         comparison_dict[outcome1] = comp_list
    #
    #     file_gen = FileGen2.FileGen(self.course1, self.course2, self.reviewer)
    #
    #     file_gen.find_split_and_copy(len(comparison_dict))
    #
    #     for oc, jst in comparison_dict.items():
    #         file_gen.like_outcome_tables(oc, jst)
    #
    #     file_name = self.course1.number + '_' + self.course2.number + '_Eval_Form.docx'
    #     file_gen.save_doc(file_name)

    def single_compare(self, outcome1):
        # compare single set of courses - designed to be used by multiprocessing
        newdict = {}
        comp_list = []
        for outcome2 in self.course2.outcomes:
            outcomes_and_scores = []
            outcome_score = self.compare_string(outcome1, outcome2)
            outcomes_and_scores.append(outcome2)
            outcomes_and_scores.append(outcome_score)
            comp_list.append(outcomes_and_scores)
        comp_list.sort(key=lambda x: x[1], reverse=True)
        newdict[outcome1] = comp_list
        # return dictionaries which will be sent to FileGen
        return newdict

    def compare(self):
        # compare courses using multiprocessing
        comparison_dict = {}
        pool = mp.Pool(mp.cpu_count())  # dynamically set number of CPUs

        # run single_compare with multiprocessing, putting the resulting dictionaries into a list
        dlist = pool.map(self.single_compare, [oc1 for oc1 in self.course1.outcomes])

        for outcome in dlist:
            comparison_dict.update(outcome)  # merge the list of dictionaries into one

        # lastly, run FileGen to generate the documents
        file_gen = FileGen2.FileGen(self.course1, self.course2, self.reviewer)

        file_gen.find_split_and_copy(len(comparison_dict))

        for oc, jst in comparison_dict.items():
            file_gen.like_outcome_tables(oc, jst)

        file_name = self.course1.number + '_' + self.course2.number + '_Eval_Form.docx'
        file_gen.save_doc(file_name)
