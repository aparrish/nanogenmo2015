import gutenfetch

import gzip
import sys

def main(nlp, dest="./serialized"):
    gutenfetch.load_data()
    for rec in gutenfetch.records[100:]:
        sys.stderr.write("current book: " + str(rec['gutenberg_id']) + "\n")
        try:
            text = gutenfetch.get_iso_text(rec['gutenberg_id'])
            doc = nlp(text)
            fh = gzip.open(dest + "/%05d.spacy.gz" % rec['gutenberg_id'], "wb")
            fh.write(str(doc.to_bytes()))
        except ValueError as e:
            sys.stderr.write(str(e) + "\n")
            continue
        except KeyError as e:
            sys.stderr.write(str(e) + "\n")
            continue

