import re
import sys

from pattern.en import parsetree, wordnet, article
from pattern.text.en.wordnet import Synset
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

def first_s(nlp, s):
    return sentences_with_lemmata(nlp, s)[0]

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
    for i, token in enumerate(sentence.root.subtree):
        deps = dep_to_root(token)
        if ('nsubj' in deps or 'nsubjpass' in deps) and \
                (sentence.start <= token.i < sentence.end):
            nsubj.append(token.i)
    if len(nsubj) == 0:
        raise ValueError
    nsubj_span = Span(sentence.doc, min(nsubj), max(nsubj)+1)
    return nsubj_span

def replace_span(sentence, span, s):
    return sentence.text.replace(span.text, s)

def nsubj_is_plural(nsubj):
    return nsubj.root.tag_ == 'NNS'

def sentence_is_past(sentence):
    return sentence.root.tag_ == 'VBD'

def sentence_is_present(sentence):
    return sentence.root.tag_ in ('VBZ', 'VBP')

def get_aux(sentence):
    for child in sentence.root.children:
        if child.dep_ in ('aux', 'auxpass'):
            return child
    return None

def requires_past_tense_agreement(sentence):
    if sentence.root.lower_ in ('was', 'were'):
        return True
    aux = get_aux(sentence)
    if aux and aux.lower_ in ('was', 'were'):
        return True
    else:
        return False

def subtree_extent(span):
    extent = [tok.i for tok in span]
    return (min(extent), max(extent)+1)

def span_subtract(whole, part):
    if part.start > whole.end or part.end < whole.start:
        return whole
    if part.start <= whole.start:
        return Span(whole.doc, part.end, whole.end)
    else:
        return Span(whole.doc, whole.start, part.start)

def trim_tokens(span, tokens=None):
    if tokens is None:
        tokens = ['punct', 'cc']
    start = span.start
    end = span.end
    for i, tok in enumerate(span):
        if tok.dep_ in tokens:
            start = span.start + (i+1)
        else:
            break
    for i, tok in enumerate(reversed(span)):
        if tok.dep_ in tokens:
            end = span.end - (i+1)
        else:
            break
    return Span(span.doc, start, end)

def clauses(sentence, i=""):
    root = sentence.root
    results = list()
    ccomps = list()
    for child in root.children:
        # don't check children OUTSIDE the span
        if sentence.start <= child.i <= sentence.end:
            if child.dep_ in ('ccomp', 'conj') and child.tag_.startswith('VB'):
                ccomps.append(child)
    rest_span = Span(sentence.doc, sentence.start, sentence.end)
    if len(ccomps) > 0:
        for child in ccomps:
            ccomp_span = Span(sentence.doc, *subtree_extent(child.subtree))
            rest_span = span_subtract(rest_span, ccomp_span)
            results.extend(clauses(ccomp_span, i+">"))
        results.append(trim_tokens(rest_span))
    else:
        results.append(trim_tokens(sentence))
    return results

def span_from_token_seq(tokens):
    tlist = list(tokens)
    """FIXME: assert that all of the tokens belong to the same document?"""
    return Span(tlist[0].doc, *subtree_extent(tlist))

def prep_phrases(root):
    phrases = list()
    for child in root.children:
        if child.dep_ == 'prep':
            phrases.append(span_from_token_seq(child.subtree))
    return phrases

def indefify(span):
    # find that article (will raise IndexError, watch out)
    det = [t for t in span.root.children \
            if t.dep_ == 'det' and t.lower_ in ('the', 'this', 'these')][0]
    # flatten to string replacing article
    following = span.doc[det.i+1]
    if span.root.tag_ == 'NNS':
        det_s = 'some'
    else:
        det_s = article(following.lower_)
    output = list()
    for t in span.subtree:
        if t.dep_ == 'predet':
            continue
        if t.i == det.i:
            output.append(det_s)
        else:
            output.append(t.orth_)
    return " ".join(output)

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
    s = re.sub(r'[{}]', '', s)
    s = re.sub(r' - ', '-', s)
    s = re.sub(r'_', '', s)
    if ')' in s and '(' not in s:
        s = s.replace(')', '')
    if '(' in s and ')' not in s:
        s = s.replace('(', '')
    return ucfirst(s)

def punctuate(s):
    if not(re.search(r"[.!?]$", s)):
        s += "."
    return s

def depunct(s):
    if re.search(r"[.!?]$", s):
        return s[:-1]
    else:
        return s

def ucfirst(s):
    return s[0].upper() + s[1:]

def nature_sentences(nlp, s, tense_check=sentence_is_past):
    for sentence in sentences_with_lemmata(nlp, s):
        if not(has_people(nlp, sentence)) and \
                subjects_are_natural(sentence) and \
                not(has_pronoun_subject(nlp, sentence)) and \
                tense_check(sentence) and \
                len(sentence.text) > 20 and \
                len(sentence.text) < 140:
            yield ucfirst(normalize(sentence.text))

def main(nlp, s):
    import sys, os
    for sentence in sentences_with_lemmata(nlp, s):
        if not(has_people(nlp, sentence)) and \
                subjects_are_natural(sentence) and \
                not(has_pronoun_subject(nlp, sentence)) and \
                sentence_is_past(sentence):
            if not(sentence.string.startswith('"')):
                try:
                    nsubj_span = get_nsubj(sentence)
                except ValueError:
                    continue
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
