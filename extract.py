import re

from pattern.en import parsetree, wordnet
from pattern.en.wordnet import Synset
from spacy.tokens import Span

person_ss = wordnet.synsets('person')[0]
def synset_is_person(synset):
    hypernyms = synset.hypernyms(recursive=True)
    return synset == person_ss or person_ss in hypernyms

def synset_is_proper(synset):
    return any([syn[0].isupper() for syn in synset.synonyms])

physical_object_ss = wordnet.synsets('physical object')[0]
def synset_is_physical_object(synset):
    hypernyms = synset.hypernyms(recursive=True)
    return synset == physical_object_ss or physical_object_ss in hypernyms

def lemma_is_physical_object(lemma):
    synsets = wordnet.synsets(lemma, wordnet.NOUN)
    if len(synsets) > 0 and all([synset_is_proper(s) for s in synsets]):
        return False
    else:
        return any([synset_is_physical_object(s) for s in synsets \
                if not(synset_is_proper(s))])

formation_ss = wordnet.synsets('geological_formation')[0]
def synset_is_geological_formation(synset):
    hypernyms = synset.hypernyms(recursive=True)
    return synset == formation_ss or formation_ss in hypernyms

def lemma_is_geological_formation(lemma):
    synsets = wordnet.synsets(lemma, wordnet.NOUN)
    if len(synsets) > 0 and all([synset_is_proper(s) for s in synsets]):
        return False
    else:
        return any([synset_is_geological_formation(s) for s in synsets \
                if not(synset_is_proper(s))])

nature_synsets = [Synset(u'natural object'), Synset(u'body of water'),
        Synset(u'geological formation'), Synset(u'location'), Synset(u'shape'),
        Synset(u'natural phenomenon'), Synset(u'land')]
def synset_is_natural(synset):
    hypernyms = synset.hypernyms(recursive=True)
    return synset in nature_synsets or any([h in nature_synsets for h in
        hypernyms])
def lemma_is_natural(lemma):
    synsets = wordnet.synsets(lemma, wordnet.NOUN)
    if len(synsets) > 0 and all([synset_is_proper(s) for s in synsets]):
        return False
    else:
        return any([synset_is_natural(s) for s in synsets \
                if not(synset_is_proper(s))])

def lemma_is_person(lemma):
    synsets = wordnet.synsets(lemma, wordnet.NOUN)
    # if ALL the synsets are proper, then it's a person!
    if len(synsets) > 0 and all([synset_is_proper(s) for s in synsets]):
        return True
    # otherwise, check ONLY the non-proper synsets
    else:
        return any([synset_is_person(s) for s in synsets \
                if not(synset_is_proper(s))])

def sentences_with_lemmata(nlp, s):
    return list(nlp(s).sents)

def get_nouns(nlp, sentence):
    NN = nlp.vocab.strings['NN']
    NNS = nlp.vocab.strings['NNS']
    for word in sentence:
        if word.tag in (NN, NNS):
            yield word

def get_pronouns(nlp, sentence):
    PRP = nlp.vocab.strings['PRP']
    PRPS = nlp.vocab.strings['PRP$']
    for word in sentence:
        if word.tag in (PRP, PRPS):
            yield word

def has_people(nlp, s):
    NNP = nlp.vocab.strings['NNP']
    any_proper_nouns = any([word.tag == NNP for word in s])
    any_caps = any([word.string[0].isupper() for word in s[1:]])
    any_person_nouns = any([lemma_is_person(nn.lemma_) \
            for nn in get_nouns(nlp, s)])
    any_not_its = any([prp.lemma_ not in ('it', 'its') for prp in get_pronouns(nlp, s)])
    return any_person_nouns or any_not_its or any_proper_nouns or any_caps

def physical_object_count(nlp, s):
    nns = get_nouns(nlp, s)
    count = len([nn.lemma_ for nn in nns \
            if lemma_is_physical_object(nn.lemma_)])
    return count

