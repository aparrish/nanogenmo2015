#Our Arrival

By [Allison Parrish](http://www.decontextualize.com/)

This is the source code for my [NaNoGenMo
2015](https://github.com/dariusk/NaNoGenMo-2015/issues/25) project. It's
written in Python 2.7. It makes extensive use of [spaCy](http://spacy.io/) (for
parsing English sentences) and
[Pattern](http://www.clips.ua.ac.be/pages/pattern-en)'s WordNet module.

[Here's a PDF with output from this
procedure](http://s3.amazonaws.com/aparrish/our-arrival.pdf).

The source code is not in great shape. Apologies for that. :/

##Usage

The `gen.py` script can be run at the command-line to fill in the
`template.tex` file with chapters and paragraphs filled in.

    $ export SPACY_DATA=/path/to/your/spacy/data
    $ python gen.py 300 nature_sentences.txt <template.tex >output.tex

You can replace `300` with the number of chapters you want to generate. The
text output from the program is a LaTeX file that you can convert to PDF using
your regular LaTeX toolchain.

##Requirements

For Python dependencies, see `requirements.txt`.

I included the database of extracted sentences in the repository as
`nature_sentences.txt`. If you want to extract the sentences yourself, you'll
need to have the Project Gutenberg corpus on your computer.

I was working with the Project Gutenberg files from the April 2010 DVD ISO.
You can download it [here](http://www.gutenberg.org/wiki/Gutenberg:The_CD_and_DVD_Project); make sure it's mounted as `/Volumes/PGDVD_2010_04_RC2/`. For
metadata, I was using Leonard Richardson's
[47000_metadata.json](https://twitter.com/leonardr/status/667049187918356480)
(which the Python scripts expect to be available in the working directory).

##Files

A quick outline of what's in all of the files...

* `extract.py`: various functions for extracting/replacing grammatical
  consituents in English sentences using spaCy; also most of the WordNet
  shenanigans
* `extract_nature_sentences.py`: command-line script to extract "natural"
  sentences from the Project Gutenberg corpus
* `gen.py`: functions and classes for generating chapters, paragraphs and
  sentences from the nature sentences corpus (including the paragraph model)
* `gutenfetch.py`: functions for searching Gutenberg metadata and retrieving
  text from the mounted Project Gutenberg ISO image
* `nature_sentences.txt`: pre-extracted corpus of sentences having no
  references to humans and whose subjects are all natural objects/phenomena
* `test.py`: unit/integration tests for a lot of the spaCy functions
* `test_wordnet.py`: unit tests for WordNet functions

##License

Copyright (c) 2015 Allison Parrish

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

