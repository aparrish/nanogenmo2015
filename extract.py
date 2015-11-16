import re

from pattern.en import parsetree, wordnet
from spacy.en import English

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
        return True
    else:
        return any([synset_is_physical_object(s) for s in synsets \
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
    any_person_nouns = any([lemma_is_person(nn.lemma) \
            for nn in get_nouns(nlp, s)])
    any_not_its = any([prp.lemma_ != 'it' for prp in get_pronouns(nlp, s)])
    return any_person_nouns or any_not_its or any_proper_nouns or any_caps

def physical_object_count(nlp, s):
    nns = get_nouns(nlp, s)
    count = len([nn.lemma_ for nn in nns \
            if lemma_is_physical_object(nn.lemma_)])
    return count

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

def normalize(s):
    s = s.lower().strip()
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
                subjects_are_physical_objects(sentence):
            if not(sentence.string.startswith('"')):
                output = normalize(sentence.string)
                if len(output) > 20:
                    print ucfirst(output).replace("\r\n", " ")

if __name__ == '__main__':
    from spacy.en import English
    nlp = English(data_dir=os.environ.get('SPACY_DATA'))
    main(nlp)