def has_pronoun_subject(nlp, s):
    PRP = nlp.vocab.strings['PRP']
    children = list(s.root.children)
    for child in children:
        if child.dep_ == 'nsubj' and child.tag == PRP:
            return True
    return False

def hypernym_chains(lemma):
    chains = []
    synsets = wordnet.synsets(lemma, pos=wordnet.NOUN)
    for synset in synsets:
        chains.append(synset.hypernyms(recursive=True))
    return chains

def subjects_are_physical_objects(sentence):
    subj_head_lemmas = []
    for word in sentence:
        if word.dep_ == 'nsubj':
            subj_head_lemmas.append(word.lemma_)
    return len(subj_head_lemmas) > 0 and \
            all([lemma_is_physical_object(lem) for lem in subj_head_lemmas])

def subjects_are_geological_formations(sentence):
    subj_head_lemmas = []
    for word in sentence:
        if word.dep_ == 'nsubj':
            subj_head_lemmas.append(word.lemma_)
    return len(subj_head_lemmas) > 0 and \
            all([lemma_is_geological_formation(lem) for lem in subj_head_lemmas])

def subjects_are_natural(sentence):
    subj_head_lemmas = []
    for word in sentence:
        if word.dep_ == 'nsubj':
            subj_head_lemmas.append(word.lemma_)
    return len(subj_head_lemmas) > 0 and \
            all([lemma_is_natural(lem) for lem in subj_head_lemmas])

def dep_to_root(token):
    if token.head.dep_ == 'ROOT': return [token.dep_]
    return [token.dep_] + dep_to_root(token.head)

def get_nsubj(sentence):
    nsubj = list()
    for i, token in enumerate(sentence.subtree):
        deps = dep_to_root(token)
        if deps[-1] in ('nsubj', 'nsubjpass'):
            nsubj.append(i)
    nsubj_span = Span(sentence.doc, sentence.start+min(nsubj),
            sentence.start+max(nsubj)+1)
    return nsubj_span

def replace_span(sentence, span, s):
    return sentence.text.replace(span.text, s)

def nsubj_is_plural(nsubj):
    return nsubj.root.tag_ == 'NNS'

def normalize(s):
    s = s.lower().strip()
    s = re.sub("[\r\n]+", " ", s)
    s = re.sub(r"others '", "others'", s)
    s = re.sub(r'(^|\s+)[\'"`_](\s+|$)', ' ', s)
    s = re.sub(r"\s([.,;:!?])(\s|$)", r"\1 ", s)
    s = re.sub(r"\s*'s", "'s", s)
    s = re.sub(r'\bi\b', 'I', s)
    s = re.sub(r'\(\s*([^)]*)\)', r'(\1)', s)
    s = re.sub(r'\s*\)', ')', s)
    s = re.sub(r'--', u"\u2014", s)
    if ')' in s and '(' not in s:
        s = s.replace(')', '')
    if '(' in s and ')' not in s:
        s = s.replace('(', '')
    return s

def ucfirst(s):
    return s[0].upper() + s[1:]

def main(nlp, s):
    import sys, os
    for sentence in sentences_with_lemmata(nlp, s):
        if not(has_people(nlp, sentence)) and \
                subjects_are_natural(sentence) and \
                not(has_pronoun_subject(nlp, sentence)):
            if not(sentence.string.startswith('"')):
                nsubj_span = get_nsubj(sentence)
                if nsubj_is_plural(nsubj_span):
                    pronounified = replace_span(sentence, nsubj_span, "they")
                else:
                    pronounified = replace_span(sentence, nsubj_span, "it")
                preface = normalize("we saw " + nsubj_span.text + ".")
                output = normalize(pronounified)
                if len(output) > 20:
                    print ucfirst(normalize(sentence.text)), "->", ucfirst(preface), ucfirst(output)

if __name__ == '__main__':
    from spacy.en import English
    nlp = English(data_dir=os.environ.get('SPACY_DATA'))
    main(nlp)
