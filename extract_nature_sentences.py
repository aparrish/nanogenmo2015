import re
import sys

import extract
import gutenfetch

def main(nlp):
    subjs = 'Western|Science fiction|Geology|Natural|Exploration|Discovery|Physical'
    book_ids = [r['gutenberg_id'] for r in \
            gutenfetch.search(
                lambda x: any([re.search(subjs, t['identifier'], re.I) for t \
                        in x['subjects']]))]
    for book_id in book_ids:
        sys.stderr.write("current book: " + str(book_id) + "\n")
        try:
            text = gutenfetch.get_iso_text(book_id)
            for sentence in extract.nature_sentences(nlp, text,
                    tense_check=extract.sentence_is_present):
                sys.stderr.write(sentence + "\n")
                print str(book_id) + "\t" + sentence
        except ValueError as e:
            sys.stderr.write(str(e) + "\n")
            continue

if __name__ == '__main__':
    import os
    from spacy.en import English
    sys.stderr.write("initializing spacy...\n")
    nlp = English(data_dir=os.environ.get('SPACY_DATA'))
    sys.stderr.write("done.\n")
    main(nlp)
