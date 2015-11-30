import random, sys
sentences = [line.split("\t")[1].strip() for line in sys.stdin]
random.shuffle(sentences)

i = 0
while True:
    advance = i+random.randrange(1, 7)
    print " ".join(sentences[i:advance])
    print ""
    i = advance

