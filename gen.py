import random
import re
import datetime

from pattern.en import wordnet
from extract import get_nsubj, first_s, replace_span, nsubj_is_plural, \
        clauses, prep_phrases, requires_past_tense_agreement, indefify, \
        normalize, punctuate, depunct

chapter_heading_synsets = [wordnet.Synset(u"natural object"),
    wordnet.Synset(u"body of water"),
    wordnet.Synset(u"geological formation"),
    wordnet.Synset(u"location")]
chapter_heading_hyponyms = reduce(list.__add__,
        [ss.hyponyms(recursive=True) for ss in chapter_heading_synsets])
chapter_heading_all_nouns = reduce(list.__add__,
        [ss.synonyms for ss in chapter_heading_hyponyms])
chapter_heading_nouns = ["the " + s for s in chapter_heading_all_nouns \
        if s.islower()]

class Sentence(object):
    """class for "flattened" sentences (i.e., spacy spans that have been
    converted to text), with an extra data attribute to record the subject
    noun phrase."""
    def __init__(self, text, nsubj):
        self.text = text
        self.nsubj = nsubj

def sentence_db(nlp, fh):
    sentences = list()
    clause_list = list()
    for line in fh.readlines():
        line = line.decode('utf8').strip()
        src, text = line.split("\t")
        span_obj = first_s(nlp, text)
        ccs = clauses(span_obj)
        pps = prep_phrases(span_obj.root)
        agree = requires_past_tense_agreement(span_obj)
        # keep sentences with no recognizable subject
        try:
            nsubj = get_nsubj(span_obj)
            plural = nsubj_is_plural(nsubj)
        except ValueError:
            nsubj = None
            plural = None
        sentences.append({
            'src': int(src),
            'text': text,
            'span': span_obj,
            'nsubj': nsubj,
            'agree': agree,
            'plural': plural,
            'pps': pps,
            })
        if len(ccs) > 1:
            clause_list.extend([(src, span_obj, c) for c in ccs])
    for src, span_obj, clause in clause_list:
        pps = prep_phrases(clause.root)
        agree = requires_past_tense_agreement(clause)
        try:
            nsubj = get_nsubj(clause)
            plural = nsubj_is_plural(nsubj)
        except ValueError:
            continue
        sentences.append({
            'src': int(src),
            'text': clause.text,
            'span': clause,
            'nsubj': nsubj,
            'agree': agree,
            'plural': plural,
            'pps': [],
            })
    return sentences

def random_sentences(sdb):
    qualified_sg = [x for x in sdb \
            if x['nsubj'] is not None and x['plural'] is False]
    qualified_pl = [x for x in sdb \
            if x['nsubj'] is not None and x['plural'] is True]
    no_nsubjs = [x for x in sdb if x['nsubj'] is None]
    all_pps = reduce(
            list.__add__, [x['pps'] for x in sdb if len(x['pps']) > 0])
    while True:
        choice = random.randrange(10)
        if choice == 0:
            no_nsubj = random.choice(no_nsubjs)
            yield Sentence(text=no_nsubj['text'], nsubj=None)
        else:
            c, d = random_sentences_match_agreement(sdb)
            if len(c['pps']) > 0 and random.randrange(2) == 0:
                stext = replace_span(c['span'], random.choice(c['pps']),
                        ""+random.choice(all_pps).text+"")
                yield Sentence(text=stext, nsubj=c['nsubj'])
            else:
                stext = replace_span(c['span'], c['nsubj'], d['nsubj'].text)
                yield Sentence(text=stext, nsubj=d['nsubj'])

def random_sentences_match_agreement(sdb):
    sentences_with_subj = [x for x in sdb if x['nsubj'] is not None]
    agree_sg = [x for x in sdb if x['nsubj'] is not None and (not(x['plural']))]
    agree_pl = [x for x in sdb if x['nsubj'] is not None and x['plural']]
    c = random.choice(sentences_with_subj)
    if c['agree'] and c['plural']:
        d = random.choice(agree_pl)
    elif c['agree'] and not(c['plural']):
        d = random.choice(agree_sg)
    else:
        d = random.choice(sentences_with_subj)
    return c, d

def random_sentence_for_nsubj(sdb, nsubj):
    no_agreement_sentences = [x for x in sdb if x['nsubj'] is not None \
            and not(x['agree'])]
    agree_sg = [x for x in sdb if x['nsubj'] is not None and \
            (not(x['plural']) and x['agree'])]
    agree_pl = [x for x in sdb if x['nsubj'] is not None and \
            (x['plural'] and x['agree'])]
    if nsubj is not None:
        if nsubj_is_plural(nsubj):
            d = random.choice(no_agreement_sentences + agree_pl)
            pronoun = "they"
        else:
            d = random.choice(no_agreement_sentences + agree_sg)
            pronoun = "it"
    else:
        d = random.choice(no_agreement_sentences + agree_sg)
        pronoun = "it"
    return pronoun, d

