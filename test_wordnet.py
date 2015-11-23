import unittest

from pattern.en import wordnet
from extract import synset_is_person, lemma_is_person, synset_is_proper, \
    sentences_with_lemmata 

class TestWordNet(unittest.TestCase):
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

    def test_lemma_is_geological_formation(self):
        from extract import lemma_is_geological_formation
        self.assertTrue(lemma_is_geological_formation('beach'))
        self.assertFalse(lemma_is_geological_formation('truth'))
        self.assertFalse(lemma_is_geological_formation('asdf'))
        self.assertFalse(lemma_is_geological_formation('might'))

    def test_lemma_is_natural(self):
        from extract import lemma_is_natural
        self.assertTrue(lemma_is_natural('rock'))
        self.assertTrue(lemma_is_natural('beach'))
        self.assertFalse(lemma_is_natural('truth'))
        self.assertFalse(lemma_is_natural('asdf'))
        self.assertFalse(lemma_is_natural('might'))

if __name__ == '__main__':
    unittest.main()

