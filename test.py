import unittest

from pattern.en import wordnet
from extract import synset_is_person, lemma_is_person, synset_is_proper, \
    get_nouns, has_people, get_pronouns, first_s

class TestExtraction(unittest.TestCase):
    def test_get_nouns(self):
        nouns = get_nouns(nlp,
                first_s(nlp, u'the tree was near both rivers.'))
        self.assertEqual(
                [w.lemma_ for w in nouns],
                ['tree', 'river'])

    def test_get_pronouns(self):
        pronouns = get_pronouns(
                nlp, first_s(
                nlp, u"we talked to him about her problems with them"))
        self.assertEqual(
                [w.lemma_ for w in pronouns],
                ['we', 'him', 'her', 'them'])

    def test_has_people(self):
        self.assertTrue(has_people(nlp, first_s(
                nlp, u'the banker kissed her wife')))
        self.assertFalse(has_people(nlp, first_s(
                nlp, u'the tree was near both rivers')))
        self.assertTrue(has_people(nlp, first_s(
                nlp, u'we ate it')))
        self.assertFalse(has_people(nlp, first_s(
                nlp, u'it was beautiful')))
        self.assertTrue(has_people(nlp, first_s(
                nlp, u'The dog was unhappy with Jane')))
        self.assertTrue(has_people(nlp, first_s(
                nlp, u'The girl is innocent.')))

    def test_subjects_are_physical_objects(self):
        from extract import subjects_are_physical_objects
        self.assertTrue(subjects_are_physical_objects(
                first_s(
                    nlp, u'the rock was beautiful')))
        self.assertFalse(subjects_are_physical_objects(
                first_s(
                    nlp, u'truth was unnecessary')))
        self.assertFalse(subjects_are_physical_objects(
                first_s(
                    nlp, u'asdf asdf asdf')))
                
    def test_subjects_are_geological_formations(self):
        from extract import subjects_are_geological_formations
        self.assertTrue(subjects_are_geological_formations(
                first_s(
                    nlp, u'the mesa was beautiful')))
        self.assertFalse(subjects_are_geological_formations(
                first_s(
                    nlp, u'truth was unnecessary')))
        self.assertFalse(subjects_are_geological_formations(
                first_s(
                    nlp, u'asdf asdf asdf')))


    def test_physical_object_count(self):
        from extract import physical_object_count
        self.assertEqual(physical_object_count(
            nlp, first_s(nlp, u"the rocks are good")), 1)

    def test_has_pronoun_subject(self):
        from extract import has_pronoun_subject
        self.assertTrue(has_pronoun_subject(nlp,
            first_s(nlp, u"it is really awful")))
        self.assertFalse(has_pronoun_subject(nlp,
            first_s(nlp, u"the dog is really awful")))
        self.assertTrue(has_pronoun_subject(nlp,
            first_s(nlp,
                u"It is one of the most graceful of the conifers.")))

    def test_get_nsubj(self):
        from extract import get_nsubj
        nsubj = get_nsubj(
            first_s(nlp,
                u"The growing darkness seemed a protection."))
        self.assertEqual(nsubj.string.strip(), u'The growing darkness')
        nsubj2 = get_nsubj(
            first_s(nlp,
                u"Annoyingly, the fish I ate yesterday swam."))
        self.assertEqual(nsubj2.string.strip(), u'the fish I ate yesterday')

    def test_sentence_is_past(self):
        from extract import sentence_is_past
        self.assertTrue(sentence_is_past(
            first_s(nlp, u"The fish were hungry")))
        self.assertFalse(sentence_is_past(
            first_s(nlp, u"The fish have hunger")))

    def test_clauses(self):
        from extract import clause_extract
        ccs = clause_extract(first_s(nlp,
            u"we went to the store; they were out of hotdogs and we left"))
        clause_strs = [c.text for c in ccs]
        target = [u'we went to the store',
                u'we left', u'they were out of hotdogs']
        self.assertEqual(clause_strs, target)
        ccs = clause_extract(first_s(nlp,
            u"A little hole showed back of the left ear and another at the right temple."))
        print [c.text for c in ccs]
        ccs = clause_extract(first_s(nlp,
            u"The storm continued four days, and the snow had reached a depth very uncommon; but day after day the search was renewed."))
        print [c.text for c in ccs]

    def test_prep_phrases(self):
        from extract import prep_phrases
        s = first_s(nlp, u"The blizzard continued throughout the afternoon.")
        target = "throughout the afternoon"
        pps = prep_phrases(s.root)
        self.assertEqual(target, pps[0].text)

    def test_get_nsubj_from_clause(self):
        from extract import clauses, get_nsubj
        s = first_s(nlp,
                u"The sea was pretty calm; a slight breeze blew on land.")
        ccs = clauses(s)
        self.assertEqual(get_nsubj(ccs[0]).text, "The sea")
        self.assertEqual(get_nsubj(ccs[1]).text, "a slight breeze")

    def test_requires_past_tense_agreement(self):
        from extract import requires_past_tense_agreement
        s = first_s(nlp,
            u"The rammed earth walls were nearly obliterated by now.")
        self.assertTrue(requires_past_tense_agreement(s))
        s = first_s(nlp, u"The waves were tremendous.")
        self.assertTrue(requires_past_tense_agreement(s))
        s = first_s(nlp, u"The waves were getting larger.")
        self.assertTrue(requires_past_tense_agreement(s))
        s = first_s(nlp, u"The wave was tremendous.")
        self.assertTrue(requires_past_tense_agreement(s))
        s = first_s(nlp, u"The wave was getting larger.")
        self.assertTrue(requires_past_tense_agreement(s))
        s = first_s(nlp, u"The wave broke.")
        self.assertFalse(requires_past_tense_agreement(s))

    def test_indefify(self):
        from extract import indefify, get_nsubj
        s = first_s(nlp, u"The rain in spain falls mainly on the plain")
        nsubj = get_nsubj(s)
        self.assertEqual(u"a rain in spain", indefify(nsubj))
        s = first_s(nlp, u"The umbrella in spain falls mainly on the plain")
        nsubj = get_nsubj(s)
        self.assertEqual(u"an umbrella in spain", indefify(nsubj))
        s = first_s(nlp, u"Yesterday a man on the freeway lost his watch")
        self.assertRaises(IndexError, indefify, get_nsubj(s))
        s = first_s(nlp, u"Every man with a fortune must be in want")
        self.assertRaises(IndexError, indefify, get_nsubj(s))
        s = first_s(nlp, u"The buildings were delicious.")
        self.assertEqual(u"some buildings", indefify(get_nsubj(s)))
        s = first_s(nlp, u"all the windows were broken")
        self.assertEqual(u"some windows", indefify(get_nsubj(s)))


if __name__ == '__main__':
    import sys, os
    from spacy.en import English
    sys.stderr.write("initializing spacy...\n")
    nlp = English(data_dir=os.environ.get('SPACY_DATA'))
    sys.stderr.write("done.\n")
    unittest.main()


