import re

from pattern.en import wordnet, parsetree

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

def sentences_with_lemmata(s):
    return parsetree(s, lemmata=True, relations=True, encoding='utf-8')

def get_nouns(sentence):
    for word in sentence:
        if word.type.startswith('NN'):
            yield word

def get_pronouns(sentence):
    for word in sentence:
        if word.type.startswith('PRP'):
            yield word

def has_people(s):
    any_proper_nouns = any([word.type.startswith('NNP') for word in s])
    any_caps = any([word.string[0].isupper() for word in s[1:]])
    any_person_nouns = any([lemma_is_person(nn.lemma) for nn in get_nouns(s)])
    any_not_its = any([prp.lemma != 'it' for prp in get_pronouns(s)])
    return any_person_nouns or any_not_its or any_proper_nouns or any_caps

def physical_object_count(s):
    nns = get_nouns(s)
    count = len([nn.lemma for nn in nns \
            if lemma_is_physical_object(nn.lemma)])
    return count

def hypernym_chains(lemma):
    chains = []
    synsets = wordnet.synsets(lemma, pos=wordnet.NOUN)
    for synset in synsets:
        chains.append(synset.hypernyms(recursive=True))
    return chains

def subjects_are_physical_objects(sentence):
    subj_head_lemmas = []
    for chunk in sentence.chunks:
        if chunk.role == 'SBJ':
            subj_head_lemmas.append(chunk.head.lemma)
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

if __name__ == '__main__':
    import sys
    for sentence in sentences_with_lemmata(sys.stdin.read().decode('utf8')):
        if not(has_people(sentence)) and \
                subjects_are_physical_objects(sentence):
            if not(sentence.string.startswith('"')):
                output = normalize(sentence.string)
                if len(output) > 20:
                    print ucfirst(output)