def exposition(sdb, state):
    sentence = random_sentences(sdb).next()
    if sentence.nsubj is not None:
        state.topics.append(sentence.nsubj)
        state.subj_orth.append(sentence.nsubj.orth_)
    return sentence.text

def awareness(sdb, state):
    verbs = ["became aware of", "sensed", "saw", "approached",
        "felt the presence of", "found", "came across", "heard",
        "encountered", "happened upon", "smelled", "perceived"]
    adverbs = ["suddenly", "all at once", "gradually", "soon", "later", "then",
            "nearby", "in the distance", "meanwhile", "once in a while",
            "over and over", "again", "somewhere", "finally", "intermittently"]
    qualified = [x for x in sdb if x['nsubj'] is not None]
    while True:
        c = random.choice(qualified)
        try:
            np = indefify(c['nsubj'])
            break
        except IndexError:
            continue
    intro = random.choice(verbs)
    state.topics.append(c['nsubj'])
    s = random.choice(["you", "I", "we"]) + " " + intro + " " + np
    if len(state.paragraphs) > 0 and len(state.topics) > 0 and \
            random.randrange(3) == 0:
        s = random.choice(adverbs) + " " + s
    if random.randrange(3) == 0:
        all_pps = reduce(
                list.__add__, [x['pps'] for x in sdb if len(x['pps']) > 0])
        s += " " + random.choice(all_pps).text
    return s

def elaborate_on_topic(sdb, state):
    if len(state.topics) > 0:
        prev = state.topics[-1]
    else:
        prev = None
    subj, d = random_sentence_for_nsubj(sdb, prev)
    if prev is not None and len(state.subj_orth) > 0 \
            and state.subj_orth[-1].lower() in ('it', 'they'):
        subj = "the " + prev.root.orth_
    state.subj_orth.append(subj)
    return replace_span(d['span'], d['nsubj'], subj)

def reminded(sdb, state):
    verbs = ['reminded me of', 'reminded you of', 'reminded us of',
            'recalled', 'brought to mind', 'evoked', 'suggested',
            'seemed like', 'resembled', 'had the quality of']
    adverbs = ['somehow', 'at the time', 'sometimes', 'at first',
            'maybe']
    if len(state.topics) > 0 and state.topics[-1] is not None and \
            nsubj_is_plural(state.topics[-1]):
        subj = 'they'
    else:
        subj = 'it'
    if len(state.subj_orth) > 0 \
            and state.subj_orth[-1].lower() in ('it', 'they') \
            and len(state.topics) > 0 \
            and state.topics[-1] is not None:
        subj = "the " + state.topics[-1].root.orth_
    state.subj_orth.append(subj)
    nps = [x['nsubj'] for x in sdb if x['nsubj'] is not None]
    s = subj + " " + random.choice(verbs) + " " + random.choice(nps).text
    if random.randrange(6) == 0:
        s = random.choice(adverbs) + " " + s
    return s

def motion(sdb, state):
    verbs = ["continue", "press on", "move on", "wander away",
            "float away", "ascend", "go up", "take flight", "leave",
            "descend", "go down", "proceed", "follow", "go around",
            "retreat"]
    modals = ["decided to", "resolved to", "agreed to", "elected to"]
    adverbs = ["reluctantly", "discreetly", "foolishly", "regretfully",
        "at last", "finally", "hastily"]
    s = ' '.join(["we", random.choice(modals), random.choice(verbs)])
    if random.randrange(3) == 0:
        s = random.choice(adverbs) + " " + s
    return s

def affection(sdb, state):
    return random.choice(["we embraced", "we smiled", "we held hands"])

def arrived(sdb, state):
    s = random.choice(["we were home", "we had come home",
        "we had arrived"])
    adverbs = ["finally", "at last"]
    if random.randrange(3) == 0:
        s = random.choice(adverbs) + " " + s
    return s


def end_para(sdb, state):
    raise EndParagraph

paragraph_model = {
    'start': [exposition, awareness],
    exposition: [exposition, exposition, exposition, elaborate_on_topic,
        elaborate_on_topic, reminded, reminded, awareness, end_para],
    elaborate_on_topic: [exposition, reminded, end_para],
    awareness: [elaborate_on_topic, elaborate_on_topic, elaborate_on_topic,
        reminded, reminded, exposition, end_para],
    reminded: [elaborate_on_topic, exposition, end_para],
    'end-chapter': [awareness, exposition, motion],
    motion: [exposition, exposition, awareness, awareness, end_para],
    'end-novel': [affection],
    affection: [arrived],
    arrived: [exposition, exposition, awareness, awareness, end_para]
}

class NovelState(object):
    def __init__(self, chapters=None, i=0, chapter_count=0):
        if chapters is None:
            self.chapters = []
        else:
            self.chapters = chapters
        self.current_date = datetime.date(
                random.randrange(1950, 2050),
                random.randrange(1, 13),
                random.randrange(1, 28))
        self.start_date = self.current_date
        self.chapter_count = chapter_count
        self.i = i

