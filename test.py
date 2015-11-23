import unittest

from pattern.en import wordnet
from extract import synset_is_person, lemma_is_person, synset_is_proper, \
    get_nouns, has_people, sentences_with_lemmata, get_pronouns

class TestExtraction(unittest.TestCase):
    def test_get_nouns(self):
        nouns = get_nouns(nlp,
                sentences_with_lemmata(
                    nlp, u'the tree was near both rivers.')[0])
        self.assertEqual(
                [w.lemma_ for w in nouns],
                ['tree', 'river'])

    def test_get_pronouns(self):
        pronouns = get_pronouns(
                nlp, sentences_with_lemmata(
                nlp, u"we talked to him about her problems with them")[0])
        self.assertEqual(
                [w.lemma_ for w in pronouns],
                ['we', 'him', 'her', 'them'])

    def test_has_people(self):
        self.assertTrue(has_people(nlp, sentences_with_lemmata(
                nlp, u'the banker kissed her wife')[0]))
        self.assertFalse(has_people(nlp, sentences_with_lemmata(
                nlp, u'the tree was near both rivers')[0]))
        self.assertTrue(has_people(nlp, sentences_with_lemmata(
                nlp, u'we ate it')[0]))
        self.assertFalse(has_people(nlp, sentences_with_lemmata(
                nlp, u'it was beautiful')[0]))
        self.assertTrue(has_people(nlp, sentences_with_lemmata(
                nlp, u'The dog was unhappy with Jane')[0]))
        self.assertTrue(has_people(nlp, sentences_with_lemmata(
                nlp, u'The girl is innocent.')[0]))

    def test_subjects_are_physical_objects(self):
        from extract import subjects_are_physical_objects
        self.assertTrue(subjects_are_physical_objects(
                sentences_with_lemmata(
                    nlp, u'the rock was beautiful')[0]))
        self.assertFalse(subjects_are_physical_objects(
                sentences_with_lemmata(
                    nlp, u'truth was unnecessary')[0]))
        self.assertFalse(subjects_are_physical_objects(
                sentences_with_lemmata(
                    nlp, u'asdf asdf asdf')[0]))
                
    def test_subjects_are_geological_formations(self):
        from extract import subjects_are_geological_formations
        self.assertTrue(subjects_are_geological_formations(
                sentences_with_lemmata(
                    nlp, u'the mesa was beautiful')[0]))
        self.assertFalse(subjects_are_geological_formations(
                sentences_with_lemmata(
                    nlp, u'truth was unnecessary')[0]))
        self.assertFalse(subjects_are_geological_formations(
                sentences_with_lemmata(
                    nlp, u'asdf asdf asdf')[0]))


    def test_physical_object_count(self):
        from extract import physical_object_count
        self.assertEqual(physical_object_count(
            nlp, sentences_with_lemmata(nlp, u"the rocks are good")[0]), 1)

    def test_has_pronoun_subject(self):
        from extract import has_pronoun_subject
        self.assertTrue(has_pronoun_subject(nlp,
            sentences_with_lemmata(nlp, u"it is really awful")[0]))
        self.assertFalse(has_pronoun_subject(nlp,
            sentences_with_lemmata(nlp, u"the dog is really awful")[0]))
        self.assertTrue(has_pronoun_subject(nlp,
            sentences_with_lemmata(nlp,
                u"It is one of the most graceful of the conifers.")[0]))

    def test_get_nsubj(self):
        from extract import get_nsubj
        nsubj = get_nsubj(
            sentences_with_lemmata(nlp,
                u"The growing darkness seemed a protection.")[0])
        self.assertEqual(nsubj.string.strip(), u'The growing darkness')
        nsubj2 = get_nsubj(
            sentences_with_lemmata(nlp,
                u"Annoyingly, the fish I ate yesterday swam.")[0])
        self.assertEqual(nsubj2.string.strip(), u'the fish I ate yesterday')

    def test_sentence_is_past(self):
        from extract import sentence_is_past
        self.assertTrue(sentence_is_past(
            sentences_with_lemmata(nlp, u"The fish were hungry")[0]))
        self.assertFalse(sentence_is_past(
            sentences_with_lemmata(nlp, u"The fish have hunger")[0]))

if __name__ == '__main__':
    import sys, os
    from spacy.en import English
    sys.stderr.write("initializing spacy...\n")
    nlp = English(data_dir=os.environ.get('SPACY_DATA'))
    sys.stderr.write("done.\n")
    unittest.main()


