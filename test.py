import unittest

from pattern.en import wordnet, parsetree
from extract import synset_is_person, lemma_is_person, synset_is_proper, \
    get_nouns, has_people, sentences_with_lemmata, get_pronouns

class TestExtraction(unittest.TestCase):
    def test_synset_synset_is_person(self):
        baker_ss = wordnet.synsets('baker')[0]
        self.assertTrue(synset_is_person(baker_ss))
        tree_ss = wordnet.synsets('tree')[0]
        self.assertFalse(synset_is_person(tree_ss))

    def test_lemma_is_person(self):
        self.assertTrue(lemma_is_person('baker'))
        self.assertFalse(lemma_is_person('tree'))
        self.assertFalse(lemma_is_person('lake'))
        self.assertTrue(lemma_is_person('person'))
        self.assertFalse(lemma_is_person('asdf'))

    def test_synset_is_proper(self):
        tree_ss = wordnet.synsets('tree')[0]
        Tree_ss = wordnet.synsets('tree')[2]
        self.assertFalse(synset_is_proper(tree_ss))
        self.assertTrue(synset_is_proper(Tree_ss))

    def test_get_nouns(self):
        nouns = get_nouns(
                sentences_with_lemmata('the tree was near both rivers.')[0])
        self.assertEqual(
                [w.lemma for w in nouns],
                ['tree', 'river'])

    def test_get_pronouns(self):
        pronouns = get_pronouns(sentences_with_lemmata(
                "we talked to him about her problems with them")[0])
        self.assertEqual(
                [w.lemma for w in pronouns],
                ['we', 'him', 'her', 'them'])

    def test_has_people(self):
        self.assertTrue(has_people(sentences_with_lemmata(
                'the banker kissed her wife')[0]))
        self.assertFalse(has_people(sentences_with_lemmata(
                'the tree was near both rivers')[0]))
        self.assertTrue(has_people(sentences_with_lemmata(
                'we ate it')[0]))
        self.assertFalse(has_people(sentences_with_lemmata(
                'it was beautiful')[0]))
        self.assertTrue(has_people(sentences_with_lemmata(
                'The dog was unhappy with Jane')[0]))

    def test_subjects_are_physical_objects(self):
        from extract import subjects_are_physical_objects
        self.assertTrue(subjects_are_physical_objects(sentences_with_lemmata(
                'the rock was beautiful')[0]))
        self.assertFalse(subjects_are_physical_objects(sentences_with_lemmata(
                'truth was unnecessary')[0]))
        self.assertFalse(subjects_are_physical_objects(sentences_with_lemmata(
                'asdf asdf asdf')[0]))

    def test_synset_is_physical_object(self):
        from extract import synset_is_physical_object
        tree_ss = wordnet.synsets('tree')[0]
        self.assertTrue(synset_is_physical_object(tree_ss))
        truth_ss = wordnet.synsets('truth')[0]
        self.assertFalse(synset_is_physical_object(truth_ss))

    def test_lemma_is_physical_object(self):
        from extract import lemma_is_physical_object
        self.assertTrue(lemma_is_physical_object('tree'))
        self.assertFalse(lemma_is_physical_object('truth'))
        self.assertFalse(lemma_is_physical_object('asdf'))

    def test_physical_object_count(self):
        from extract import physical_object_count
        self.assertEqual(physical_object_count(
            sentences_with_lemmata("the rocks are good")[0]), 1)

if __name__ == '__main__':
    unittest.main()