class ChapterState(object):
    def __init__(self, novel, i=0, paragraph_count=0, paragraphs=None):
        self.topics = []
        self.history = []
        self.subj_orth = []
        self.novel = novel
        self.paragraph_count = paragraph_count
        self.i = i
        if paragraphs is None:
            self.paragraphs = []
        else:
            self.paragraphs = paragraphs
    def __str__(self):
        return " ".join([str(x) for x in [self.topics, self.history, 
            self.subj_orth, self.paragraphs]])

class EndParagraph(Exception):
    pass

def chapter_heading(sdb):
    nps = [x['nsubj'].text for x in sdb if x['nsubj'] is not None \
            and len(x['nsubj'].text) < 30]
    headings = list(set(nps + chapter_heading_nouns))
    return random.choice(headings)

def chapter(sdb, state):
    "a chapter consists of a series of paragraphs."
    heading = normalize(chapter_heading(sdb))
    if random.randrange(3) == 0:
        dds = str(int(state.current_date.strftime("%d")))
        heading += ". " + state.current_date.strftime("%A, %B ") + dds
    if random.randrange(2) == 0:
        delta = state.current_date - state.start_date
        delta_dds = delta.days + 1
        heading += " (Day %d)" % delta_dds
    paragraphs = list()
    paragraph_count = random.choice([1,2,2,2,3,3,3,3,3,4,4,4,4,5,5,5,6,7,8])
    for i in range(paragraph_count):
        st = ChapterState(paragraphs=paragraphs, novel=state,
                paragraph_count=paragraph_count, i=i)
        new_p = paragraph(sdb, st)
        paragraphs.append(new_p)
    return heading, paragraphs

def paragraph(sdb, state):
    """a paragraph consists of a series of sentences. the nature of each
    sentence follows the "sentence model" for the novel"""
    sentences = list()
    while True:
        try:
            # special positional rules
            if len(state.history) == 0:
                if state.i == state.paragraph_count - 1:
                    if state.novel.i == state.novel.chapter_count - 1:
                        current = 'end-novel'
                    else:
                        current = 'end-chapter'
                else:
                    current = 'start'
            else:
                current = state.history[-1]
            pick = random.choice(paragraph_model[current])
            sentences.append((pick, pick(sdb, state)))
            state.history.append(pick)
        except EndParagraph:
            return sentences

def surface(chapter):
    "turn a chapter into surface text."
    title = chapter[0]
    paragraph_src = chapter[1]
    paragraphs = list()

    for para_i, para in enumerate(paragraph_src):
        sentences = list()
        i = 0
        while i < len(para):
            # randomly conjoin sentences when possible
            sentence = para[i][1]
            if i < len(para) - 1:
                next_s = para[i+1][1]
            # haxx: suppress conjunction behavior in final paragraph
            # (for novel-final affective sentences)
            if i < len(para)-1 and len(sentence) < 60 and len(next_s) < 60 and \
                    not(re.search(r"\b(and|but)\b", sentence+next_s)) and \
                    para_i != len(paragraph_src)-1 and \
                    random.randrange(2) == 0:
                if random.randrange(4) == 0:
                    conj = "; "
                else:
                    conj = " and "
                sentences.append(
                        punctuate(normalize(depunct(sentence)+conj+next_s)))
                i += 2
            else:
                sentences.append(punctuate(normalize(sentence)))
                i += 1
        paragraphs.append(sentences)

    return title, paragraphs

def novel(sdb, chapter_count=100):
    state = NovelState(chapter_count=chapter_count)
    chapters = list()
    for i in range(chapter_count):
        state.i = i
        chapters.append(chapter(sdb, state))
        state.current_date += datetime.timedelta(
                days=random.choice([1,1,1,1,2,2,3,4,5]))
    return chapters

def render_latex_template(fh, chapters):
    tmpl = fh.read().decode('utf8')
    tmpl_s = tmpl.replace("<<chapters>>",
            '\n'.join([to_latex(surface(ch)) for ch in chapters]))
    return tmpl_s

# from http://stackoverflow.com/a/25875504 ugh
def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless',
        '>': r'\textgreater',
    }
    regex = re.compile('|'.join(re.escape(unicode(key)) \
        for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

def to_latex(surfaced):
    doc = "\chapter{%s}\n\n" % surfaced[0]
    for para in surfaced[1]:
        doc += tex_escape(' '.join(para)) + "\n\n"
    return doc

def to_text(surfaced, *args, **kwargs):
    import textwrap
    doc = surfaced[0] + "\n\n"
    for para in surfaced[1]:
        doc += "\n".join(textwrap.wrap(' '.join(para))) + "\n\n"
    return doc

if __name__ == '__main__':
    import os, sys
    from spacy.en import English
    sys.stderr.write("initializing spacy...")
    nlp = English(data_dir=os.environ.get('SPACY_DATA'))
    sys.stderr.write("done.\n")
    sdb = sentence_db(nlp, open("nature_sentences.txt"))
    print render_latex_template(sys.stdin, novel(sdb, 10))

