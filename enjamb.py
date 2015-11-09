import pronouncing as pr
import re

# horrible but maybe good enough
def estimate(s):
    return max(2, len([1 for c in s if c in 'aeiouy'])) - 1

def syllable_count(tok):
    count = 0
    match = re.search(r"(\w+)", tok)
    if match:
        phones = pr.phones_for_word(match.group())
        if len(phones) > 0:
            return len(pr.stresses(phones[0]))
        else:
            return estimate(tok)
    return 0

def syllable_buckets(tokens, syllables_per=10):
    syl_tuples = [(tok, syllable_count(tok)) for tok in tokens]
    syls = sum([t[1] for t in syl_tuples])
    if syls < syllables_per:
        bucket_count = 1
    else:
        bucket_count = syls / syllables_per
    syls_per_bucket = syls / bucket_count
    #print "syllable_buckets", syls, bucket_count
    current_bucket_syl_count = 0
    current_bucket = list() 
    buckets = list()
    for tok, syl_count in syl_tuples:
        if len(tok) == 0: continue
        #print tok, syl_count, current_bucket_syl_count, current_bucket
        if current_bucket_syl_count >= syls_per_bucket:
            buckets.append(current_bucket[:])
            current_bucket = list()
            current_bucket_syl_count = 0
        current_bucket.append(tok)
        current_bucket_syl_count += syl_count
    if len(current_bucket) > 0:
        buckets.append(current_bucket)
    # care for orphans
    if len(buckets) > 1 and len(buckets[-1]) == 1 and \
            syllable_count(buckets[-1][0]) == 1:
        buckets[-2].append(buckets[-1][0])
        buckets.pop(-1)
    return buckets 

def enjamb(tokens, per_stanza=11, per_line=5):
    line_stress_count = 0
    enjambed = list()
    stanzas = syllable_buckets(tokens, per_stanza)
    for stanza in stanzas:
        lines = syllable_buckets(stanza, per_line)
        enjambed.append(lines)
    return enjambed

def ucfirst(s):
    return s[0].upper() + s[1:]

def stanza_line_join(stanzas):
    return "\n\n".join(
        ["\n".join(
            [" ".join(line) for line in stanza]
        ) for stanza in stanzas]
    )

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

def as_poem(tokens, per_stanza=11, per_line=4):
    return ucfirst(stanza_line_join(enjamb(tokens, per_stanza=per_stanza,
        per_line=per_line)))


if __name__ == '__main__':
    print sum([syllable_count(x) for x in "plugh xyzzy foo bar baz".split()])
    print syllable_buckets("this indicates that in there will be agreement in the fire , and that bereavement cannot lift .".split())
    print as_poem(normalize("this indicates that in there will be agreement in the fire , and that bereavement cannot lift .").split())
    print ""
    print normalize("this ( is a test ) of a thing")
    print normalize("this ( is a test .")
    print normalize("this ) is a test .")
    print normalize("cheese 's")
    print normalize("this time ?")
    print normalize('" my god')
    print normalize("this is a test _ .")
    print normalize("They should be viewed in ` the")
    print normalize("this--is a test.")
